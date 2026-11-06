#!/usr/bin/env python3
"""Tests de publish.py : python3 test_publish.py"""
import contextlib
import io
import json
import os
import tempfile
import unittest

import publish


def dish(key, week, **extra):
    return {"id": key, "type": "plat", "nom": "Plat " + key, "semaine": week, "statut": "choisi", "jour": "2026-11-10",
            "couverts": {"note": "invités"}, "notes": {"b": 1, "c": -1}, "ingredients": [{"n": "Oignon"}, {"n": "Curcuma"}],
            "etapes": [{"t": "Cuire"}], **extra}


class PublishTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, path, doc):
        full = os.path.join(self.root, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False)

    def week(self, week, count=5, **extra):
        self.write("config/etat.json", {"semaine": week, "theme": None, "defi": None, "taches": {"secret": 1}})
        for i in range(count):
            key = f"{week[-2:]}-{i}"
            self.write(f"recettes/{key}.json", dish(key, week, **extra))

    def refused(self, previous=None):
        with self.assertRaises(SystemExit) as caught, contextlib.redirect_stderr(io.StringIO()):
            publish.build(self.root, previous or {})
        return str(caught.exception)

    def test_rien_sur_le_foyer_ne_sort(self):
        self.week("2026-W46")
        out = json.loads(publish.build(self.root, {})[0])
        r = out["recettes"]["46-0"]
        for field in ("jour", "couverts", "achete", "fait", "choisiLe"):
            self.assertNotIn(field, r)
        self.assertEqual(r["notes"], {"b": 0, "c": 0})
        self.assertEqual(r["statut"], "propose")
        self.assertEqual(sorted(out["config"]["etat"]), ["defi", "semaine", "theme"])

    def test_les_nouveautes_s_ajoutent_a_ce_qui_est_publie(self):
        self.week("2026-W46")
        previous = json.loads(publish.build(self.root, {})[0])
        for name in os.listdir(os.path.join(self.root, "recettes")):
            os.remove(os.path.join(self.root, "recettes", name))
        self.week("2026-W47")
        out = json.loads(publish.build(self.root, previous)[0])
        self.assertEqual(out["recettes"]["46-0"]["statut"], "archive")
        self.assertEqual(out["recettes"]["47-0"]["statut"], "propose")
        self.assertEqual(out["config"]["etat"]["semaine"], "2026-W47")

    def test_les_plats_de_plus_de_8_semaines_sortent(self):
        self.week("2026-W50")
        previous = {"recettes": {"old": dish("old", "2026-W42"), "kept": dish("kept", "2026-W43")}}
        out = json.loads(publish.build(self.root, previous)[0])
        self.assertNotIn("old", out["recettes"])
        self.assertIn("kept", out["recettes"])

    def test_un_document_lu_avec_son_enveloppe_est_accepte(self):
        self.week("2026-W46")
        self.write("recettes/enveloppe.json", {"id": "enveloppe", "data": dish("enveloppe", "2026-W46"), "version": 1})
        out = json.loads(publish.build(self.root, {})[0])
        self.assertEqual(out["recettes"]["enveloppe"]["nom"], "Plat enveloppe")

    def test_un_nom_bloque_la_publication(self):
        self.week("2026-W46", accroche="Le plat préféré de Raphaëlle")
        self.assertIn("donnée personnelle", self.refused())

    def test_trop_peu_de_plats_bloque_la_publication(self):
        self.week("2026-W46", count=4)
        self.assertIn("4 plats seulement", self.refused())

    def test_une_recette_incomplete_bloque_la_publication(self):
        self.week("2026-W46", etapes=[])
        self.assertIn("incomplète", self.refused())

    def test_une_semaine_plus_ancienne_bloque_la_publication(self):
        self.week("2026-W46")
        self.assertIn("plus ancienne", self.refused({"config": {"etat": {"semaine": "2026-W47"}}}))

    def test_un_fichier_mal_recopie_bloque_la_publication(self):
        self.week("2026-W46")
        with open(os.path.join(self.root, "recettes", "46-0.json"), "w", encoding="utf-8") as f:
            f.write('{"nom": "tronqué"')
        self.assertIn("pas du JSON valide", self.refused())

    def test_un_prix_saisi_a_la_main_ne_remonte_pas(self):
        self.week("2026-W46")
        self.write("produits/p-a.json", {"nom": "A", "prix": {"v": 1, "src": "Votre prix"}})
        self.write("produits/p-b.json", {"nom": "B", "prix": {"v": 2, "src": "Estimation"}})
        out = json.loads(publish.build(self.root, {})[0])
        self.assertNotIn("prix", out["produits"]["p-a"])
        self.assertEqual(out["produits"]["p-b"]["prix"]["v"], 2)

    def test_ingredients_sans_fiche(self):
        self.week("2026-W46")
        self.assertEqual(publish.missing_products(self.root, {"produits": {"p": {"nom": "Oignon"}}}), ["Curcuma"])




