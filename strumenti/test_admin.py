"""L'editor (admin/) usa una copia di nota.py e media.py: devono restare identiche,
altrimenti l'editor accetterebbe post che la build del sito rifiuta (o viceversa).

Se questo test fallisce: cp strumenti/nota.py strumenti/media.py admin/lib/
"""

import pathlib
import unittest

RADICE = pathlib.Path(__file__).resolve().parent.parent


class TestCopieAdmin(unittest.TestCase):
    def test_copie_identiche(self):
        for nome in ("nota.py", "media.py"):
            copia = RADICE / "admin" / "lib" / nome
            if not copia.exists():
                self.skipTest("cartella admin/ assente")
            self.assertEqual((RADICE / "strumenti" / nome).read_bytes(), copia.read_bytes(),
                             f"admin/lib/{nome} è diverso da strumenti/{nome}: ricopialo")


if __name__ == "__main__":
    unittest.main()
