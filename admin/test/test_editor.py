"""Test delle azioni dell'editor e della funzione HTTP, con un GitHub finto."""

import base64
import http.client
import json
import os
import sys
import threading
import unittest
from http.server import HTTPServer

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, "..", "lib"))

import accesso  # noqa: E402
import github  # noqa: E402
import azioni  # noqa: E402
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("funzione", os.path.join(QUI, "..", "api", "editor.py"))
funzione = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(funzione)

def _png():
    """Un PNG 2x1 vero, con un blocco tEXt (dati privati) che deve sparire."""
    import struct
    import zlib

    def blocco(tipo, dati):
        return (struct.pack(">I", len(dati)) + tipo + dati
                + struct.pack(">I", zlib.crc32(tipo + dati) & 0xFFFFFFFF))
    return (b"\x89PNG\r\n\x1a\n"
            + blocco(b"IHDR", struct.pack(">IIBBBBB", 2, 1, 8, 2, 0, 0, 0))
            + blocco(b"tEXt", b"Comment\x00gps segreto")
            + blocco(b"IDAT", zlib.compress(b"\x00\xff\x00\x00\x00\xff\x00"))
            + blocco(b"IEND", b""))


PNG = _png()

PUBBLICATO = """titolo: Pubblicato
data: 2026-11-10
tipo: pensiero
---
Ciao.
"""
BOZZA = """titolo: Bozza
data: 2026-11-11
tipo: pensiero
bozza: si
---
Ciao.
"""


class GitHubFinto:
    def __init__(self):
        self.file = {"diario/2026-11-10-pubblicato.nota": PUBBLICATO.encode(),
                     "diario/2026-11-11-bozza.nota": BOZZA.encode()}
        self.commit = []

    @staticmethod
    def sha(dati):
        import hashlib
        return hashlib.sha1(dati).hexdigest()

    def elenco(self, cartella):
        pref = cartella + "/"
        return [(p[len(pref):], self.sha(d), len(d)) for p, d in sorted(self.file.items())
                if p.startswith(pref) and "/" not in p[len(pref):]]

    def leggi(self, percorso):
        if percorso not in self.file:
            raise github.ErroreGitHub(404, "file non trovato")
        return self.file[percorso]

    def scrivi(self, percorso, dati, messaggio, sha=None):
        attuale = self.file.get(percorso)
        if (attuale is None) != (sha is None) or (attuale is not None and self.sha(attuale) != sha):
            raise github.ErroreGitHub(409, "cambiato")
        self.file[percorso] = dati
        self.commit.append((percorso, messaggio))
        return self.sha(dati)


class ConGitHubFinto(unittest.TestCase):
    def setUp(self):
        self.gh = GitHubFinto()
        self.vecchi = (github.elenco, github.leggi, github.scrivi)
        github.elenco, github.leggi, github.scrivi = self.gh.elenco, self.gh.leggi, self.gh.scrivi

    def tearDown(self):
        github.elenco, github.leggi, github.scrivi = self.vecchi


