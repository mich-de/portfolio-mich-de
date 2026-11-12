"""Test di media.py con file costruiti a mano (niente librerie esterne)."""

import struct
import unittest
import zlib

import media


def jpeg(orientamento=6, extra=b""):
    tiff = (b"MM\x00\x2a\x00\x00\x00\x08" + b"\x00\x02"
            + b"\x01\x12\x00\x03\x00\x00\x00\x01" + struct.pack(">H", orientamento) + b"\x00\x00"
            + b"\x01\x0f\x00\x02\x00\x00\x00\x04" + b"GPS!"            # finto produttore
            + b"\x00\x00\x00\x00" + b"45N 9E segreto")
    app1 = b"Exif\x00\x00" + tiff
    return (b"\xff\xd8"
            + b"\xff\xe0" + struct.pack(">H", 16) + b"JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
            + b"\xff\xe1" + struct.pack(">H", len(app1) + 2) + app1
            + b"\xff\xfe" + struct.pack(">H", 10) + b"commento"
            + b"\xff\xc0" + struct.pack(">HBHHB", 11, 8, 300, 400, 1) + b"\x01\x11\x00"
            + b"\xff\xda" + struct.pack(">H", 8) + b"\x01\x01\x00\x00\x3f\x00"
            + b"\x12\x34\xff\x00\x56" + b"\xff\xd9" + extra)


def png(testo=b"segreto"):
    def pezzo(tipo, dati):
        return struct.pack(">I", len(dati)) + tipo + dati + struct.pack(">I", zlib.crc32(tipo + dati))
    return (b"\x89PNG\r\n\x1a\n" + pezzo(b"IHDR", struct.pack(">IIBBBBB", 20, 10, 8, 2, 0, 0, 0))
            + pezzo(b"tEXt", b"Author\x00" + testo) + pezzo(b"IDAT", zlib.compress(b"\x00" * 61 * 10))
            + pezzo(b"IEND", b""))


def webp():
    vp8 = b"\x00\x00\x00\x9d\x01\x2a" + struct.pack("<HH", 64, 32) + b"\x00" * 10
    exif = b"segreto!"
    vp8x = bytes([0x08, 0, 0, 0]) + (63).to_bytes(3, "little") + (31).to_bytes(3, "little")
    corpo = (b"WEBP" + b"VP8X" + struct.pack("<I", 10) + vp8x
             + b"VP8 " + struct.pack("<I", len(vp8)) + vp8
             + b"EXIF" + struct.pack("<I", len(exif)) + exif)
    return b"RIFF" + struct.pack("<I", len(corpo)) + corpo


class Immagini(unittest.TestCase):
    def test_jpeg_senza_metadati_ma_dritto(self):
        m = media.prepara("foto.jpg", jpeg(6, extra=b"coda segreta"))
        self.assertEqual((m.tipo, m.larghezza, m.altezza), ("immagine", 300, 400))  # girata
        for segreto in (b"GPS!", b"segreto", b"commento", b"coda"):
            self.assertNotIn(segreto, m.dati)
        self.assertEqual(media._orientamento(m.dati[m.dati.index(b"Exif") + 6:]), 6)
        self.assertTrue(m.dati.endswith(b"\xff\xd9"))

    def test_jpeg_dritto_senza_exif(self):
        m = media.prepara("foto.jpg", jpeg(1))
        self.assertNotIn(b"Exif", m.dati)
        self.assertEqual((m.larghezza, m.altezza), (400, 300))

    def test_png(self):
        m = media.prepara("schema.png", png())
        self.assertEqual((m.larghezza, m.altezza), (20, 10))
        self.assertNotIn(b"segreto", m.dati)
        self.assertIn(b"IDAT", m.dati)

    def test_webp(self):
        m = media.prepara("a.webp", webp())
        self.assertEqual((m.larghezza, m.altezza), (64, 32))
        self.assertNotIn(b"segreto", m.dati)
        self.assertEqual(m.dati[20] & 0x08, 0)
        self.assertEqual(int.from_bytes(m.dati[4:8], "little"), len(m.dati) - 8)

    def test_mp3_senza_tag(self):
        id3 = b"ID3\x03\x00\x00\x00\x00\x00\x07segreto"
        m = media.prepara("brano.mp3", id3 + b"\xff\xfb\x90\x00" + b"\x00" * 200 + b"TAG" + b"x" * 125)
        self.assertEqual(m.tipo, "audio")
        self.assertTrue(m.dati.startswith(b"\xff\xfb"))
        self.assertNotIn(b"segreto", m.dati)
        self.assertNotIn(b"TAG", m.dati)


class Rifiuti(unittest.TestCase):
    def rifiuta(self, nome, dati, parola):
        with self.assertRaises(media.ErroreMedia) as ctx:
            media.prepara(nome, dati)
        self.assertIn(parola, ctx.exception.messaggio)

    def test_travestimenti(self):
        self.rifiuta("foto.jpg", b"<html><script>alert(1)</script></html>", "JPEG")
        self.rifiuta("foto.png", jpeg(), "PNG")
        self.rifiuta("brano.mp3", b"<svg onload=alert(1)>", "MP3")
        self.rifiuta("x.ogg", b"ID3", "OGG")

    def test_nomi(self):
        for nome in ("x.svg", "x.html", "Foto.jpg", "../x.jpg", "x y.jpg", ".jpg", "x.jpg.html"):
            self.rifiuta(nome, jpeg(), "nome")

    def test_troncati_e_troppo_grandi(self):
        self.rifiuta("foto.jpg", jpeg()[:40], "")
        self.rifiuta("a.png", png()[:-12], "")
        self.rifiuta("foto.jpg", b"\xff\xd8\xff" + b"\x00" * (media.MAX_IMMAGINE + 1), "grande")

    def test_byte_a_caso(self):
        import random
        rnd = random.Random(3)
        campioni = {"a.jpg": jpeg(), "a.png": png(), "a.webp": webp()}
        for _ in range(3000):
            nome, dati = rnd.choice(list(campioni.items()))
            dati = bytearray(dati)
            for _ in range(rnd.randint(1, 4)):
                p = rnd.randrange(len(dati))
                if rnd.random() < 0.6:
                    dati[p] = rnd.randrange(256)
                else:
                    del dati[p:p + rnd.randint(1, 20)]
            try:
                media.prepara(nome, bytes(dati))
            except media.ErroreMedia:
                pass


if __name__ == "__main__":
    unittest.main()
