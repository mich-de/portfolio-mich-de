#!/usr/bin/env python3
"""Genera le pagine statiche del sito (italiano e inglese) in public/.

Il sito non ha codice lato server, né JavaScript, né dipendenze npm:
per modificarlo si cambiano i testi qui sotto e si rilancia

    python3 strumenti/genera.py

poi si fa commit delle pagine generate in public/.
"""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public"
SITE = "https://mdeangelis.vercel.app"

LINK_MUSICA = [
    ("spotify", "Spotify", "https://open.spotify.com/intl-it/artist/3OucxkLy5uqnpSEHavZbpe"),
    ("applemusic", "Apple Music", "https://music.apple.com/us/artist/mdeangelis/1796261710"),
    ("youtube", "YouTube Music", "https://music.youtube.com/channel/UCYJ3e3Ho1Jv2o2NhuI3JO7A"),
    ("soundcloud", "SoundCloud", "https://soundcloud.com/mich_de"),
]
INSTAGRAM = "https://instagram.com/mdeangelis_official"

TESTI = {
    "it": {
        "lang": "it",
        "locale": "it_IT",
        "path": "/",
        "altro": ("/en/", "English", "en"),
        "title": "MDEANGELIS | Informatica, tecnologia e musica",
        "meta": "Michele De Angelis: professionista IT, appassionato di tecnologia e AI, produttore musicale.",
        "skip": "Vai al contenuto",
        "nav": [("chi-sono", "Chi sono"), ("interessi", "Interessi"), ("musica", "Musica")],
        "ruolo": "Professionista IT e produttore musicale",
        "ruoli": ["Professionista IT", "Produttore musicale", "Appassionato di AI"],
        "scorri": "Scorri",
        "intro": "Appassionato di informatica, tecnologia e intelligenza artificiale. "
                 "Esploro il mondo digitale e quello reale con lo stesso entusiasmo: "
                 "musica, viaggi, cultura e conversazioni vere.",
        "cta_musica": "Ascolta la mia musica",
        "cta_chi": "Chi sono",
        "chi_titolo": "Chi sono",
        "citazione": "La tecnologia non è solo codice: è il linguaggio con cui scriviamo il futuro.",
        "bio": [
            "Lavoro nell'informatica e vivo all'incrocio tra innovazione e creatività.",
            "Voglio capire il perché dietro ogni bit. Dall'architettura software "
            "all'intelligenza artificiale, affronto ogni problema con la curiosità "
            "di un bambino e il rigore di un ingegnere.",
            "Ma non vivo di solo codice. Trovo ispirazione nelle armonie della musica, "
            "nei colori dei viaggi lontani e in una buona conversazione davanti a un "
            "calice di vino.",
        ],
        "passioni_titolo": "Le passioni di sempre",
        "passioni": ["Sviluppo software", "AI e machine learning", "Produzione musicale",
                     "Viaggi", "Vino", "Filosofia"],
        "int_titolo": "Interessi",
        "int_intro": "Quello che mi tiene curioso, dentro e fuori dallo schermo.",
        "gruppi": [
            ("Tecnologia", [
                ("informatica", "Informatica", "Architetture software, sistemi e soluzioni nuove da esplorare."),
                ("tecnologia", "Tecnologia", "Le ultime innovazioni, i gadget e dove sta andando il settore."),
                ("programmazione", "Programmazione", "Codice pulito, coding creativo e sempre un linguaggio nuovo da imparare."),
                ("ia", "Intelligenza artificiale", "Modelli linguistici, reti neurali e le domande etiche che portano con sé."),
            ]),
            ("Musica e cultura", [
                ("musica", "Musica", "Ascolto e produzione, tra generi diversi e paesaggi sonori miei."),
                ("cultura", "Cultura", "Arte, storia, cinema e ogni forma di creatività umana."),
                ("lettura", "Lettura", "Libri che fanno pensare, dall'informatica alla filosofia."),
                ("lingue", "Lingue", "Italiano, inglese e oltre, per capire meglio persone e culture."),
            ]),
            ("Fuori dallo schermo", [
                ("viaggi", "Viaggi", "Culture, luoghi e paesaggi nuovi da collezionare."),
                ("passeggiate", "Passeggiate", "Il miglior debugging: camminare e lasciare che le idee si sistemino."),
                ("amici", "Amici", "Le relazioni autentiche e i momenti condivisi."),
                ("cibo", "Buon cibo", "Ricette di tradizione e cucine da scoprire."),
                ("vini", "Vini", "Vitigni, territori e degustazioni."),
                ("conversazioni", "Conversazioni", "Confronti che fanno crescere e persone con storie da raccontare."),
            ]),
        ],
        "mus_titolo": "Musica",
        "mus_intro": "Produco musica con il nome MDEANGELIS. La trovi su tutte le piattaforme.",
        "ascolta": "Ascolta su",
        "insta_titolo": "Instagram",
        "insta_testo": "Foto, anteprime e quello che succede tra un progetto e l'altro.",
        "insta_link": "Seguimi su Instagram",
        "footer": "Sito statico: nessun cookie, nessun tracciamento.",
        "nuova_scheda": "(si apre in una nuova scheda)",
    },
    "en": {
        "lang": "en",
        "locale": "en_US",
        "path": "/en/",
        "altro": ("/", "Italiano", "it"),
        "title": "MDEANGELIS | IT, technology and music",
        "meta": "Michele De Angelis: IT professional, technology and AI enthusiast, music producer.",
        "skip": "Skip to content",
        "nav": [("chi-sono", "About"), ("interessi", "Interests"), ("musica", "Music")],
        "ruolo": "IT professional and music producer",
        "ruoli": ["IT professional", "Music producer", "AI enthusiast"],
        "scorri": "Scroll",
        "intro": "Passionate about computer science, technology and artificial intelligence. "
                 "I explore the digital world and the real one with the same enthusiasm: "
                 "music, travel, culture and real conversations.",
        "cta_musica": "Listen to my music",
        "cta_chi": "About me",
        "chi_titolo": "About me",
        "citazione": "Technology is not just code: it's the language we write the future with.",
        "bio": [
            "I work in IT and live where innovation meets creativity.",
            "I want to understand the why behind every bit. From software architecture "
            "to artificial intelligence, I approach every problem with a child's "
            "curiosity and an engineer's rigour.",
            "But I don't live by code alone. I find inspiration in the harmonies of music, "
            "in the colours of faraway places and in a good conversation over a glass of wine.",
        ],
        "passioni_titolo": "Lifelong passions",
        "passioni": ["Software development", "AI and machine learning", "Music production",
                     "Travel", "Wine", "Philosophy"],
        "int_titolo": "Interests",
        "int_intro": "What keeps me curious, on and off the screen.",
        "gruppi": [
            ("Technology", [
                ("informatica", "Computer science", "Software architecture, systems and new solutions to explore."),
                ("tecnologia", "Technology", "The latest innovations, gadgets and where the industry is heading."),
                ("programmazione", "Programming", "Clean code, creative coding and always a new language to learn."),
                ("ia", "Artificial intelligence", "Language models, neural networks and the ethical questions they raise."),
            ]),
            ("Music and culture", [
                ("musica", "Music", "Listening and producing, across genres and soundscapes of my own."),
                ("cultura", "Culture", "Art, history, cinema and every form of human creativity."),
                ("lettura", "Reading", "Books that make you think, from computer science to philosophy."),
                ("lingue", "Languages", "Italian, English and beyond, to better understand people and cultures."),
            ]),
            ("Off the screen", [
                ("viaggi", "Travel", "New cultures, places and landscapes to collect."),
                ("passeggiate", "Walks", "The best debugging: walking and letting ideas settle."),
                ("amici", "Friends", "Real relationships and shared moments."),
                ("cibo", "Good food", "Traditional recipes and cuisines to discover."),
                ("vini", "Wine", "Grapes, terroir and tastings."),
                ("conversazioni", "Conversations", "Exchanges that help you grow, and people with stories to tell."),
            ]),
        ],
        "mus_titolo": "Music",
        "mus_intro": "I produce music as MDEANGELIS. You can find it on every platform.",
        "ascolta": "Listen on",
        "insta_titolo": "Instagram",
        "insta_testo": "Photos, previews and what happens between one project and the next.",
        "insta_link": "Follow me on Instagram",
        "footer": "Static site: no cookies, no tracking.",
        "nuova_scheda": "(opens in a new tab)",
    },
}