class TestAzioni(ConGitHubFinto):

    def test_elenco_dal_piu_nuovo(self):
        stato, dati = azioni.elenco_post()
        self.assertEqual(stato, 200)
        self.assertEqual([p["nome"] for p in dati["post"]],
                         ["2026-11-11-bozza.nota", "2026-11-10-pubblicato.nota"])
        self.assertTrue(dati["post"][0]["bozza"])

    def test_anteprima_errore_con_riga(self):
        stato, dati = azioni.anteprima("2026-11-12-x.nota", "titolo: X\ndata: 2026-11-12\ntipo: storia\n---\nciao\n")
        self.assertFalse(dati["ok"])
        self.assertEqual(dati["riga"], 3)

    def test_anteprima_html(self):
        _, dati = azioni.anteprima("2026-11-12-x.nota", "titolo: X\ndata: 2026-11-12\ntipo: pensiero\n---\n*ciao* <b>\n")
        self.assertTrue(dati["ok"])
        self.assertIn("<strong>ciao</strong>", dati["html"])
        self.assertIn("&lt;b&gt;", dati["html"])

    def test_salva_nuovo_e_aggiorna(self):
        nome = "2026-11-12-nuovo.nota"
        testo = "titolo: Nuovo\ndata: 2026-11-12\ntipo: pensiero\n---\nciao\n"
        stato, dati = azioni.salva(nome, testo, None, "io@example.com")
        self.assertEqual(stato, 200, dati)
        self.assertIn("diario/" + nome, self.gh.file)
        # di nuovo come "nuovo": rifiutato
        stato, dati = azioni.salva(nome, testo, None, "io@example.com")
        self.assertEqual(stato, 409)
        # aggiornamento con la versione sbagliata: rifiutato
        stato, _ = azioni.salva(nome, testo + "altro\n", "0" * 40, "io@example.com")
        self.assertEqual(stato, 409)
        stato, _ = azioni.salva(nome, testo + "altro\n", dati_sha(self.gh, nome), "io@example.com")
        self.assertEqual(stato, 200)

    def test_salva_rifiuta_errori(self):
        stato, dati = azioni.salva("2026-11-12-x.nota", "titolo: X\n---\n", None, "io@example.com")
        self.assertEqual(stato, 422)
        self.assertEqual(self.gh.commit, [])

    def test_link_a_post_inesistente(self):
        testo = "titolo: X\ndata: 2026-11-12\ntipo: pensiero\n---\n[a](/diario/2026-01-01-nessuno/)\n"
        stato, dati = azioni.salva("2026-11-12-x.nota", testo, None, "io@example.com")
        self.assertEqual((stato, dati["riga"]), (422, 5))

    def test_pubblicato_non_punta_a_bozza(self):
        testo = "titolo: X\ndata: 2026-11-12\ntipo: pensiero\n---\n[a](/diario/2026-11-11-bozza/)\n"
        stato, dati = azioni.salva("2026-11-12-x.nota", testo, None, "io@example.com")
        self.assertEqual(stato, 422)
        self.assertIn("bozza", dati["errore"])
        # da bozza invece si può
        stato, _ = azioni.salva("2026-11-12-x.nota", testo.replace("---", "bozza: si\n---"), None, "io@example.com")
        self.assertEqual(stato, 200)

    def test_post_citato_non_torna_bozza(self):
        citante = "titolo: C\ndata: 2026-11-12\ntipo: pensiero\n---\n[a](/diario/2026-11-10-pubblicato/)\n"
        self.gh.file["diario/2026-11-12-c.nota"] = citante.encode()
        stato, dati = azioni.salva("2026-11-10-pubblicato.nota", PUBBLICATO.replace("---", "bozza: si\n---"),
                                   dati_sha(self.gh, "2026-11-10-pubblicato.nota"), "io@example.com")
        self.assertEqual(stato, 422)
        self.assertIn("2026-11-12-c", dati["errore"])

    def test_nomi_e_percorsi(self):
        for nome in ("../vercel.json", "diario/x.nota", "2026-11-12-X.nota", "2026-11-12-x.md", "", None):
            with self.assertRaises(github.ErroreGitHub):
                azioni.anteprima(nome, "x")
        for nome in ("../x.png", "a/b.png", "x.svg", "x.html", "X.png"):
            with self.assertRaises(github.ErroreGitHub):
                azioni.carica(nome, base64.b64encode(PNG).decode())

    def test_carica_pulisce(self):
        stato, dati = azioni.carica("prova.png", base64.b64encode(PNG).decode())
        self.assertEqual(stato, 200, dati)
        salvato = self.gh.file["diario/media/prova.png"]
        self.assertNotIn(b"gps", salvato)
        self.assertEqual((dati["larghezza"], dati["altezza"]), (2, 1))
        stato, _ = azioni.carica("prova.png", base64.b64encode(PNG).decode())
        self.assertEqual(stato, 409)

    def test_carica_rifiuta_finti(self):
        stato, dati = azioni.carica("finto.png", base64.b64encode(b"<html>ciao</html>").decode())
        self.assertEqual(stato, 422)
        stato, _ = azioni.carica("x.png", "non base64!!")
        self.assertEqual(stato, 400)

    def test_immagine_nel_post(self):
        azioni.carica("prova.png", base64.b64encode(PNG).decode())
        _, dati = azioni.anteprima("2026-11-12-x.nota",
                                   "titolo: X\ndata: 2026-11-12\ntipo: pensiero\n---\n![una prova](prova.png)\n")
        self.assertTrue(dati["ok"], dati)
        self.assertIn('src="/diario/media/prova.png"', dati["html"])


