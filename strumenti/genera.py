#!/usr/bin/env python3
"""Genera le pagine statiche del sito (italiano, inglese e 404) in public/.

Il sito è una sessione di terminale: ogni sezione è un comando
(neofetch, bat, tree, ls). Niente JavaScript, niente codice lato server,
niente dipendenze npm. Per modificarlo si cambiano i testi qui sotto e si
rilancia

    python3 strumenti/genera.py
"""
import datetime
import re
import unicodedata
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public"
SITE = "https://mdeangelis.vercel.app"

# (nome file, link, icona Font Awesome in strumenti/icone/, classe colore)
LINK_MUSICA = [
    ("spotify", "https://open.spotify.com/intl-it/artist/3OucxkLy5uqnpSEHavZbpe", "spotify", "i-spotify"),
    ("apple_music", "https://music.apple.com/us/artist/mdeangelis/1796261710", "itunes-note", "i-apple"),
    ("youtube_music", "https://music.youtube.com/channel/UCYJ3e3Ho1Jv2o2NhuI3JO7A", "youtube", "i-youtube"),
    ("soundcloud", "https://soundcloud.com/mich_de", "soundcloud", "i-soundcloud"),
    ("instagram", "https://instagram.com/mdeangelis_official", "instagram", "i-instagram"),
]

