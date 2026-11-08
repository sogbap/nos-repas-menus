#!/usr/bin/env python3
"""Relève le prix de toutes les fiches produits de picard.fr, pour l'app iOS « Nos repas ».

Usage : python3 releve_picard.py picard.json [--max N]

Le robot respecte robots.txt : il ne lit que les fiches /produits/ que le plan du site publie, jamais la recherche ni le panier. Il
s'annonce sous son vrai nom, lit une page à la fois avec une seconde et demie d'écart, et s'arrête au premier refus (403, 429, page
anti-robot) en gardant le relevé précédent : il ne cherche jamais à contourner un blocage.
"""
import datetime
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import urllib.robotparser

AGENT = "NosRepas-releve-prix/1.0 (+https://github.com/sogbap/nos-repas-menus)"
SITE = "https://www.picard.fr"
DELAY = 1.5


class Blocked(Exception):
    pass


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": AGENT, "Accept-Language": "fr-FR"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""


def text(fragment):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def number(s):
    return float(s.replace(" ", "").replace(" ", "").replace(",", "."))


def parse(page):
    """Le nom, le prix, le prix au kilo ou au litre, le format et le rayon d'une fiche ; None si la page n'a pas de prix."""
    price = re.search(r'itemprop="price" content="([\d.]+)"', page)
    title = re.search(r"<h1[^>]*>(.*?)</h1>", page, re.S)
    if not price or not title:
        return None
    out = {"nom": text(title.group(1)), "prix": float(price.group(1))}
    unit = re.search(r'class="pi-ProductDetails-kiloPrice"[^>]*>(.*?)</div>', page, re.S)
    if unit:
        m = re.search(r"([\d\s ]+,\d+)\s*€\s*/\s*(kg|l|L)", text(unit.group(1)))
        if m:
            out["kilo"] = number(m.group(1))
            out["par"] = m.group(2).lower()
    weight = re.search(r'class="pi-ProductDetails-weight"[^>]*>(.*?)</(?:span|div|p)>', page, re.S)
    if weight and text(weight.group(1)):
        out["format"] = text(weight.group(1))
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S):
        try:
            data = json.loads(block)
        except ValueError:
            continue
        if data.get("@type") == "BreadcrumbList":
            names = [i.get("name") for i in data.get("itemListElement", [])]
            out["rayon"] = " › ".join(n for n in names[2:-1] if n)
    return out


def product_urls(robots):
    status, page = fetch(SITE + "/sitemap_0.xml")
    if status != 200:
        raise Blocked(f"plan du site : {status}")
    urls = sorted(set(re.findall(r"<loc>([^<]*/produits/[^<]*)</loc>", page)))
    return [u for u in urls if robots.can_fetch(AGENT, u)]


def main(out, limit=None):
    robots = urllib.robotparser.RobotFileParser(SITE + "/robots.txt")
    robots.read()
    urls = product_urls(robots)[:limit]
    products, skipped = {}, 0
    try:
        for n, url in enumerate(urls):
            if n:
                time.sleep(DELAY)
            status, page = fetch(url)
            if status in (403, 429) or (status == 200 and re.search(r"datadome|cf-chl|captcha-delivery", page, re.I)):
                raise Blocked(f"{status} sur {url}")
            info = parse(page) if status == 200 else None
            code = re.search(r"(\d{12,})\.html", url)
            if info and code:
                products[code.group(1)] = {**info, "url": url}
            else:
                skipped += 1
    except Blocked as b:
        sys.exit(f"Relevé arrêté, picard.fr refuse le robot ({b}) : le relevé précédent est gardé.")
    if len(products) < max(1, len(urls) // 2):
        sys.exit(f"Relevé incomplet ({len(products)} prix sur {len(urls)} fiches) : le relevé précédent est gardé.")
    # Rangés par code produit : il ne change pas quand Picard renomme une fiche.
    doc = {"releve": datetime.date.today().isoformat(), "source": "picard.fr", "produits": dict(sorted(products.items()))}
    tmp = out + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=0, sort_keys=True)
    os.replace(tmp, out)
    print(f"{len(products)} prix relevés sur {len(urls)} fiches ({skipped} sans prix).")


if __name__ == "__main__":
    args = sys.argv[1:]
    limit = None
    if "--max" in args:
        i = args.index("--max")
        limit = int(args[i + 1])
        del args[i:i + 2]
    if len(args) != 1:
        sys.exit(__doc__)
    main(args[0], limit)