class CheckSteps(unittest.TestCase):
    def good(self):
        return {
            "id": "w46-01", "type": "plat", "nom": "Plat", "etapesVersion": 1, "ustensiles": ["Poêle"],
            "ingredients": [{"n": "Riz basmati", "q": 60, "u": "g"}, {"n": "Huile d'olive", "q": 5, "u": "g"}],
            "etapes": [
                {"n": f"Étape {k}", "t": "Faites ceci.", "r": "chef"} for k in range(1, 4)
            ] + [
                {"n": "Riz", "t": "Lancez le riz.", "r": "commis", "m": 12, "p": "L'eau est absorbée.",
                 "i": ["Riz basmati", "Eau=2*Riz basmati", "Huile d'olive|0.5"], "g": ["riz"]},
                {"n": "Finir", "t": "Ajoutez le reste de l'huile.", "r": "ensemble", "i": ["Huile d'olive|0.5"]},
            ],
        }

    def check(self, recipe):
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.join(root, "recettes"))
            with open(os.path.join(root, "recettes", "w46-01.json"), "w", encoding="utf-8") as f:
                json.dump(recipe, f)
            return publish.check_steps(root)

    def test_une_recette_conforme_passe(self):
        self.assertEqual(self.check(self.good()), [])

    def test_le_vocabulaire_de_cuisinier_est_signale(self):
        r = self.good()
        r["etapes"][0]["t"] = "Émincez l'oignon et réservez."
        self.assertTrue(any("mot de cuisinier" in p for p in self.check(r)))

    def test_un_ingredient_oublie_est_signale(self):
        r = self.good()
        r["ingredients"].append({"n": "Persil plat", "q": 3, "u": "g"})
        self.assertTrue(any("Persil plat" in p for p in self.check(r)))

    def test_des_parts_qui_ne_font_pas_un_sont_signalees(self):
        r = self.good()
        r["etapes"][-1]["i"] = ["Huile d'olive"]
        self.assertTrue(any("les parts font" in p for p in self.check(r)))

    def test_un_ingredient_inconnu_est_signale(self):
        r = self.good()
        r["etapes"][-1]["i"] = ["Huile d'olive|0.5", "Eau=2*Riz"]
        self.assertTrue(any("Riz" in p and "pas un ingrédient" in p for p in self.check(r)))

    def test_un_minuteur_sans_repere_est_signale(self):
        r = self.good()
        del r["etapes"][3]["p"]
        self.assertTrue(any("sans repère" in p for p in self.check(r)))

    def test_des_etapes_non_reecrites_sont_signalees(self):
        r = self.good()
        del r["etapesVersion"], r["ustensiles"]
        problems = self.check(r)
        self.assertTrue(any("etapesVersion" in p for p in problems) and any("ustensiles" in p for p in problems))


if __name__ == "__main__":
    unittest.main(verbosity=0)
