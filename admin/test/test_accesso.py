"""Test del controllo d'accesso: firma, algoritmo, destinatario, scadenza, email.

La chiave RSA qui sotto è SOLO PER I TEST: generata apposta, non protegge niente.
"""

import base64
import hashlib
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))

import accesso  # noqa: E402

N = int(
    "96b4170ea38624505a015e757f5da96636a5f0cf597d2bb54f4e0100ba903599cf4520c3041ab8cbea74ab1d"
    "30e3de8d7dcf9583e72737ec16f7474f5d772b9ff8bbb7b9ccd2f34b3507deb745dfc5a57178870f1ca19f6f"
    "e2f8e5be144fe92dd310e4471cb1a92680b9d80672d4c8c810966149b8a61ec973495b36fa84f6417b90eb4a"
    "5dfbb890930ed381bee6de6b1446814d8333e3d2e1222c3fc3e05e83a16123d8bbd29930aff51c6c7b9bc37a"
    "68b8f2f2fb4aa6482b9f3933a92b11fe8162b536a2b57562b18717f6734378ffde28d950e5cea742af17f478"
    "83ea1dc2aad690735ba947fae929b7ef85c4205a3266712811d26a61d64e9a02e54934e5", 16)
D = int(
    "d213e9b06108e01b97dc20ae44b0c3dbd5d781d65f3665ca31402e405dd17966c27b3d82f223189d9464b3c3"
    "d575fbb486ea407a71ad4754b764583bad06daabfd881aed1e8bfcd59c99d9403d0a05f2ed8d73cdaa692db5"
    "97fe195a31e67e1ed5adce5fc85815d1092607f05ffd79dbaa2e77202ab927b6f01c14d33c6b97a4e7217a3d"
    "c3740628468f753e4a69389c9cb7db1269bce068f397788f238bb3a2bfa7440a4e8a98bbe4f70a0c2830797e"
    "1f5734547088a6a6013e69bb5eb8d3bc6ccc925ea60f93df886722d118502915b4738bac9ee0f107367a5e94"
    "0de5405a0aeb0609989a3b5d6a18ae5fba2308eb0b14d409b5ed184a2509dd4cb4e7257", 16)
E = 65537
CHIAVI = {"k1": (N, E)}
AMMESSI = frozenset({"io@example.com"})
ADESSO = 1_800_000_000


def b64(dati: bytes) -> str:
    return base64.urlsafe_b64encode(dati).rstrip(b"=").decode("ascii")


def firma(dati: bytes, d=D, n=N) -> bytes:
    k = (n.bit_length() + 7) // 8
    t = accesso._SHA256_INFO + hashlib.sha256(dati).digest()
    blocco = b"\x00\x01" + b"\xff" * (k - len(t) - 3) + b"\x00" + t
    return pow(int.from_bytes(blocco, "big"), d, n).to_bytes(k, "big")


def token(testa=None, **corpo):
    t = {"alg": "RS256", "kid": "k1", "typ": "JWT"}
    t.update(testa or {})
    c = {"iss": "https://" + accesso.TEAM, "aud": [accesso.AUD], "email": "io@example.com",
         "iat": ADESSO - 10, "nbf": ADESSO - 10, "exp": ADESSO + 3600}
    c.update(corpo)
    c = {k: v for k, v in c.items() if v is not None}
    inizio = b64(json.dumps(t).encode()) + "." + b64(json.dumps(c).encode())
    return inizio + "." + b64(firma(inizio.encode()))


def verifica(tk):
    return accesso.verifica(tk, adesso=ADESSO, chiavi=CHIAVI, elenco_ammessi=AMMESSI)


