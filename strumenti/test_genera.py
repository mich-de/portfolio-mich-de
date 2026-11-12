"""Controlli sulle pagine generate: niente script, niente stili inline, feed valido."""

import datetime
import re
import unittest
import xml.etree.ElementTree as ET

import genera
import media
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
    yield "post-vecchio", genera.pagina_post(VECCHIO, POST, None, NOTE)
    yield "tag", genera.pagina_indice([POST], NOTE, tag="retro")
    yield "tag-indice", genera.pagina_tag_indice(NOTE)
    yield "tag-indice-vuoto", genera.pagina_tag_indice([])


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
        self.assertEqual(len(mappa), 6)   # home it/en, diario, 2 post, 1 tag

    def test_bozze_fuori_da_sitemap(self):
        bozza = nota.leggi("2026-11-13-b.nota",
                           "titolo: B\ndata: 2026-11-13\ntipo: pensiero\nbozza: si\n---\nx")
        self.assertNotIn("2026-11-13-b", genera.sitemap([bozza]))
        self.assertIn('content="noindex"', genera.pagina_post(bozza, None, None))


    def test_copertina_e_feed_con_indirizzi_completi(self):
        genera.MEDIA["cop.jpg"] = media.Media("cop.jpg", "immagine", "jpeg", 640, 480, b"")
        info = {"cop.jpg": ("immagine", 640, 480)}
        n = nota.leggi("2026-11-12-con-foto.nota",
                       "titolo: Foto\ndata: 2026-11-12\ntipo: passato\ncopertina: cop.jpg\n---\n"
                       "![una foto](cop.jpg)\n[su](#s-sotto) [home](/)\n# Sotto", info)
        html = genera.pagina_post(n, None, None)
        self.assertIn(f'<meta property="og:image" content="{genera.SITE}/diario/media/cop.jpg">', html)
        self.assertIn('<meta property="og:image:width" content="640">', html)
        self.assertIn('class="nota-copertina"', html)
        voce = genera.feed([n])
        self.assertIn(f"src=&quot;{genera.SITE}/diario/media/cop.jpg&quot;", voce)
        self.assertIn(f"href=&quot;{genera.SITE}/diario/2026-11-12-con-foto/#s-sotto&quot;", voce)
        self.assertNotIn("href=&quot;/", voce)
        ET.fromstring(voce)


    def test_ordine_dal_piu_nuovo(self):
        def post(nome, ora=""):
            testa = f"titolo: {nome}\ndata: 2026-11-12\n" + (f"ora: {ora}\n" if ora else "")
            return nota.leggi(f"2026-11-12-{nome}.nota", testa + "tipo: cronaca\n---\nx")
        mattina, sera, senza = post("zeta", "09:15"), post("alfa", "21:42"), post("beta")
        ieri = nota.leggi("2026-11-11-ieri.nota", "titolo: I\ndata: 2026-11-11\nora: 23:59\ntipo: cronaca\n---\nx")
        self.assertEqual([n.slug[11:] for n in genera.ordina([ieri, mattina, senza, sera])],
                         ["alfa", "zeta", "beta", "ieri"])
        self.assertEqual(genera.istante(sera), "2026-11-12T21:42:00+01:00")
        self.assertEqual(genera.fuso_roma(datetime.date(2026, 7, 1)), "+02:00")
        self.assertEqual(genera.fuso_roma(datetime.date(2026, 10, 25)), "+01:00")
        self.assertEqual(genera.fuso_roma(datetime.date(2026, 3, 29)), "+02:00")
        with self.assertRaises(nota.ErroreNota):
            nota.leggi("2026-11-12-x.nota", "titolo: X\ndata: 2026-11-12\nora: 25:00\ntipo: cronaca\n---\nx")


    def test_tag_cliccabili_e_correlati(self):
        def post(nome, tag, giorno="12"):
            return nota.leggi(f"2026-11-{giorno}-{nome}.nota",
                              f"titolo: {nome}\ndata: 2026-11-{giorno}\ntipo: cronaca\ntag: {tag}\n---\nx")
        a, b, c, d = post("a", "ai, reti"), post("b", "ai, reti", "10"), post("c", "ai", "11"), post("d", "vino")
        tutte = [a, b, c, d]
        self.assertEqual(genera.conta_tag(tutte), [("ai", 3), ("reti", 2), ("vino", 1)])
        self.assertEqual([x.slug for x in genera.correlati(a, tutte)], ["2026-11-10-b", "2026-11-11-c"])
        html = genera.pagina_post(a, None, None, tutte)
        self.assertIn('href="/diario/tag/ai/">#ai <span class="tag-conta">3</span>', html)
        self.assertIn('git tag --contains', html)
        self.assertIn('href="/diario/2026-11-10-b/"', html)
        self.assertNotIn('href="/diario/2026-11-12-d/"', html)
        indice = genera.pagina_indice([a, b, c], tutte, tag="ai")
        self.assertIn('<a href="/diario/tag/ai/" aria-current="page">', indice)
        self.assertIn("git log --grep=&quot;#ai&quot;", indice)


if __name__ == "__main__":
    unittest.main()