MESI = {"it": "gen feb mar apr mag giu lug ago set ott nov dic".split(),
        "en": "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()}

TESTI = {
    "it": {
        "lang": "it",
        "locale": "it_IT",
        "path": "/",
        "altro": ("/en/", "EN", "en", "English"),
        "title": "MDEANGELIS | Informatica, tecnologia e musica",
        "meta": "Michele De Angelis: professionista IT, appassionato di tecnologia e AI, produttore musicale.",
        "skip": "Vai al contenuto",
        "nav_label": "Sezioni",
        "nav": [("chi-sono", "chi_sono"), ("interessi", "interessi"), ("musica", "musica")],
        "terminale": ("./avvia --sito", ["monogramma caricato", "zero javascript",
                                         "csp: default-src 'none'", "pronto. benvenuto!"]),
        "ruolo": "Professionista IT e produttore musicale",
        "ruoli": ["Professionista IT", "Produttore musicale", "Appassionato di AI"],
        "neofetch": [
            ("Ruolo", None),
            ("Musica", "produttore, alias MDEANGELIS"),
            ("Stack", "informatica, AI, programmazione"),
            ("Lingue", "italiano, inglese"),
            ("Passioni", "viaggi, vino, filosofia"),
            ("Kernel", "curiosità"),
            ("Sito", "statico, 0 JS, 0 cookie"),
        ],
        "intro": "Appassionato di informatica, tecnologia e intelligenza artificiale. "
                 "Esploro il mondo digitale e quello reale con lo stesso entusiasmo: "
                 "musica, viaggi, cultura e conversazioni vere.",
        "cta_musica": "Ascolta la mia musica",
        "cta_chi": "Chi sono",
        "chi_titolo": "Chi sono",
        "chi_file": "chi_sono.md",
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
        "passioni_var": "passioni",
        "passioni": ["Sviluppo software", "AI e machine learning", "Produzione musicale",
                     "Viaggi", "Vino", "Filosofia"],
        "foto_alt": "Una ragazza tiene davanti a sé un disco con il logo MDEANGELIS",
        "badge": "visionario",
        "int_titolo": "Interessi",
        "int_intro": "quello che mi tiene curioso, dentro e fuori dallo schermo",
        "gruppi": [
            ("tecnologia", [
                ("Informatica", "Architetture software, sistemi e soluzioni nuove da esplorare."),
                ("Tecnologia", "Le ultime innovazioni, i gadget e dove sta andando il settore."),
                ("Programmazione", "Codice pulito, coding creativo e sempre un linguaggio nuovo da imparare."),
                ("Intelligenza artificiale", "Modelli linguistici, reti neurali e le domande etiche che portano con sé."),
            ]),
            ("musica_e_cultura", [
                ("Musica", "Ascolto e produzione, tra generi diversi e paesaggi sonori miei."),
                ("Cultura", "Arte, storia, cinema e ogni forma di creatività umana."),
                ("Lettura", "Libri che fanno pensare, dall'informatica alla filosofia."),
                ("Lingue", "Italiano, inglese e oltre, per capire meglio persone e culture."),
            ]),
            ("fuori_dallo_schermo", [
                ("Viaggi", "Culture, luoghi e paesaggi nuovi da collezionare."),
                ("Passeggiate", "Il miglior debugging: camminare e lasciare che le idee si sistemino."),
                ("Amici", "Le relazioni autentiche e i momenti condivisi."),
                ("Buon cibo", "Ricette di tradizione e cucine da scoprire."),
                ("Vini", "Vitigni, territori e degustazioni."),
                ("Conversazioni", "Confronti che fanno crescere e persone con storie da raccontare."),
            ]),
        ],
        "riepilogo_tree": "3 cartelle, 14 file",
        "mus_titolo": "Musica",
        "mus_intro": "produco musica come MDEANGELIS: la trovi su tutte le piattaforme",
        "in_riproduzione": "MDEANGELIS, in riproduzione ovunque",
        "totale": "totale",
        "eza_perm": "Permessi", "eza_size": "Dim", "eza_user": "Utente",
        "eza_data": "Modificato", "eza_nome": "Nome",
        "crediti": "Icone: Font Awesome Free (CC BY 4.0).",
        "footer": "Sito statico: nessun cookie, nessun tracciamento.",
        "nuova_scheda": "(si apre in una nuova scheda)",
        "modo": "NORMALE",
    },
    "en": {
        "lang": "en",
        "locale": "en_US",
        "path": "/en/",
        "altro": ("/", "IT", "it", "Italiano"),
        "title": "MDEANGELIS | IT, technology and music",
        "meta": "Michele De Angelis: IT professional, technology and AI enthusiast, music producer.",
        "skip": "Skip to content",
        "nav_label": "Sections",
        "nav": [("chi-sono", "about"), ("interessi", "interests"), ("musica", "music")],
        "terminale": ("./boot --site", ["monogram loaded", "zero javascript",
                                        "csp: default-src 'none'", "ready. welcome!"]),
        "ruolo": "IT professional and music producer",
        "ruoli": ["IT professional", "Music producer", "AI enthusiast"],
        "neofetch": [
            ("Role", None),
            ("Music", "producer, alias MDEANGELIS"),
            ("Stack", "IT, AI, programming"),
            ("Languages", "Italian, English"),
            ("Passions", "travel, wine, philosophy"),
            ("Kernel", "curiosity"),
            ("Site", "static, 0 JS, 0 cookies"),
        ],
        "intro": "Passionate about computer science, technology and artificial intelligence. "
                 "I explore the digital world and the real one with the same enthusiasm: "
                 "music, travel, culture and real conversations.",
        "cta_musica": "Listen to my music",
        "cta_chi": "About me",
        "chi_titolo": "About me",
        "chi_file": "about_me.md",
        "citazione": "Technology is not just code: it's the language we write the future with.",
        "bio": [
            "I work in IT and live where innovation meets creativity.",
            "I want to understand the why behind every bit. From software architecture "
            "to artificial intelligence, I approach every problem with a child's "
            "curiosity and an engineer's rigour.",
            "But I don't live by code alone. I find inspiration in the harmonies of music, "
            "in the colours of faraway places and in a good conversation over a glass of wine.",
        ],
        "passioni_var": "passions",
        "passioni": ["Software development", "AI and machine learning", "Music production",
                     "Travel", "Wine", "Philosophy"],
        "foto_alt": "A woman holding a record sleeve with the MDEANGELIS logo",
        "badge": "visionary",
        "int_titolo": "Interests",
        "int_intro": "what keeps me curious, on and off the screen",
        "gruppi": [
            ("technology", [
                ("Computer science", "Software architecture, systems and new solutions to explore."),
                ("Technology", "The latest innovations, gadgets and where the industry is heading."),
                ("Programming", "Clean code, creative coding and always a new language to learn."),
                ("Artificial intelligence", "Language models, neural networks and the ethical questions they raise."),
            ]),
            ("music_and_culture", [
                ("Music", "Listening and producing, across genres and soundscapes of my own."),
                ("Culture", "Art, history, cinema and every form of human creativity."),
                ("Reading", "Books that make you think, from computer science to philosophy."),
                ("Languages", "Italian, English and beyond, to better understand people and cultures."),
            ]),
            ("off_the_screen", [
                ("Travel", "New cultures, places and landscapes to collect."),
                ("Walks", "The best debugging: walking and letting ideas settle."),
                ("Friends", "Real relationships and shared moments."),
                ("Good food", "Traditional recipes and cuisines to discover."),
                ("Wine", "Grapes, terroir and tastings."),
                ("Conversations", "Exchanges that help you grow, and people with stories to tell."),
            ]),
        ],
        "riepilogo_tree": "3 directories, 14 files",
        "mus_titolo": "Music",
        "mus_intro": "I produce music as MDEANGELIS: you can find it on every platform",
        "in_riproduzione": "MDEANGELIS, now playing everywhere",
        "totale": "total",
        "eza_perm": "Permissions", "eza_size": "Size", "eza_user": "User",
        "eza_data": "Date Modified", "eza_nome": "Name",
        "crediti": "Icons: Font Awesome Free (CC BY 4.0).",
        "footer": "Static site: no cookies, no tracking.",
        "nuova_scheda": "(opens in a new tab)",
        "modo": "NORMAL",
    },
}

ESTERNO = 'rel="noopener noreferrer external" target="_blank"'


def e(s: str) -> str:
    return escape(s, quote=True)


def slug(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


# ---------- Monogramma vettoriale (ricalcato dal logo) ----------

_righe = (Path(__file__).with_name("monogramma.txt")).read_text().splitlines()
_W, _H = eval(_righe[0])
_TRATTI = [r.split("\t") for r in _righe[1:]]


def monogramma(classe: str) -> str:
    tratti = "".join(
        f'<path class="t-{nome}" pathLength="1" d="{d}"/>' for nome, d in _TRATTI)
    return (f'<svg class="{classe}" viewBox="0 0 {_W} {_H}" aria-hidden="true" '
            f'focusable="false">{tratti}</svg>')


# ---------- Icone delle piattaforme (Font Awesome Free, CC BY 4.0) ----------

def icona(nome: str, classe: str) -> str:
    svg = (Path(__file__).with_name("icone") / f"{nome}.svg").read_text().strip()
    return svg.replace("<svg ", f'<svg class="ico {classe}" aria-hidden="true" focusable="false" ', 1)


# ---------- Marchio: come nel logo, MDE pieno e ANGELIS sottile ----------

MARCHIO = ('<span class="m-scrive"><span class="m-forte">MDE</span>'
           '<span class="m-leggero">ANGELIS</span></span>'
           '<span class="m-cursore" aria-hidden="true"></span>')


def prompt(cmd: str, cwd: str = "~") -> str:
    return (f'<p class="cmd" aria-hidden="true"><span class="ps1">m@deangelis</span>'
            f'<span class="ps-sep">:</span><span class="cwd">{e(cwd)}</span>'
            f'<span class="ps-sep">$</span> {cmd}</p>')


# ---------- Pagina ----------

def pagina(t: dict) -> str:
    p = "../" if t["lang"] == "en" else ""
    altro_href, altro_breve, altro_lang, altro_nome = t["altro"]

    nav = "\n".join(
        f'        <li><a href="#{a}"><span class="n" aria-hidden="true">{i}:</span>{e(n)}</a></li>'
        for i, (a, n) in enumerate(t["nav"], 1))

    righe_term = "\n".join(
        f'        <p class="term-log l{i}"><span class="term-ok">[ ok ]</span> {e(r)}</p>'
        for i, r in enumerate(t["terminale"][1], 1))

    ruoli = "".join(f"<span>{e(r)}</span>" for r in t["ruoli"] + t["ruoli"][:1])
    info = []
    for k, v in t["neofetch"]:
        chiave = f'<span class="k">{e(k)}</span><span class="dp">: </span>'
        if v is None:
            valore = (f'<span class="visivamente-nascosto">{e(t["ruolo"])}</span>'
                      f'<span class="ruota" aria-hidden="true"><span class="ruota-in">{ruoli}</span></span>')
        else:
            valore = f"<span>{e(v)}</span>"
        info.append(f'            <li>{chiave}{valore}</li>')
    info = "\n".join(info)

    # bat chi_sono.md: ogni elemento è una riga numerata
    md = [f'<p class="md-quote"><span class="md-seg" aria-hidden="true">&gt; </span>{e(t["citazione"])}</p>',
          '<p class="md-vuota" aria-hidden="true"></p>']
    md += [f"<p>{e(x)}</p>" for x in t["bio"]]
    md.append('<p class="md-vuota" aria-hidden="true"></p>')
    md.append('<p class="md-code" aria-hidden="true"><span class="sx-k">```</span><span class="sx-c">js</span></p>')
    md.append(f'<p class="md-code"><span class="sx-k">const</span> <span class="sx-v">{e(t["passioni_var"])}</span> <span class="sx-p">= [</span></p>')
    for i, x in enumerate(t["passioni"]):
        virgola = "," if i < len(t["passioni"]) - 1 else ""
        md.append(f'<p class="md-code md-ind"><span class="sx-s">"{e(x)}"</span><span class="sx-p">{virgola}</span></p>')
    md.append('<p class="md-code"><span class="sx-p">];</span></p>')
    md.append('<p class="md-code" aria-hidden="true"><span class="sx-k">```</span></p>')
    md = "\n".join(f"            {x}" for x in md)

    # tree ~/interessi
    tree = [f'<li class="tr-radice"><span class="tr-nome">~/{e(slug(t["int_titolo"]))}</span>'
            f' <span class="tr-com"># {e(t["int_intro"])}</span></li>']
    gruppi = t["gruppi"]
    for gi, (cartella, voci) in enumerate(gruppi):
        ultimo_g = gi == len(gruppi) - 1
        tree.append(f'<li class="tr-dir"><span class="tr-pre" aria-hidden="true">{"└── " if ultimo_g else "├── "}</span>'
                    f'<span class="tr-nome">{e(cartella)}/</span></li>')
        cont_g = "    " if ultimo_g else "│   "
        for ii, (nome, desc) in enumerate(voci):
            ultimo_i = ii == len(voci) - 1
            pre = cont_g + ("└── " if ultimo_i else "├── ")
            cont = cont_g + ("    " if ultimo_i else "│   ")
            tree.append(
                f'<li class="tr-file"><span class="tr-pre" aria-hidden="true">{pre}</span>'
                f'<span class="tr-nome">{e(slug(nome))}</span>'
                f'<span class="tr-cont" aria-hidden="true">{chr(10).join([cont] * 12)}</span>'
                f'<span class="tr-com"><span aria-hidden="true"># </span>{e(desc)}</span></li>')
    tree.append(f'<li class="tr-fine" aria-hidden="true">{e(t["riepilogo_tree"])}</li>')
    tree = "\n".join(f"        {x}" for x in tree)

    # eza -l --icons ~/musica: ogni piattaforma è un link simbolico con la sua icona
    oggi = datetime.date.today()
    data = f"{oggi.day:2d} {MESI[t['lang']][oggi.month - 1]}"
    perm = "".join(
        f'<b class="p-{c if c != "-" else "n"}">{c}</b>' for c in "lrwxrwxrwx")
    ls = []
    for nome, url, file_icona, classe in LINK_MUSICA:
        vista = re.sub(r"^https://", "", url)
        ls.append(
            f'        <li><a class="ls-riga" href="{e(url)}" {ESTERNO}>'
            f'<span class="ls-perm" aria-hidden="true">{perm}</span>'
            f'<span class="ls-size" aria-hidden="true">-</span>'
            f'<span class="ls-user" aria-hidden="true">mde</span>'
            f'<span class="ls-data" aria-hidden="true">{e(data)}</span>'
            f'<span class="ls-ico">{icona(file_icona, classe)}</span>'
            f'<span class="ls-nome">{e(nome)}</span>'
            f'<span class="ls-freccia" aria-hidden="true">-&gt;</span>'
            f'<span class="ls-url">{e(vista)}</span>'
            f'<span class="visivamente-nascosto"> {e(t["nuova_scheda"])}</span></a></li>')
    ls = "\n".join(ls)
    barre = "".join(f'<i class="b{i}"></i>' for i in range(1, 25))

    return f"""<!doctype html>
<html lang="{t["lang"]}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(t["title"])}</title>
  <meta name="description" content="{e(t["meta"])}">
  <meta name="referrer" content="no-referrer">
  <meta name="theme-color" content="#14181e">
  <meta name="color-scheme" content="dark">
  <link rel="canonical" href="{SITE}{t["path"]}">
  <link rel="alternate" hreflang="it" href="{SITE}/">
  <link rel="alternate" hreflang="en" href="{SITE}/en/">
  <link rel="alternate" hreflang="x-default" href="{SITE}/">
  <link rel="icon" href="{p}img/icona.png" type="image/png">
  <link rel="apple-touch-icon" href="{p}img/icona.png">
  <link rel="preload" href="{p}fonts/jetbrains-mono.woff2" as="font" type="font/woff2" crossorigin>
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
    <div class="term">
      <div class="term-barra"><i></i><i></i><i></i><span>mdeangelis — zsh</span></div>
      <div class="term-corpo">
        <p class="term-cmd"><span class="term-prompt">m@deangelis:~$</span> <span class="term-scrive">{e(t["terminale"][0])}</span></p>
{righe_term}
      </div>
    </div>
  </div>
  <a class="salta" href="#contenuto">{e(t["skip"])}</a>

  <header class="barra">
    <a class="barra-casa" href="{t["path"]}" aria-label="MDEANGELIS">
      <img src="{p}img/icona.png" alt="" width="28" height="28">
      <span class="barra-sessione" aria-hidden="true">[mde] 0:zsh</span>
    </a>
    <nav aria-label="{e(t["nav_label"])}">
      <ul>
{nav}
        <li><a class="barra-lingua" href="{altro_href}" hreflang="{altro_lang}" lang="{altro_lang}" aria-label="{e(altro_nome)}">{altro_breve}</a></li>
      </ul>
    </nav>
  </header>

  <main id="contenuto">
    <section class="eroe" aria-labelledby="t-eroe">
      <h1 id="t-eroe" class="marchio">{MARCHIO}</h1>

      {prompt("neofetch")}
      <div class="neofetch">
        <div class="neo-logo">{monogramma("mono")}</div>
        <div class="neo-info">
          <p class="neo-utente"><span class="k">michele</span>@<span class="k">mdeangelis</span></p>
          <p class="neo-riga" aria-hidden="true">------------------</p>
          <ul>
{info}
          </ul>
          <p class="neo-colori" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></p>
        </div>
      </div>

      <p class="commento intro"><span aria-hidden="true"># </span>{e(t["intro"])}</p>
      <p class="azioni">
        <a class="bottone" href="#musica"><span aria-hidden="true">▶ </span>{e(t["cta_musica"])}</a>
        <a class="bottone bottone-linea" href="#chi-sono"><span aria-hidden="true">cd </span>{e(t["cta_chi"])}</a>
      </p>
    </section>

    <section class="blocco" id="chi-sono" aria-labelledby="t-chi">
      <h2 id="t-chi" class="titolo"><span class="hash" aria-hidden="true">## </span>{e(t["chi_titolo"])}</h2>
      {prompt("bat " + e(t["chi_file"]))}
      <div class="chi">
        <div class="bat">
          <p class="bat-testa" aria-hidden="true"><span class="bat-g"></span><span>File: <b>{e(t["chi_file"])}</b></span></p>
          <div class="bat-corpo">
{md}
          </div>
        </div>
        <figure class="finestra ritratto">
          <figcaption class="fin-barra"><i></i><i></i><i></i><span>ritratto.webp</span></figcaption>
          <img src="{p}img/ritratto-880.webp" srcset="{p}img/ritratto-480.webp 480w, {p}img/ritratto-880.webp 880w" sizes="(max-width: 52rem) 92vw, 26rem" alt="{e(t["foto_alt"])}" width="880" height="880" loading="lazy" decoding="async">
          <p class="fin-stato"><span>880x880 webp</span><span class="tag">--{e(t["badge"])}</span></p>
        </figure>
      </div>
    </section>

    <section class="blocco" id="interessi" aria-labelledby="t-int">
      <h2 id="t-int" class="titolo"><span class="hash" aria-hidden="true">## </span>{e(t["int_titolo"])}</h2>
      {prompt("tree ~/" + e(slug(t["int_titolo"])))}
      <ul class="tree">
{tree}
      </ul>
    </section>

    <section class="blocco" id="musica" aria-labelledby="t-mus">
      <h2 id="t-mus" class="titolo"><span class="hash" aria-hidden="true">## </span>{e(t["mus_titolo"])}</h2>
      {prompt("mdeangelis --play")}
      <div class="player" aria-hidden="true">
        <div class="eq">{barre}</div>
        <p class="player-titolo">♪ {e(t["in_riproduzione"])}</p>
      </div>
      <p class="commento"><span aria-hidden="true"># </span>{e(t["mus_intro"])}</p>
      {prompt("eza -l --icons --header ~/" + e(slug(t["mus_titolo"])))}
      <p class="ls-testa" aria-hidden="true"><span>{e(t["eza_perm"])}</span><span>{e(t["eza_size"])}</span><span>{e(t["eza_user"])}</span><span>{e(t["eza_data"])}</span><span></span><span>{e(t["eza_nome"])}</span></p>
      <ul class="ls">
{ls}
      </ul>
      {prompt('<span class="cursore"></span>')}
    </section>
  </main>

  <footer class="stato">
    <p class="stato-riga" aria-hidden="true">
      <span class="stato-modo">{e(t["modo"])}</span>
      <span class="stato-file">~/mdeangelis/index.html</span>
      <span class="stato-info">html+css  0 js  utf-8</span>
      <span class="stato-pos">100%</span>
    </p>
    <p class="stato-note">© 2026 Michele De Angelis. {e(t["footer"])}
      <a href="https://fontawesome.com/license/free" {ESTERNO}>{e(t["crediti"])}<span class="visivamente-nascosto"> {e(t["nuova_scheda"])}</span></a>
      <a href="{altro_href}" hreflang="{altro_lang}" lang="{altro_lang}">{e(altro_nome)}</a></p>
  </footer>
</body>
</html>
"""


def pagina_404() -> str:
    return f"""<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>404 | MDEANGELIS</title>
  <meta name="robots" content="noindex">
  <meta name="referrer" content="no-referrer">
  <meta name="theme-color" content="#14181e">
  <meta name="color-scheme" content="dark">
  <link rel="icon" href="/img/icona.png" type="image/png">
  <link rel="stylesheet" href="/stile.css">
</head>
<body>
  <main class="errore">
    <p class="marchio">{MARCHIO}</p>
    {prompt("cd ./pagina-richiesta")}
    <h1 class="errore-msg">bash: cd: pagina-richiesta: File o directory non esistente</h1>
    <p class="commento" lang="en"><span aria-hidden="true"># </span>404: this page doesn't exist.</p>
    {prompt('cd ~ <span class="cursore"></span>')}
    <p class="azioni">
      <a class="bottone" href="/">Torna alla home</a>
      <a class="bottone bottone-linea" href="/en/" hreflang="en" lang="en">English home</a>
    </p>
  </main>
</body>
</html>
"""


def main() -> None:
    (OUT / "index.html").write_text(pagina(TESTI["it"]), encoding="utf-8")
    (OUT / "en").mkdir(exist_ok=True)
    (OUT / "en" / "index.html").write_text(pagina(TESTI["en"]), encoding="utf-8")
    (OUT / "404.html").write_text(pagina_404(), encoding="utf-8")
    print("Pagine generate in", OUT)


if __name__ == "__main__":
    main()
