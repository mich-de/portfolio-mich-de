"""Immagini e audio del diario (diario/media/), solo libreria standard.

Per ogni file:
- il formato si riconosce dai byte, non dal nome: un HTML chiamato foto.jpg
  viene rifiutato;
- si leggono larghezza e altezza (per scriverle nell'HTML, niente salti
  della pagina mentre carica);
- si tolgono i metadati: EXIF (posizione GPS, modello del telefono, data),
  XMP, IPTC, commenti, tag ID3. Dalle foto JPEG si tiene solo
  l'orientamento, altrimenti le foto del telefono apparirebbero ruotate.

Sul sito finisce solo la versione pulita, e solo se un post la usa.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

MAX_IMMAGINE = 6_000_000      # byte
MAX_AUDIO = 25_000_000
MAX_LATO = 12_000             # pixel

FORMATI = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp", "gif": "gif",
           "mp3": "mp3", "ogg": "ogg"}
IMMAGINI = ("jpeg", "png", "webp", "gif")
RE_NOME = re.compile(r"^[a-z0-9][a-z0-9-]{0,60}\.(jpg|jpeg|png|webp|gif|mp3|ogg)$")


class ErroreMedia(Exception):
    def __init__(self, nome: str, messaggio: str):
        super().__init__(f"diario/media/{nome}: {messaggio}")
        self.nome = nome
        self.messaggio = messaggio


@dataclass(frozen=True)
class Media:
    nome: str
    tipo: str          # "immagine" | "audio"
    formato: str
    larghezza: int
    altezza: int
    dati: bytes        # già ripuliti dai metadati


def prepara(nome: str, dati: bytes) -> Media:
    m = RE_NOME.match(nome)
    if not m:
        raise ErroreMedia(nome, "nome non valido: minuscole, cifre e trattini, "
                                "estensione jpg, png, webp, gif, mp3 o ogg")
    formato = FORMATI[m.group(1)]
    limite = MAX_AUDIO if formato in ("mp3", "ogg") else MAX_IMMAGINE
    if len(dati) > limite:
        raise ErroreMedia(nome, f"file troppo grande ({len(dati) // 1_000_000} MB, "
                                f"massimo {limite // 1_000_000} MB): riducilo prima di caricarlo")
    lettori = {"jpeg": _jpeg, "png": _png, "webp": _webp, "gif": _gif, "mp3": _mp3, "ogg": _ogg}
    try:
        puliti, larghezza, altezza = lettori[formato](dati)
    except (IndexError, ValueError):
        raise ErroreMedia(nome, f"file rovinato o non è un {formato.upper()}") from None
    except _NonValido as err:
        raise ErroreMedia(nome, str(err)) from None
    if formato in IMMAGINI:
        if not (0 < larghezza <= MAX_LATO and 0 < altezza <= MAX_LATO):
            raise ErroreMedia(nome, f"dimensioni non valide ({larghezza}x{altezza})")
        tipo = "immagine"
    else:
        tipo = "audio"
    return Media(nome, tipo, formato, larghezza, altezza, bytes(puliti))


class _NonValido(Exception):
    pass


def _intero(b: bytes, ordine: str = "big") -> int:
    return int.from_bytes(b, ordine)


# ---------------------------------------------------------------- JPEG

def _orientamento(tiff: bytes) -> int:
    """Legge il tag Orientation (0x0112) dal primo blocco EXIF; 1 se manca."""
    if len(tiff) < 8 or tiff[:2] not in (b"II", b"MM"):
        return 1
    o = "little" if tiff[:2] == b"II" else "big"
    inizio = _intero(tiff[4:8], o)
    if inizio + 2 > len(tiff):
        return 1
    for k in range(min(_intero(tiff[inizio:inizio + 2], o), 500)):
        p = inizio + 2 + 12 * k
        if p + 12 > len(tiff):
            break
        if _intero(tiff[p:p + 2], o) == 0x0112:
            valore = _intero(tiff[p + 8:p + 10], o)
            return valore if 1 <= valore <= 8 else 1
    return 1


def _exif_solo_orientamento(valore: int) -> bytes:
    tiff = (b"MM\x00\x2a\x00\x00\x00\x08"            # intestazione TIFF
            + b"\x00\x01"                              # una sola voce
            + b"\x01\x12\x00\x03\x00\x00\x00\x01"      # Orientation, SHORT, 1
            + valore.to_bytes(2, "big") + b"\x00\x00"
            + b"\x00\x00\x00\x00")                     # nessun altro blocco
    corpo = b"Exif\x00\x00" + tiff
    return b"\xff\xe1" + (len(corpo) + 2).to_bytes(2, "big") + corpo


def _jpeg(d: bytes):
    if d[:3] != b"\xff\xd8\xff":
        raise _NonValido("non è un JPEG")
    fuori = bytearray(b"\xff\xd8")
    i, orient, w, h = 2, 1, 0, 0
    dopo_app0 = None
    while True:
        if i + 4 > len(d) or d[i] != 0xFF:
            raise _NonValido("JPEG troncato o rovinato")
        m = d[i + 1]
        if m == 0xFF:                                  # byte di riempimento
            i += 1
            continue
        if 0xD0 <= m <= 0xD7 or m == 0x01:
            fuori += d[i:i + 2]
            i += 2
            continue
        if m in (0xD8, 0xD9):
            raise _NonValido("JPEG senza immagine")
        lung = _intero(d[i + 2:i + 4])
        if lung < 2 or i + 2 + lung > len(d):
            raise _NonValido("JPEG troncato o rovinato")
        seg = d[i:i + 2 + lung]
        if m == 0xDA:                                  # inizio dei dati: copia fino alla fine
            fine = d.find(b"\xff\xd9", i + 2 + lung)
            if fine == -1:
                raise _NonValido("JPEG troncato (manca la fine)")
            if not w:
                raise _NonValido("JPEG senza dimensioni")
            fuori += d[i:fine + 2]                     # ciò che segue la fine viene scartato
            break
        if m == 0xE1 and seg[4:10] == b"Exif\x00\x00":
            orient = _orientamento(seg[10:])
        if 0xC0 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):
            h, w = _intero(seg[5:7]), _intero(seg[7:9])
        tieni = (m == 0xE0                                         # JFIF
                 or (m == 0xE2 and seg[4:16] == b"ICC_PROFILE\x00")  # profilo colore
                 or m == 0xEE                                      # Adobe (colori)
                 or not (0xE0 <= m <= 0xEF or m == 0xFE))          # niente APPn né commenti
        if tieni:
            fuori += seg
            if m == 0xE0 and dopo_app0 is None:
                dopo_app0 = len(fuori)
        i += 2 + lung
    if orient != 1:
        pos = dopo_app0 if dopo_app0 is not None else 2
        fuori[pos:pos] = _exif_solo_orientamento(orient)
    if orient >= 5:                                    # foto girata di 90°
        w, h = h, w
    return fuori, w, h


# ---------------------------------------------------------------- PNG

_PNG_TOGLI = {b"tEXt", b"zTXt", b"iTXt", b"eXIf", b"tIME"}


def _png(d: bytes):
    if d[:8] != b"\x89PNG\r\n\x1a\n":
        raise _NonValido("non è un PNG")
    fuori = bytearray(d[:8])
    i, w, h, finito = 8, 0, 0, False
    while i < len(d):
        if i + 12 > len(d):
            raise _NonValido("PNG troncato")
        lung = _intero(d[i:i + 4])
        tipo = d[i + 4:i + 8]
        fine = i + 12 + lung
        if fine > len(d) or not tipo.isalpha():
            raise _NonValido("PNG rovinato")
        if i == 8:
            if tipo != b"IHDR":
                raise _NonValido("PNG rovinato (manca IHDR)")
            w, h = _intero(d[i + 8:i + 12]), _intero(d[i + 12:i + 16])
        if tipo not in _PNG_TOGLI:
            fuori += d[i:fine]
        i = fine
        if tipo == b"IEND":
            finito = True
            break
    if not finito:
        raise _NonValido("PNG troncato (manca IEND)")
    return fuori, w, h


# ---------------------------------------------------------------- WebP

def _webp(d: bytes):
    if d[:4] != b"RIFF" or d[8:12] != b"WEBP":
        raise _NonValido("non è un WebP")
    fine_riff = min(len(d), 8 + _intero(d[4:8], "little"))
    i, w, h = 12, 0, 0
    parti, vp8x = [], None
    while i + 8 <= fine_riff:
        tipo = d[i:i + 4]
        lung = _intero(d[i + 4:i + 8], "little")
        if i + 8 + lung > fine_riff:
            raise _NonValido("WebP troncato")
        pezzo = bytearray(d[i:i + 8 + lung])
        if lung % 2:
            pezzo += b"\x00"
        dati = pezzo[8:8 + lung]
        if tipo == b"VP8X":
            vp8x = len(parti)
            w, h = 1 + _intero(dati[4:7], "little"), 1 + _intero(dati[7:10], "little")
        elif tipo == b"VP8 " and not w:
            if dati[3:6] != b"\x9d\x01\x2a":
                raise _NonValido("WebP rovinato")
            w, h = _intero(dati[6:8], "little") & 0x3FFF, _intero(dati[8:10], "little") & 0x3FFF
        elif tipo == b"VP8L" and not w:
            if dati[0] != 0x2F:
                raise _NonValido("WebP rovinato")
            bit = _intero(dati[1:5], "little")
            w, h = (bit & 0x3FFF) + 1, ((bit >> 14) & 0x3FFF) + 1
        if tipo not in (b"EXIF", b"XMP "):
            parti.append(pezzo)
        i += 8 + lung + (lung % 2)
    if not w:
        raise _NonValido("WebP senza immagine")
    if vp8x is not None:
        parti[vp8x][8] &= 0xFF ^ (0x08 | 0x04)         # niente più EXIF né XMP
    corpo = b"WEBP" + b"".join(parti)
    return b"RIFF" + len(corpo).to_bytes(4, "little") + corpo, w, h


# ---------------------------------------------------------------- GIF

def _gif(d: bytes):
    if d[:6] not in (b"GIF87a", b"GIF89a") or len(d) < 14:
        raise _NonValido("non è un GIF")
    return d, _intero(d[6:8], "little"), _intero(d[8:10], "little")


# ---------------------------------------------------------------- audio

def _mp3(d: bytes):
    if d[:3] == b"ID3" and len(d) >= 10:                # tag ID3v2 in testa
        dim = (d[6] & 0x7F) << 21 | (d[7] & 0x7F) << 14 | (d[8] & 0x7F) << 7 | (d[9] & 0x7F)
        d = d[10 + dim + (10 if d[5] & 0x10 else 0):]
    if len(d) >= 128 and d[-128:-125] == b"TAG":       # tag ID3v1 in coda
        d = d[:-128]
    if len(d) < 4 or d[0] != 0xFF or (d[1] & 0xE0) != 0xE0:
        raise _NonValido("non è un MP3")
    return d, 0, 0


def _ogg(d: bytes):
    if d[:4] != b"OggS":
        raise _NonValido("non è un OGG")
    return d, 0, 0