def dati_sha(gh, nome):
    return gh.sha(gh.file["diario/" + nome])


class TestFunzione(ConGitHubFinto):
    """La funzione HTTP vera, su un server locale."""

    def setUp(self):
        super().setUp()
        self.verifica = accesso.verifica
        accesso.verifica = lambda tk: "io@example.com" if tk == "buono" else (_ for _ in ()).throw(accesso.Negato("no"))
        self.server = HTTPServer(("127.0.0.1", 0), funzione.handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        accesso.verifica = self.verifica
        super().tearDown()

    def chiedi(self, metodo, percorso, corpo=None, intestazioni=None):
        c = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        h = dict(intestazioni or {})
        dati = None
        if corpo is not None:
            dati = json.dumps(corpo).encode()
            h.setdefault("Content-Type", "application/json")
        c.request(metodo, percorso, body=dati, headers=h)
        r = c.getresponse()
        risposta = r.read()
        c.close()
        return r.status, r.getheader("Cache-Control"), risposta

    def test_senza_token_niente(self):
        for metodo, a in (("GET", "io"), ("GET", "elenco"), ("GET", "post&nome=2026-11-10-pubblicato.nota"),
                          ("POST", "salva"), ("POST", "carica")):
            stato, _, corpo = self.chiedi(metodo, "/api/editor?a=" + a, {} if metodo == "POST" else None)
            self.assertEqual(stato, 401, a)
            self.assertNotIn(b"Ciao", corpo)
        stato, _, _ = self.chiedi("GET", "/api/editor?a=io", intestazioni={"Cf-Access-Jwt-Assertion": "falso"})
        self.assertEqual(stato, 401)

    def test_con_token(self):
        stato, cache, corpo = self.chiedi("GET", "/api/editor?a=io", intestazioni={"Cf-Access-Jwt-Assertion": "buono"})
        self.assertEqual((stato, cache), (200, "no-store"))
        self.assertEqual(json.loads(corpo)["email"], "io@example.com")

    def test_post_da_altra_origine(self):
        h = {"Cf-Access-Jwt-Assertion": "buono", "Origin": "https://altro.example"}
        stato, _, _ = self.chiedi("POST", "/api/editor?a=salva", {"nome": "x"}, h)
        self.assertEqual(stato, 403)
        h = {"Cf-Access-Jwt-Assertion": "buono"}
        stato, _, _ = self.chiedi("POST", "/api/editor?a=salva", {"nome": "x"}, h)
        self.assertEqual(stato, 403)

    def test_post_buono(self):
        h = {"Cf-Access-Jwt-Assertion": "buono", "Origin": accesso.ORIGINE, "Sec-Fetch-Site": "same-origin"}
        testo = "titolo: Y\ndata: 2026-11-12\ntipo: pensiero\n---\nciao\n"
        stato, _, corpo = self.chiedi("POST", "/api/editor?a=salva", {"nome": "2026-11-12-y.nota", "testo": testo}, h)
        self.assertEqual(stato, 200, corpo)
        stato, _, _ = self.chiedi("POST", "/api/editor?a=salva", {"nome": "../../x", "testo": testo}, h)
        self.assertEqual(stato, 400)

    def test_serve_json(self):
        h = {"Cf-Access-Jwt-Assertion": "buono", "Origin": accesso.ORIGINE, "Content-Type": "text/plain"}
        stato, _, _ = self.chiedi("POST", "/api/editor?a=salva", {"nome": "x"}, h)
        self.assertEqual(stato, 415)


if __name__ == "__main__":
    unittest.main()
