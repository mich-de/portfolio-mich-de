"""Test del linguaggio Nota. Si lanciano con:  python3 -m unittest discover -s strumenti"""

import random
import string
import unittest
from html.parser import HTMLParser

import nota

TESTA = "titolo: Prova\ndata: 2026-11-12\ntipo: pensiero\n---\n"
FILE = "2026-11-12-prova.nota"


MEDIA = {"foto.jpg": ("immagine", 800, 600), "altra.webp": ("immagine", 600, 800),
         "brano.mp3": ("audio", 0, 0)}


def corpo(testo: str) -> str:
    return nota.leggi(FILE, TESTA + testo, MEDIA).html


def errore(testo: str):
    with unittest.TestCase().assertRaises(nota.ErroreNota) as ctx:
        nota.leggi(FILE, TESTA + testo, MEDIA)
    return ctx.exception


class Controllore(HTMLParser):
    """Verifica che l'HTML prodotto usi solo tag, attributi e valori ammessi."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.problemi = []

    def handle_starttag(self, tag, attrs):
        if tag not in nota.TAG_AMMESSI:
            self.problemi.append(f"tag {tag}")
        for nome, valore in attrs:
            valore = valore or ""
            if nome not in nota.ATTRIBUTI.get(tag, set()):
                self.problemi.append(f"attributo {nome} su {tag}")
            if nome == "href" and not (valore.startswith("https://") or valore.startswith("#")
                                       or (valore.startswith("/") and not valore.startswith("//"))):
                self.problemi.append(f"href {valore}")
            if nome == "src" and not valore.startswith(nota.PERCORSO_MEDIA):
                self.problemi.append(f"src {valore}")
            if nome == "rel" and valore != "noopener noreferrer external":
                self.problemi.append("rel")
            if nome == "class" and not set(valore.split()) <= nota.CLASSI:
                self.problemi.append(f"class {valore}")

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
                    + "~|^" + "àèé€✓🙂")
        for _ in range(4000):
            lunghezza = rnd.randint(1, 300)
            testo = "".join(rnd.choice(alfabeto) for _ in range(lunghezza))
            if rnd.random() < 0.3:
                testo += f"\n[link](https://esempio.it/{rnd.randint(0, 99)})"
            if rnd.random() < 0.2:
                testo = rnd.choice(PEZZI) + "\n" + testo + "\n" + rnd.choice(PEZZI)
            try:
                out = corpo(testo)
            except nota.ErroreNota:
                continue
            self.assertEqual(sicuro(out), [], repr(testo))

    def test_deterministico(self):
        testo = "# A\n*b* _c_ [d](https://e.it)\n- f"
        self.assertEqual(corpo(testo), corpo(testo))


PEZZI = ["![foto](foto.jpg)", '![foto](foto.jpg "una *didascalia*")', "![brano](brano.mp3)",
         "| a | b |\n|---|---:|\n| 1 | 2 |", "> [!nota]\n> testo", "1. uno\n2. due",
         "- [x] fatto\n- [ ] da fare", "testo[^n]\n\n[^n]: nota", "~~via~~ ==sì== [[Ctrl]]",
         "[sezione](#s-titolo)\n# Titolo", "[post](/diario/2026-01-01-altro/)"]


class Media(unittest.TestCase):
    def test_immagine(self):
        out = corpo('![Un gatto](foto.jpg "Il *mio* gatto")')
        self.assertEqual(out, '<figure class="nota-img"><a class="apri" href="/diario/media/foto.jpg">'
                              '<img src="/diario/media/foto.jpg" alt="Un gatto" width="800" height="600" '
                              'loading="lazy" decoding="async"></a>'
                              '<figcaption>Il <strong>mio</strong> gatto</figcaption></figure>')

    def test_galleria(self):
        out = corpo("![a](foto.jpg)\n![b](altra.webp)\n\n![c](foto.jpg)")
        self.assertEqual(out.count('<div class="galleria">'), 1)
        self.assertEqual(out.count("<figure"), 3)

    def test_audio(self):
        out = corpo('![Notturno](brano.mp3 "demo")')
        self.assertIn('<audio controls preload="none" src="/diario/media/brano.mp3"></audio>', out)
        self.assertEqual(sicuro(out), [])

    def test_file_usati_e_copertina(self):
        n = nota.leggi(FILE, "titolo: T\ndata: 2026-11-12\ntipo: passato\ncopertina: altra.webp\n"
                             "---\n![x](foto.jpg)\n![y](foto.jpg)", MEDIA)
        self.assertEqual(n.copertina, "altra.webp")
        self.assertEqual(n.media, ("altra.webp", "foto.jpg"))

    def test_errori(self):
        self.assertIn("non trovato", errore("![x](manca.jpg)").messaggio)
        self.assertIn("non trovato", errore("![x](../../etc/passwd)").messaggio)
        self.assertIn("non trovato", errore("![x](https://altro.it/a.jpg)").messaggio)
        self.assertIn("descrizione", errore("![x](foto.jpg").messaggio)
        self.assertIn("cosa si vede", errore("![](foto.jpg)").messaggio)
        self.assertIn("riga da sole", errore("testo ![x](foto.jpg)").messaggio)
        self.assertEqual(corpo("Wow\\![x](https://a.it)"),
                         '<p>Wow!<a href="https://a.it" rel="noopener noreferrer external" '
                         'target="_blank">x</a></p>')
        with self.assertRaises(nota.ErroreNota):
            nota.leggi(FILE, TESTA + "![x](foto.jpg)")          # senza elenco dei media
        with self.assertRaises(nota.ErroreNota):
            nota.leggi(FILE, "titolo: T\ndata: 2026-11-12\ntipo: passato\ncopertina: brano.mp3\n---\nx", MEDIA)

    def test_alt_escapato(self):
        out = corpo('![<script>"x"](foto.jpg "<b>")')
        self.assertIn('alt="&lt;script&gt;&quot;x&quot;"', out)
        self.assertEqual(sicuro(out), [])


class NuoviBlocchi(unittest.TestCase):
    def test_numerato(self):
        self.assertEqual(corpo("1. uno\n2. due"), "<ol><li>uno</li><li>due</li></ol>")
        self.assertEqual(corpo("3. tre\n4. quattro"), '<ol start="3"><li>tre</li><li>quattro</li></ol>')
        self.assertEqual(corpo("- a\n1. b"), "<ul><li>a</li></ul>\n<ol><li>b</li></ol>")
        self.assertEqual(corpo("2026\\. anno"), "<p>2026. anno</p>")

    def test_spunte(self):
        self.assertEqual(corpo("- [x] fatto\n- [ ] da fare"),
                         '<ul><li><span class="spunta spunta-si">[x]</span> fatto</li>'
                         '<li><span class="spunta">[ ]</span> da fare</li></ul>')

    def test_tabella(self):
        out = corpo("| Anno | Modem |\n|:---:|---:|\n| 1996 | `56k` |\n| 2001 | a \\| b |")
        self.assertEqual(out, '<div class="tabella"><table><thead><tr><th class="a-c">Anno</th>'
                              '<th class="a-d">Modem</th></tr></thead><tbody>'
                              '<tr><td class="a-c">1996</td><td class="a-d"><code>56k</code></td></tr>'
                              '<tr><td class="a-c">2001</td><td class="a-d">a | b</td></tr>'
                              '</tbody></table></div>')
        self.assertEqual(errore("| a | b |\n| c | d |").riga, 5)
        self.assertEqual(errore("| a | b |\n|---|---|\n| 1 |").riga, 7)

    def test_riquadri(self):
        self.assertEqual(corpo("> [!attenzione]\n> Scotta."),
                         '<aside class="riquadro r-attenzione"><p class="riquadro-tipo">[ attenzione ]</p>'
                         "<p>Scotta.</p></aside>")
        self.assertIn("sconosciuto", errore("> [!boh]\n> x").messaggio)
        self.assertIn("vuoto", errore("> [!nota]").messaggio)
        self.assertEqual(corpo("> [!x] non è un riquadro"), "<blockquote><p>[!x] non è un riquadro</p></blockquote>")

    def test_note_a_pie_di_pagina(self):
        out = corpo("Testo[^a] e ancora[^b], di nuovo[^a].\n\n[^b]: Seconda.\n[^a]: Prima, con *stile*.")
        self.assertIn('<a href="#nota-a" id="rif-a-1">[1]</a>', out)
        self.assertIn('<a href="#nota-b" id="rif-b-1">[2]</a>', out)
        self.assertIn('<a href="#nota-a" id="rif-a-2">[1]</a>', out)
        self.assertTrue(out.endswith('<li id="nota-a">Prima, con <strong>stile</strong>. '
                                     '<a class="torna" href="#rif-a-1" aria-label="torna al testo">↑</a></li>'
                                     '<li id="nota-b">Seconda. <a class="torna" href="#rif-b-1" '
                                     'aria-label="torna al testo">↑</a></li></ol></section>'), out)
        self.assertIn("non è definita", errore("x[^z]").messaggio)
        self.assertIn("mai richiamata", errore("x\n\n[^z]: nota").messaggio)
        self.assertIn("due volte", errore("x[^z]\n\n[^z]: a\n[^z]: b").messaggio)
        self.assertNotIn("[^", nota.leggi(FILE, TESTA + "Ciao[^a].\n\n[^a]: n").sommario)

    def test_in_linea_nuovi(self):
        self.assertEqual(corpo("~~vecchio~~ ==nuovo== [[Ctrl]]+[[C]]"),
                         "<p><del>vecchio</del> <mark>nuovo</mark> <kbd>Ctrl</kbd>+<kbd>C</kbd></p>")
        self.assertEqual(corpo("cd ~/diario e ~3 min, a == b"), "<p>cd ~/diario e ~3 min, a == b</p>")

    def test_link_interni(self):
        n = nota.leggi(FILE, TESTA + "[home](/) [musica](/#musica) [post](/diario/2026-01-01-altro/)\n"
                                     "[su](#s-titolo)\n# Titolo", MEDIA)
        self.assertIn('<a href="/#musica">musica</a>', n.html)
        self.assertEqual(n.collegamenti, (("2026-01-01-altro", 5),))
        self.assertEqual(sicuro(n.html), [])
        self.assertIn("nessuna sezione", errore("[x](#s-manca)").messaggio)
        for url in ("//altro.it", "/a/../b", "/A", "/a b", "#Maiusc", "/diario/<x>/"):
            with self.assertRaises(nota.ErroreNota, msg=url):
                corpo(f"[x]({url})")

    def test_tutto_insieme_sicuro(self):
        out = corpo("\n\n".join(PEZZI))
        self.assertEqual(sicuro(out), [], out)


if __name__ == "__main__":
    unittest.main()