class TestAccesso(unittest.TestCase):

    def test_token_buono(self):
        self.assertEqual(verifica(token()), "io@example.com")

    def test_email_maiuscole(self):
        self.assertEqual(verifica(token(email="IO@Example.com")), "io@example.com")

    def test_aud_come_stringa(self):
        self.assertEqual(verifica(token(aud=accesso.AUD)), "io@example.com")

    def negato(self, tk):
        with self.assertRaises(accesso.Negato):
            verifica(tk)

    def test_email_non_ammessa(self):
        self.negato(token(email="altro@example.com"))

    def test_senza_email(self):
        self.negato(token(email=None))

    def test_nessuno_ammesso_se_manca_la_lista(self):
        with self.assertRaises(accesso.Negato):
            accesso.verifica(token(), adesso=ADESSO, chiavi=CHIAVI, elenco_ammessi=frozenset())

    def test_scaduto(self):
        self.negato(token(exp=ADESSO - 3600))

    def test_senza_scadenza(self):
        self.negato(token(exp=None))

    def test_non_ancora_valido(self):
        self.negato(token(nbf=ADESSO + 3600, iat=ADESSO + 3600))

    def test_altra_applicazione(self):
        self.negato(token(aud=["un-altro-aud"]))

    def test_altro_emittente(self):
        self.negato(token(iss="https://altro.cloudflareaccess.com"))

    def test_chiave_sconosciuta(self):
        self.negato(token(testa={"kid": "k2"}))

    def test_alg_none(self):
        tk = token(testa={"alg": "none"})
        self.negato(tk.rsplit(".", 1)[0] + ".")
        self.negato(tk)

    def test_alg_hs256(self):
        self.negato(token(testa={"alg": "HS256"}))

    def test_corpo_cambiato(self):
        tk = token()
        a, b, c = tk.split(".")
        altro = json.loads(base64.urlsafe_b64decode(b + "=="))
        altro["email"] = "io@example.com"
        altro["exp"] = ADESSO + 10 ** 7
        self.negato(a + "." + b64(json.dumps(altro).encode()) + "." + c)

    def test_firma_di_altra_chiave(self):
        tk = token()
        inizio = tk.rsplit(".", 1)[0]
        self.negato(inizio + "." + b64(firma(inizio.encode(), d=D - 2)))

    def test_firma_troppo_corta_o_lunga(self):
        inizio = token().rsplit(".", 1)[0]
        self.negato(inizio + "." + b64(b"\x01" * 255))
        self.negato(inizio + "." + b64(b"\x01" * 257))

    def test_firma_uguale_al_modulo(self):
        inizio = token().rsplit(".", 1)[0]
        self.negato(inizio + "." + b64(N.to_bytes(256, "big")))

    def test_spazzatura(self):
        for tk in ("", "a", "a.b", "a.b.c.d", "!!.!!.!!", "x" * 9000, None, 12):
            self.negato(tk)

    def test_carica_chiavi_scarta_le_deboli(self):
        jwks = {"keys": [
            {"kty": "RSA", "kid": "buona", "n": b64(N.to_bytes(256, "big")), "e": "AQAB"},
            {"kty": "RSA", "kid": "corta", "n": b64((N >> 1100).to_bytes(120, "big")), "e": "AQAB"},
            {"kty": "RSA", "kid": "hs", "alg": "HS256", "n": b64(N.to_bytes(256, "big")), "e": "AQAB"},
            {"kty": "EC", "kid": "ec"},
        ]}
        self.assertEqual(set(accesso.carica_chiavi(json.dumps(jwks))), {"buona"})

    def test_origine(self):
        self.assertTrue(accesso.stessa_origine({"Origin": accesso.ORIGINE, "Sec-Fetch-Site": "same-origin"}))
        self.assertTrue(accesso.stessa_origine({"Origin": accesso.ORIGINE}))
        self.assertFalse(accesso.stessa_origine({"Origin": "https://mdeangelis.me"}))
        self.assertFalse(accesso.stessa_origine({"Origin": accesso.ORIGINE, "Sec-Fetch-Site": "same-site"}))
        self.assertFalse(accesso.stessa_origine({}))


if __name__ == "__main__":
    unittest.main()
