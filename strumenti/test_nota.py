"""Test del linguaggio Nota. Si lanciano con:  python3 -m unittest discover -s strumenti"""

import random
import string
import unittest
from html.parser import HTMLParser

import nota

TESTA = "titolo: Prova\ndata: 2026-11-12\ntipo: pensiero\n---\n"
FILE = "2026-11-12-prova.nota"


def corpo(testo: str) -> str:
    return nota.leggi(FILE, TESTA + testo).html


class Controllore(HTMLParser):
    """Verifica che l'HTML prodotto usi solo tag e attributi ammessi."""

    ATTRIBUTI = {"a": {"href", "rel", "target"}, "h2": {"id"}, "h3": {"id"},
                 "span": {"class"}}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.problemi = []

    def handle_starttag(self, tag, attrs):
        if tag not in nota.TAG_AMMESSI:
            self.problemi.append(f"tag {tag}")
        for nome, valore in attrs:
            if nome not in self.ATTRIBUTI.get(tag, set()):
                self.problemi.append(f"attributo {nome} su {tag}")
            if nome == "href" and not (valore or "").startswith("https://"):
                self.problemi.append(f"href {valore}")
            if nome == "rel" and valore != "noopener noreferrer external":
                self.problemi.append("rel")
            if nome == "class" and valore != "nota-lingua":
                self.problemi.append("class")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_comment(self, data):
        self.problemi.append("commento")

    def handle_decl(self, decl):
        self.problemi.append("dichiarazione")

    def handle_pi(self, data):
        self.problemi.append("istruzione")


def sicuro(html_prodotto: str) -> list:
    c = Controllore()
    c.feed(html_prodotto)
    c.close()
    return c.problemi


class Intestazione(unittest.TestCase):
    def test_minima(self):
        n = nota.leggi(FILE, TESTA + "Ciao.")
        self.assertEqual(n.titolo, "Prova")
        self.assertEqual(n.tipo, "pensiero")
        self.assertEqual(n.slug, "2026-11-12-prova")
        self.assertFalse(n.bozza)
        self.assertEqual(n.sommario, "Ciao.")
        self.assertEqual(len(n.hash), 40)

    def test_completa(self):
        n = nota.leggi(FILE, "titolo: T\ndata: 2026-11-12\ntipo: passato\n"
                             "tag: retro, reti-locali\nsommario: S\nbozza: si\n---\nx")
        self.assertEqual(n.tag, ("retro", "reti-locali"))
        self.assertTrue(n.bozza)
        self.assertEqual(n.sommario, "S")

    def errore(self, testo, riga, parola, file=FILE):
        with self.assertRaises(nota.ErroreNota) as ctx:
            nota.leggi(file, testo)
        self.assertEqual(ctx.exception.riga, riga, str(ctx.exception))
        self.assertIn(parola, ctx.exception.messaggio)

    def test_errori(self):
        self.errore("titolo: T\ndata: 2026-11-12\n---\nx", 1, "tipo")
        self.errore("titolo: T\ndata: 2026-13-12\ntipo: pensiero\n---\nx", 2, "data")
        self.errore("titolo: T\ndata: 2026-11-11\ntipo: pensiero\n---\nx", 2, "coincide")
        self.errore("titolo: T\ndata: 2026-11-12\ntipo: poesia\n---\nx", 3, "tipo")
        self.errore("titolo: T\ncolore: rosso\n---\nx", 2, "sconosciuta")
        self.errore("titolo: T\ntitolo: U\n---\nx", 2, "ripetuta")
        self.errore("titolo: T\ndata: 2026-11-12\ntipo: pensiero\nx", 4, "---")
        self.errore("titolo T\n---\nx", 1, "chiave: valore")
        self.errore(TESTA, 5, "testo")
        self.errore("titolo: T\ndata: 2026-11-12\ntipo: pensiero\ntag: Ciao Mondo\n---\nx", 4, "tag")
        self.errore("titolo: T\ndata: 2026-11-12\ntipo: pensiero\nbozza: forse\n---\nx", 4, "bozza")
        self.errore(TESTA + "x", 1, "nome file", file="ciao.nota")
        self.errore(TESTA + "x", 1, "nome file", file="2026-11-12-Ciao.nota")

    def test_caratteri_invisibili(self):
        self.errore(TESTA + "ciao\u202eolleh", 5, "invisibile")
        self.errore(TESTA + "a\x00b", 5, "invisibile")

    def test_riga_lunga(self):
        self.errore(TESTA + "a" * (nota.MAX_RIGA + 1), 5, "lunga")


