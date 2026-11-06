#!/usr/bin/env python3
"""Met à jour menus.json, le fichier que l'app iOS « Nos repas » lit toute seule, avec les nouveautés de la semaine.

Usage : python3 publish.py <dossier d'export> <menus.json>
        python3 publish.py --manquants <dossier d'export> <menus.json>   liste les ingrédients sans fiche produit connue

Le dossier d'export contient config/etat.json et, un fichier JSON par document, recettes/ et produits/ (les nouveautés suffisent : ce
qui est déjà dans menus.json reste). Ce dépôt est public : seuls les recettes et les prix estimés en sortent, sans rien de ce qui
concerne le foyer (couverts, notes, soirs prévus, réglages, poids, commandes, placard, bilans). Le script refuse de publier s'il
trouve un nom, un plat incomplet, ou une semaine plus ancienne que celle déjà publiée.
"""
import datetime
import json
import os
import re
import sys

# Un iPhone resté sans ouvrir l'app rattrape jusqu'à 8 semaines de plats.
WEEKS_KEPT = 8
MIN_DISHES = 5
HOUSEHOLD_FIELDS = ("achete", "choisiLe", "couverts", "fait", "jour")
PERSONAL = re.compile(r"Baptiste|Rapha[eë]lle|Simonneau|Soul[eé]\b|Dammarie|@[a-z0-9-]+\.[a-z]", re.I)
WEEK = re.compile(r"^(\d{4})-W(\d{2})$")


def fail(message):
    sys.exit("Publication refusée : " + message)


def unwrap(doc):
    """Un document tel que le rend ArtifactData : {"id": …, "data": {…}}."""
    if isinstance(doc.get("data"), dict) and set(doc) <= {"id", "data", "version"}:
        return doc["data"]
    return doc


def load(root, collection):
    folder = os.path.join(root, collection)
    docs = {}
    if os.path.isdir(folder):
        for name in sorted(os.listdir(folder)):
            if name.endswith(".json"):
                try:
                    with open(os.path.join(folder, name), encoding="utf-8") as f:
                        docs[name[:-5]] = unwrap(json.load(f))
                except ValueError as error:
                    fail(f"{collection}/{name} n'est pas du JSON valide ({error}).")
    return docs


def monday(week):
    match = WEEK.match(week or "")
    if not match:
        fail("semaine illisible (" + repr(week) + ").")
    return datetime.date.fromisocalendar(int(match[1]), int(match[2]), 1)


def recipe(doc):
    r = {k: v for k, v in doc.items() if k not in HOUSEHOLD_FIELDS}
    r["notes"] = {"b": 0, "c": 0}
    r["photos"] = []
    r["fois"] = 0
    r["cumul"] = 0
    return r


def product(doc):
    p = dict(doc)
    # Un prix saisi à la main sur la page : l'iPhone garde le sien, souvent plus récent.
    if str((p.get("prix") or {}).get("src", "")).startswith("Votre prix"):
        p.pop("prix")
    return p


def build(root, previous):
    state = load(root, "config").get("etat")
    if not state:
        fail("config/etat.json manque dans l'export.")
    week = state.get("semaine")
    start = monday(week)
    known = (previous.get("config", {}).get("etat") or {}).get("semaine")
    if known and monday(known) > start:
        fail(f"{week} est plus ancienne que la semaine déjà publiée ({known}).")

    recipes = dict(previous.get("recettes", {}))
    recipes.update({k: recipe(v) for k, v in load(root, "recettes").items()})
    products = dict(previous.get("produits", {}))
    products.update({k: product(v) for k, v in load(root, "produits").items()})

    oldest = start - datetime.timedelta(weeks=WEEKS_KEPT - 1)
    kept = {}
    for key, r in recipes.items():
        dish = r.get("type") == "plat"
        if dish and not (WEEK.match(r.get("semaine") or "") and oldest <= monday(r["semaine"]) <= start):
            continue
        kept[key] = {**r, "statut": "archive" if dish and r.get("semaine") != week else "propose"}

    dishes = [r for r in kept.values() if r.get("type") == "plat" and r.get("semaine") == week]
    if len(dishes) < MIN_DISHES:
        fail(f"{len(dishes)} plats seulement pour {week}.")
    for r in kept.values():
        if not r.get("nom") or not r.get("ingredients") or not r.get("etapes"):
            fail("recette incomplète : " + str(r.get("id")) + ".")
    out = {
        "config": {"etat": {k: state.get(k) for k in ("semaine", "theme", "defi")}},
        "produits": products,
        "recettes": kept,
    }
    text = json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    found = PERSONAL.search(text)
    if found:
        fail("donnée personnelle dans le fichier : « " + text[max(0, found.start() - 40):found.end() + 40].replace("\n", " ") + " ».")
    return text, week, len(dishes), len(kept), len(products)


def missing_products(root, previous):
    """Les ingrédients des nouvelles recettes qui n'ont pas encore de fiche (les épices en cuillères n'en ont pas toutes)."""
    known = {p.get("nom") for p in previous.get("produits", {}).values()}
    known |= {p.get("nom") for p in load(root, "produits").values()}
    names = set()
    for r in load(root, "recettes").values():
        for i in (r.get("ingredients") or []) + ((r.get("midi") or {}).get("extras") or []):
            names.add(i.get("n"))
    return sorted(n for n in names - known if n)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--manquants"]
    if len(args) != 2:
        sys.exit(__doc__)
    previous = {}
    if os.path.exists(args[1]):
        with open(args[1], encoding="utf-8") as f:
            previous = json.load(f)
    if "--manquants" in sys.argv:
        print(json.dumps(missing_products(args[0], previous), ensure_ascii=False))
        sys.exit(0)
    text, week, dishes, recipes, products = build(args[0], previous)
    with open(args[1], "w", encoding="utf-8") as f:
        f.write(text)
    print(f"{week} : {dishes} plats de la semaine, {recipes} recettes, {products} produits, {len(text.encode()) // 1024} Ko")
