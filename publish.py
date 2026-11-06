#!/usr/bin/env python3
"""Construit menus.json, le fichier que l'app iOS « Nos repas » lit toute seule, à partir d'un export de la base de l'artéfact.

Usage : python3 publish.py <dossier d'export> <menus.json>

Le dossier d'export contient recettes/, produits/ et config/, un fichier JSON par document, tel que l'écrit l'outil ArtifactData
avec out_dir. Ce dépôt est public : seuls les recettes et les prix estimés en sortent, sans rien de ce qui concerne le foyer
(couverts, notes, soirs prévus, réglages, poids, commandes, placard, bilans). Le script refuse de publier s'il trouve un nom.
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


def load(root, collection):
    folder = os.path.join(root, collection)
    if not os.path.isdir(folder):
        fail("le dossier " + collection + "/ manque dans l'export.")
    docs = {}
    for name in sorted(os.listdir(folder)):
        if name.endswith(".json"):
            with open(os.path.join(folder, name), encoding="utf-8") as f:
                docs[name[:-5]] = json.load(f)
    return docs


def monday(week):
    match = WEEK.match(week or "")
    if not match:
        fail("semaine illisible (" + repr(week) + ").")
    return datetime.date.fromisocalendar(int(match[1]), int(match[2]), 1)


def recipe(doc, week):
    r = {k: v for k, v in doc.items() if k not in HOUSEHOLD_FIELDS}
    dish = r.get("type") == "plat"
    r["statut"] = "archive" if dish and r.get("semaine") != week else "propose"
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


def build(root):
    state = load(root, "config").get("etat") or {}
    week = state.get("semaine")
    start = monday(week)
    oldest = start - datetime.timedelta(weeks=WEEKS_KEPT - 1)
    recipes = {}
    for key, doc in load(root, "recettes").items():
        if doc.get("type") == "plat":
            if not WEEK.match(doc.get("semaine") or "") or not oldest <= monday(doc["semaine"]) <= start:
                continue
        recipes[key] = recipe(doc, week)
    dishes = [r for r in recipes.values() if r.get("type") == "plat" and r.get("semaine") == week]
    if len(dishes) < MIN_DISHES:
        fail(f"{len(dishes)} plats seulement pour {week}.")
    for r in dishes:
        if not r.get("nom") or not r.get("ingredients") or not r.get("etapes"):
            fail("plat incomplet : " + str(r.get("id")) + ".")
    out = {
        "config": {"etat": {k: state.get(k) for k in ("semaine", "theme", "defi", "historique")}},
        "produits": {k: product(v) for k, v in load(root, "produits").items()},
        "recettes": recipes,
    }
    text = json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    found = PERSONAL.search(text)
    if found:
        fail("donnée personnelle dans le fichier : « " + text[max(0, found.start() - 40):found.end() + 40].replace("\n", " ") + " ».")
    return text, week, len(dishes), len(recipes), len(out["produits"])


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    text, week, dishes, recipes, products = build(sys.argv[1])
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write(text)
    print(f"{week} : {dishes} plats de la semaine, {recipes} recettes, {products} produits, {len(text.encode()) // 1024} Ko")
