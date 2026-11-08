#!/usr/bin/env python3
"""Tests de releve_picard.py : python3 test_releve_picard.py (sans réseau)."""
import unittest

import releve_picard

PAGE = """<html><h1 class="pi-ProductDetails-title">Ail coup&eacute;</h1>
<div class="pi-ProductDetails-price"><meta itemprop="price" content="5.5" /> </div>
<div class="pi-ProductDetails-kiloPrice"> <span class="sr-only">Prix au kilo</span> 22,00 &#8364;/kg</div>
<span class="pi-ProductDetails-weight">le sachet de 250 g</span>
<script type="application/ld+json">{"@type": "BreadcrumbList", "itemListElement": [{"name": "Accueil"}, {"name": "Rayons"},
{"name": "Légumes et fruits"}, {"name": "Légumes"}, {"name": "Ail coupé"}]}</script></html>"""


class Parse(unittest.TestCase):
    def test_une_fiche_complete(self):
        self.assertEqual(releve_picard.parse(PAGE), {"nom": "Ail coupé", "prix": 5.5, "kilo": 22.0, "par": "kg",
                                                     "format": "le sachet de 250 g", "rayon": "Légumes et fruits › Légumes"})

    def test_le_prix_au_litre(self):
        page = PAGE.replace("22,00 &#8364;/kg", "3,98 &#8364;/L")
        self.assertEqual((releve_picard.parse(page)["kilo"], releve_picard.parse(page)["par"]), (3.98, "l"))

    def test_une_page_sans_prix_est_ignoree(self):
        self.assertIsNone(releve_picard.parse("<html><h1>Produit épuisé</h1></html>"))


if __name__ == "__main__":
    unittest.main(verbosity=0)
