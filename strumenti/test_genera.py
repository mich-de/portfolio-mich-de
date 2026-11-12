"""Controlli sulle pagine generate: niente script, niente stili inline, feed valido."""

import re
import unittest
import xml.etree.ElementTree as ET

import genera
import nota

POST = nota.leggi("2026-11-12-prova.nota",
                  "titolo: Prova <b>&\ndata: 2026-11-12\ntipo: passato\ntag: retro\n---\n"
                  "# Titolo\nTesto con *grassetto* e [link](https://esempio.it/?a=1&b=2).")
VECCHIO = nota.leggi("2026-11-01-vecchio.nota",
                     "titolo: Vecchio\ndata: 2026-11-01\ntipo: cronaca\n---\nCiao.")
NOTE = [POST, VECCHIO]


def tutte_le_pagine():
    yield "home", genera.pagina(genera.TESTI["it"], NOTE)
    yield "home-en", genera.pagina(genera.TESTI["en"], NOTE)
    yield "home-vuota", genera.pagina(genera.TESTI["it"], [])
    yield "404", genera.pagina_404()
    yield "indice", genera.pagina_indice(NOTE, NOTE)
    yield "indice-vuoto", genera.pagina_indice([], [])
    for tipo, (ramo, _) in genera.RAMI.items():
        yield ramo, genera.pagina_indice([n for n in NOTE if n.tipo == tipo], NOTE, ramo)
    yield "post", genera.pagina_post(POST, None, VECCHIO)
    yield "post-vecchio", genera.pagina_post(VECCHIO, POST, None)


class Pagine(unittest.TestCase):
    def test_niente_script_ne_stili_inline(self):
        for nome, html in tutte_le_pagine():
            with self.subTest(pagina=nome):
                self.assertNotRegex(html, r"(?i)<script")
                self.assertNotRegex(html, r"(?i)<style")
                self.assertNotRegex(html, r"(?i)\sstyle=")
                self.assertNotRegex(html, r"(?i)\son[a-z]+=")
                self.assertNotRegex(html, r"(?i)javascript:")

    def test_titolo_escapato(self):
        html = genera.pagina_post(POST, None, None)
        self.assertIn("Prova &lt;b&gt;&amp;", html)
        self.assertNotIn("<b>&", html)

    def test_link_interni(self):
        html = genera.pagina_indice(NOTE, NOTE)
        self.assertIn('href="/diario/2026-11-12-prova/"', html)
        self.assertIn('href="/diario/passato/"', html)

    def test_feed_e_sitemap_xml_validi(self):
        radice = ET.fromstring(genera.feed(NOTE))
        voci = radice.findall("{http://www.w3.org/2005/Atom}entry")
        self.assertEqual(len(voci), 2)
        ET.fromstring(genera.feed([]))
        mappa = ET.fromstring(genera.sitemap(NOTE))
        self.assertEqual(len(mappa), 5)

    def test_bozze_fuori_da_sitemap(self):
        bozza = nota.leggi("2026-11-13-b.nota",
                           "titolo: B\ndata: 2026-11-13\ntipo: pensiero\nbozza: si\n---\nx")
        self.assertNotIn("2026-11-13-b", genera.sitemap([bozza]))
        self.assertIn('content="noindex"', genera.pagina_post(bozza, None, None))


if __name__ == "__main__":
    unittest.main()