class Blocchi(unittest.TestCase):
    def test_paragrafi(self):
        self.assertEqual(corpo("uno\ndue\n\ntre"), "<p>uno due</p>\n<p>tre</p>")

    def test_a_capo(self):
        self.assertEqual(corpo("uno\\\ndue"), "<p>uno<br>due</p>")

    def test_titoli(self):
        self.assertEqual(corpo("# Ciao mondo\n## Più giù"),
                         '<h2 id="s-ciao-mondo">Ciao mondo</h2>\n<h3 id="s-piu-giu">Più giù</h3>')
        self.assertIn('id="s-a-2"', corpo("# A\n# A"))
        with self.assertRaises(nota.ErroreNota):
            corpo("### troppo")

    def test_elenco_citazione_linea(self):
        self.assertEqual(corpo("- a\n- *b*"), "<ul><li>a</li><li><strong>b</strong></li></ul>")
        self.assertEqual(corpo("> uno\n>\n> due"),
                         "<blockquote><p>uno</p><p>due</p></blockquote>")
        self.assertEqual(corpo("a\n\n---\n\nb"), "<p>a</p>\n<hr>\n<p>b</p>")

    def test_codice(self):
        html_codice = corpo("```python\nif a < b:\n    print('<ok>')\n```")
        self.assertEqual(html_codice, '<pre><span class="nota-lingua">python</span><code>'
                                      "if a &lt; b:\n    print(&#x27;&lt;ok&gt;&#x27;)</code></pre>")
        with self.assertRaises(nota.ErroreNota) as ctx:
            corpo("testo\n\n```\nmai chiuso")
        self.assertEqual(ctx.exception.riga, 7)
        with self.assertRaises(nota.ErroreNota):
            corpo('```"><script>\nx\n```')


class InLinea(unittest.TestCase):
    def test_stili(self):
        self.assertEqual(corpo("*g* _c_ `x<y`"),
                         "<p><strong>g</strong> <em>c</em> <code>x&lt;y</code></p>")
        self.assertEqual(corpo("*grassetto con _corsivo_ dentro*"),
                         "<p><strong>grassetto con <em>corsivo</em> dentro</strong></p>")

    def test_identificatori_restano_intatti(self):
        self.assertEqual(corpo("apple_music e snake_case_name, 2*3*4"),
                         "<p>apple_music e snake_case_name, 2*3*4</p>")

    def test_segni_spaiati(self):
        self.assertEqual(corpo("un * solo e un _ e un ` e [ e ]"),
                         "<p>un * solo e un _ e un ` e [ e ]</p>")

    def test_escape(self):
        self.assertEqual(corpo(r"\*non grassetto\* e \\"), r"<p>*non grassetto* e \</p>")

    def test_link(self):
        self.assertEqual(corpo("[sito](https://mdeangelis.me/diario/?a=1&b=2#x)"),
                         '<p><a href="https://mdeangelis.me/diario/?a=1&amp;b=2#x" '
                         'rel="noopener noreferrer external" target="_blank">sito</a></p>')

    def test_link_pericolosi(self):
        for url in ("javascript:alert(1)", "http://esempio.it", "https://", "//esempio.it",
                    'https://a.it/"onmouseover=alert(1)', "https://a.it/<script>",
                    "https://a.it/ spazio", "data:text/html,x", "HTTPS://A.IT",
                    "https://a.it\\@b.it", "https://-a.it"):
            with self.assertRaises(nota.ErroreNota, msg=url):
                corpo(f"[x]({url})")

    def test_niente_link_annidati(self):
        out = corpo("[a [b](https://x.it)](https://y.it)")
        self.assertEqual(out.count("<a "), 1, out)
        self.assertEqual(sicuro(out), [])


class Sicurezza(unittest.TestCase):
    ATTACCHI = [
        "<script>alert(1)</script>",
        "<img src=x onerror=alert(1)>",
        '"><svg onload=alert(1)>',
        "<!-- commento -->",
        "&lt;script&gt;",
        "*<b>grassetto</b>*",
        "`</code><script>x</script>`",
        "[<script>](https://a.it)",
        "# <iframe src=//x>",
        "> <style>body{display:none}</style>",
        "- <a href=javascript:x>",
        "```\n</pre><script>alert(1)</script>\n```",
        "]]>&#x3C;script&#x3E;",
    ]

    def test_attacchi_escapati(self):
        for attacco in self.ATTACCHI:
            out = corpo(attacco)
            self.assertEqual(sicuro(out), [], f"{attacco!r} -> {out!r}")
            self.assertNotIn("<script", out)
            self.assertNotIn("<img", out)
            self.assertNotIn("<iframe", out)

    def test_fuzz(self):
        """Migliaia di testi casuali: o errore controllato, o HTML con soli tag ammessi."""
        rnd = random.Random(20261112)
        alfabeto = (string.ascii_letters + string.digits + " \n\n\n" + "*_`[]()<>&\"'\\#->!/:=."
                    + "àèé€✓🙂")
        for _ in range(4000):
            lunghezza = rnd.randint(1, 300)
            testo = "".join(rnd.choice(alfabeto) for _ in range(lunghezza))
            if rnd.random() < 0.3:
                testo += f"\n[link](https://esempio.it/{rnd.randint(0, 99)})"
            try:
                out = corpo(testo)
            except nota.ErroreNota:
                continue
            self.assertEqual(sicuro(out), [], repr(testo))

    def test_deterministico(self):
        testo = "# A\n*b* _c_ [d](https://e.it)\n- f"
        self.assertEqual(corpo(testo), corpo(testo))


if __name__ == "__main__":
    unittest.main()
