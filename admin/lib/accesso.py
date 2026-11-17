"""Chi può usare l'editor: controllo del token di Cloudflare Access.

admin.mdeangelis.me sta dietro Cloudflare Access. Chi supera il login
(codice via email, solo per gli indirizzi ammessi) arriva qui con un token
firmato da Cloudflare nell'intestazione Cf-Access-Jwt-Assertion.

Questo modulo non si fida di niente altro: a ogni richiesta controlla
- la firma RS256 con le chiavi pubbliche del team Cloudflare;
- emittente, destinatario (tag AUD dell'applicazione) e scadenza;
- che l'email sia una di quelle ammesse (variabile ADMIN_EMAILS su Vercel,
  separate da virgola; se manca non entra nessuno).
Così l'editor resta chiuso anche se qualcuno arriva direttamente su Vercel
saltando Cloudflare.

Solo libreria standard. La verifica RSA segue PKCS#1 v1.5 "ricostruisci e
confronta": si ricostruisce l'intero blocco atteso e lo si confronta byte per
byte, senza interpretare il contenuto della firma.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
import urllib.request

TEAM = os.environ.get("CF_TEAM_DOMAIN", "super-surf-258f.cloudflareaccess.com")
AUD = os.environ.get("CF_AUD", "7dd6054cb916fe675d186f39882741631bbe015c944aaa8500ddf7a8354eda69")
ORIGINE = os.environ.get("ADMIN_ORIGIN", "https://admin.mdeangelis.me")

MARGINE = 60                    # secondi di tolleranza sugli orologi
DURATA_CHIAVI = 3600            # le chiavi pubbliche si rileggono ogni ora
MAX_TOKEN = 8192

# DigestInfo DER di SHA-256 (RFC 8017, 9.2)
_SHA256_INFO = bytes.fromhex("3031300d060960864801650304020105000420")

_cache = {"quando": 0.0, "chiavi": {}}


class Negato(Exception):
    """Accesso rifiutato. Il messaggio è per il registro, non per chi chiede."""


def ammessi() -> frozenset:
    testo = os.environ.get("ADMIN_EMAILS", "")
    return frozenset(x.strip().lower() for x in testo.split(",") if "@" in x)


def _b64(s: str) -> bytes:
    if not isinstance(s, str) or not s or len(s) > MAX_TOKEN:
        raise Negato("parte del token non valida")
    for c in s:
        if not (c.isascii() and (c.isalnum() or c in "-_")):
            raise Negato("parte del token non valida")
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def _intero(s: str) -> int:
    return int.from_bytes(_b64(s), "big")


def carica_chiavi(testo: str) -> dict:
    """kid -> (n, e) dalle chiavi pubbliche JWKS di Cloudflare."""
    chiavi = {}
    for k in json.loads(testo).get("keys", []):
        if k.get("kty") != "RSA" or not isinstance(k.get("kid"), str):
            continue
        if k.get("alg", "RS256") != "RS256" or k.get("use", "sig") != "sig":
            continue
        n, e = _intero(k["n"]), _intero(k["e"])
        if n.bit_length() < 2048 or e < 3 or e % 2 == 0:
            continue
        chiavi[k["kid"]] = (n, e)
    return chiavi


def _chiavi(adesso: float, forza: bool = False) -> dict:
    if forza or not _cache["chiavi"] or adesso - _cache["quando"] > DURATA_CHIAVI:
        url = "https://" + TEAM + "/cdn-cgi/access/certs"
        richiesta = urllib.request.Request(url, headers={"User-Agent": "admin-mdeangelis"})
        with urllib.request.urlopen(richiesta, timeout=5) as r:
            _cache["chiavi"] = carica_chiavi(r.read(200_000).decode("utf-8"))
        _cache["quando"] = adesso
    return _cache["chiavi"]


def firma_valida(dati: bytes, firma: bytes, n: int, e: int) -> bool:
    k = (n.bit_length() + 7) // 8
    if len(firma) != k:
        return False
    s = int.from_bytes(firma, "big")
    if s >= n:
        return False
    blocco = pow(s, e, n).to_bytes(k, "big")
    t = _SHA256_INFO + hashlib.sha256(dati).digest()
    if k < len(t) + 11:
        return False
    atteso = b"\x00\x01" + b"\xff" * (k - len(t) - 3) + b"\x00" + t
    return hmac.compare_digest(blocco, atteso)


def verifica(token: str, adesso: float = None, chiavi=None, elenco_ammessi=None) -> str:
    """Controlla il token e restituisce l'email. Solleva Negato se non va bene."""
    if adesso is None:
        adesso = time.time()
    if not isinstance(token, str) or not token or len(token) > MAX_TOKEN:
        raise Negato("token assente")
    parti = token.split(".")
    if len(parti) != 3:
        raise Negato("token malformato")
    try:
        testa = json.loads(_b64(parti[0]))
        corpo = json.loads(_b64(parti[1]))
        firma = _b64(parti[2])
    except (ValueError, UnicodeDecodeError):
        raise Negato("token malformato") from None
    if not isinstance(testa, dict) or not isinstance(corpo, dict):
        raise Negato("token malformato")
    if testa.get("alg") != "RS256":            # niente "none", niente HS256
        raise Negato("algoritmo non ammesso")
    kid = testa.get("kid")
    if not isinstance(kid, str):
        raise Negato("chiave non indicata")

    elenco = chiavi if chiavi is not None else _chiavi(adesso)
    if kid not in elenco and chiavi is None:  # Cloudflare ruota le chiavi: rileggi una volta
        elenco = _chiavi(adesso, forza=True)
    if kid not in elenco:
        raise Negato("chiave sconosciuta")
    n, e = elenco[kid]
    if not firma_valida((parti[0] + "." + parti[1]).encode("ascii"), firma, n, e):
        raise Negato("firma non valida")

    if corpo.get("iss") != "https://" + TEAM:
        raise Negato("emittente sbagliato")
    aud = corpo.get("aud")
    if isinstance(aud, str):
        aud = [aud]
    if not isinstance(aud, list) or AUD not in aud:
        raise Negato("token di un'altra applicazione")
    exp, iat = corpo.get("exp"), corpo.get("iat")
    nbf = corpo.get("nbf", iat)
    if not isinstance(exp, (int, float)) or adesso > exp + MARGINE:
        raise Negato("token scaduto")
    if isinstance(nbf, (int, float)) and adesso < nbf - MARGINE:
        raise Negato("token non ancora valido")
    if isinstance(iat, (int, float)) and iat > adesso + MARGINE:
        raise Negato("token dal futuro")
    consentiti = ammessi() if elenco_ammessi is None else elenco_ammessi
    email = corpo.get("email")
    if not consentiti or not isinstance(email, str) or email.strip().lower() not in consentiti:
        raise Negato("email non ammessa")
    return email.strip().lower()


def stessa_origine(intestazioni) -> bool:
    """Per le richieste che cambiano qualcosa: devono partire dalla pagina dell'editor."""
    if intestazioni.get("Origin") != ORIGINE:
        return False
    return intestazioni.get("Sec-Fetch-Site") in (None, "same-origin")