ESTERNO = 'rel="noopener noreferrer external" target="_blank"'

# Il monogramma, ricalcato in vettoriale dal logo: tre livelli (rame, grigio, chiaro).
_righe = (Path(__file__).with_name("monogramma.txt")).read_text().splitlines()
_W, _H = eval(_righe[0])
_TRATTI = [r.split("\t") for r in _righe[1:]]


def monogramma(classe: str) -> str:
    tratti = "".join(
        f'<path class="t-{nome}" pathLength="1" d="{d}"/>' for nome, d in _TRATTI)
    return (f'<svg class="{classe}" viewBox="0 0 {_W} {_H}" aria-hidden="true" '
            f'focusable="false">{tratti}</svg>')


TRIANGOLO = '<svg viewBox="0 0 100 100" aria-hidden="true" focusable="false"><path d="M50 9 93 88H7Z"/></svg>'


def e(s: str) -> str:
    return escape(s, quote=True)


def pagina(t: dict) -> str:
    p = "../" if t["lang"] == "en" else ""
    nav = "\n".join(f'          <li><a href="#{a}">{e(n)}</a></li>' for a, n in t["nav"])
    altro_href, altro_nome, altro_lang = t["altro"]
    bio = "\n".join(f"          <p>{e(x)}</p>" for x in t["bio"])
    ruoli = "".join(f"<span>{e(r)}</span>" for r in t["ruoli"] + t["ruoli"][:1])
    passioni = "\n".join(f"            <li>{e(x)}</li>" for x in t["passioni"])

    gruppi = []
    for titolo, voci in t["gruppi"]:
        righe = "\n".join(
            f"""            <li class="voce">
              <img src="{p}img/{k}.webp" alt="" width="56" height="56" loading="lazy" decoding="async">
              <div>
                <h4>{e(n)}</h4>
                <p>{e(d)}</p>
              </div>
            </li>""" for k, n, d in voci)
        gruppi.append(f"""        <section class="gruppo" aria-labelledby="g-{titolo[:4].lower().strip()}">
          <h3 id="g-{titolo[:4].lower().strip()}">{e(titolo)}</h3>
          <ul class="voci">
{righe}
          </ul>
        </section>""")
    gruppi = "\n".join(gruppi)

    piattaforme = "\n".join(
        f"""          <li>
            <a class="piattaforma" href="{e(u)}" {ESTERNO}>
              <img src="{p}img/{k}.webp" alt="" width="40" height="40" loading="lazy" decoding="async">
              <span class="pf-testo"><span class="pf-pre">{e(t["ascolta"])}</span> <span class="pf-nome">{e(n)}</span></span>
              <span class="visivamente-nascosto">{e(t["nuova_scheda"])}</span>
            </a>
          </li>""" for k, n, u in LINK_MUSICA)

    return f"""<!doctype html>
<html lang="{t["lang"]}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(t["title"])}</title>
  <meta name="description" content="{e(t["meta"])}">
  <meta name="referrer" content="no-referrer">
  <meta name="theme-color" content="#232a33">
  <link rel="canonical" href="{SITE}{t["path"]}">
  <link rel="alternate" hreflang="it" href="{SITE}/">
  <link rel="alternate" hreflang="en" href="{SITE}/en/">
  <link rel="alternate" hreflang="x-default" href="{SITE}/">
  <link rel="icon" href="{p}img/icona.png" type="image/png">
  <link rel="apple-touch-icon" href="{p}img/icona.png">
  <link rel="preload" href="{p}fonts/kamerik.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="{p}stile.css">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="MDEANGELIS">
  <meta property="og:locale" content="{t["locale"]}">
  <meta property="og:title" content="{e(t["title"])}">
  <meta property="og:description" content="{e(t["meta"])}">
  <meta property="og:url" content="{SITE}{t["path"]}">
  <meta property="og:image" content="{SITE}/img/og.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
</head>
<body>
  <div class="sipario" aria-hidden="true" hidden>
    {monogramma("sipario-mono")}
    <p class="sipario-marchio"><span class="m-forte">MDE</span><span class="m-leggero">ANGELIS</span></p>
    <span class="sipario-filo"></span>
  </div>
  <a class="salta" href="#contenuto">{e(t["skip"])}</a>

  <header class="testata">
    <div class="testata-in">
      <nav class="nav" aria-label="{"Sezioni" if t["lang"] == "it" else "Sections"}">
        <a class="nav-marchio" href="{t["path"]}" aria-label="MDEANGELIS">
          <img src="{p}img/icona.png" alt="" width="36" height="36">
        </a>
        <ul>
{nav}
          <li><a href="{altro_href}" hreflang="{altro_lang}" lang="{altro_lang}">{e(altro_nome)}</a></li>
        </ul>
      </nav>

      <div class="eroe">
        <div class="forme" aria-hidden="true">
          <span class="forma f-tri f1">{TRIANGOLO}</span>
          <span class="forma f-anello f2"></span>
          <span class="forma f-punto f3"></span>
          <span class="forma f-tri f4">{TRIANGOLO}</span>
          <span class="forma f-anello f5"></span>
          <span class="forma f-tri f6">{TRIANGOLO}</span>
          <span class="forma f-punto f7"></span>
        </div>
        <div class="eroe-centro">
          <div class="alone">{monogramma("mono")}</div>
          <h1 class="marchio"><span class="m-forte">MDE</span><span class="m-leggero">ANGELIS</span></h1>
          <span class="filo-rame" aria-hidden="true"></span>
          <p class="ruolo"><span class="visivamente-nascosto">{e(t["ruolo"])}</span><span class="ruota" aria-hidden="true"><span class="ruota-in">{ruoli}</span></span></p>
          <p class="intro">{e(t["intro"])}</p>
          <p class="azioni">
            <a class="bottone" href="#musica">{e(t["cta_musica"])}</a>
            <a class="bottone bottone-linea" href="#chi-sono">{e(t["cta_chi"])}</a>
          </p>
        </div>
        <div class="scorri" aria-hidden="true"><span>{e(t["scorri"])}</span><i></i></div>
      </div>
    </div>
  </header>

  <main id="contenuto" class="carta">
    <section class="sezione" id="chi-sono" aria-labelledby="t-chi">
      <h2 id="t-chi" class="titolo-sezione">{e(t["chi_titolo"])}</h2>
      <div class="chi">
        <blockquote class="citazione"><p>{e(t["citazione"])}</p></blockquote>
        <div class="bio">
{bio}
          <h3 class="passioni-titolo">{e(t["passioni_titolo"])}</h3>
          <ul class="passioni">
{passioni}
          </ul>
        </div>
      </div>
    </section>

    <section class="sezione" id="interessi" aria-labelledby="t-int">
      <h2 id="t-int" class="titolo-sezione">{e(t["int_titolo"])}</h2>
      <p class="sezione-intro">{e(t["int_intro"])}</p>
      <div class="gruppi">
{gruppi}
      </div>
    </section>
  </main>

  <section class="musica" id="musica" aria-labelledby="t-mus">
    <div class="musica-in">
      <h2 id="t-mus" class="titolo-sezione">{e(t["mus_titolo"])}</h2>
      <p class="sezione-intro">{e(t["mus_intro"])}</p>
      <ul class="piattaforme">
{piattaforme}
      </ul>
      <div class="insta">
        <img src="{p}img/instagram.webp" alt="" width="40" height="40" loading="lazy" decoding="async">
        <div>
          <h3>{e(t["insta_titolo"])}</h3>
          <p>{e(t["insta_testo"])}</p>
          <a href="{INSTAGRAM}" {ESTERNO}>{e(t["insta_link"])}<span class="visivamente-nascosto"> {e(t["nuova_scheda"])}</span></a>
        </div>
      </div>
    </div>
  </section>

  <footer class="piede">
    <p class="piede-marchio"><span class="m-forte">MDE</span><span class="m-leggero">ANGELIS</span></p>
    <p>© 2026 Michele De Angelis. {e(t["footer"])}</p>
    <p><a href="{altro_href}" hreflang="{altro_lang}" lang="{altro_lang}">{e(altro_nome)}</a></p>
  </footer>
</body>
</html>
"""


def main() -> None:
    (OUT / "index.html").write_text(pagina(TESTI["it"]), encoding="utf-8")
    (OUT / "en").mkdir(exist_ok=True)
    (OUT / "en" / "index.html").write_text(pagina(TESTI["en"]), encoding="utf-8")
    print("Pagine generate in", OUT)


if __name__ == "__main__":
    main()
