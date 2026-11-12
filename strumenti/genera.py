#!/usr/bin/env python3
"""Genera le pagine statiche del sito (italiano, inglese e 404) in public/.

Il sito è una sessione di terminale: ogni sezione è un comando
(neofetch, bat, tree, ls). Niente JavaScript, niente codice lato server,
niente dipendenze npm. Per modificarlo si cambiano i testi qui sotto e si
rilancia

    python3 strumenti/genera.py
"""
import datetime
import os
import re
import shutil
import sys
import unicodedata
from html import escape
from pathlib import Path

import media  # immagini e audio del diario: controllo dei formati e niente metadati
import nota  # il linguaggio del diario, accanto a questo file

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public"
SITE = "https://mdeangelis.vercel.app"

# (nome file, link, icona Font Awesome in strumenti/icone/, classe colore, profilo, azione)
LINK_MUSICA = [
    ("spotify", "https://open.spotify.com/intl-it/artist/3OucxkLy5uqnpSEHavZbpe", "spotify", "i-spotify", "@MDEANGELIS", "ascolta"),
    ("apple_music", "https://music.apple.com/us/artist/mdeangelis/1796261710", "itunes-note", "i-apple", "@MDEANGELIS", "ascolta"),
    ("youtube_music", "https://music.youtube.com/channel/UCYJ3e3Ho1Jv2o2NhuI3JO7A", "youtube", "i-youtube", "@MDEANGELIS", "ascolta"),
    ("soundcloud", "https://soundcloud.com/mich_de", "soundcloud", "i-soundcloud", "@mich_de", "ascolta"),
    ("instagram", "https://instagram.com/mdeangelis_official", "instagram", "i-instagram", "@mdeangelis_official", "segui"),
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
        # comando mostrato nella console quando si apre una sezione dal menu
        "salti": {"chi-sono": ("cd ~/chi_sono", "apro chi_sono.md"),
                  "interessi": ("cd ~/interessi", "apro interessi/"),
                  "musica": ("cd ~/musica", "avvio mdeangelis --play"),
                  "diario": ("cd ~/diario", "git log --oneline -3")},
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
        "azioni_link": {"ascolta": "ascolta", "segui": "segui"},
        "footer": "Sito statico: nessun cookie, nessun tracciamento.",
        "nuova_scheda": "(si apre in una nuova scheda)",
        "modo": "NORMALE",
        "nav_diario": "diario",
        "dia_titolo": "Diario",
        "dia_intro": "gli ultimi post: pensieri, storie di adesso, cose del passato spiegate",
        "dia_tutto": "tutto il diario",
        "dia_nota": "",
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
        "salti": {"chi-sono": ("cd ~/about", "opening about_me.md"),
                  "interessi": ("cd ~/interests", "opening interests/"),
                  "musica": ("cd ~/music", "starting mdeangelis --play"),
                  "diario": ("cd ~/journal", "git log --oneline -3")},
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
        "azioni_link": {"ascolta": "listen", "segui": "follow"},
        "footer": "Static site: no cookies, no tracking.",
        "nuova_scheda": "(opens in a new tab)",
        "modo": "NORMAL",
        "nav_diario": "journal",
        "dia_titolo": "Journal",
        "dia_intro": "latest posts: thoughts, stories from today, how things used to work",
        "dia_tutto": "the whole journal",
        "dia_nota": " (in Italian)",
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


def salto(t: dict, sezione: str) -> str:
    """Console che 'esegue' il comando quando si arriva alla sezione dal menu (solo CSS, :target)."""
    cmd, log = t["salti"][sezione]
    return (f'<div class="salto" aria-hidden="true"><div class="salto-term">'
            f'<div class="term-barra"><i></i><i></i><i></i><span>mdeangelis — zsh</span></div>'
            f'<div class="salto-corpo">'
            f'<p><span class="term-prompt">m@deangelis:~$</span> <span class="salto-scrive">{e(cmd)}</span></p>'
            f'<p class="salto-log"><span class="term-ok">[ ok ]</span> {e(log)}</p>'
            f'<p class="salto-avanza"><span class="salto-barra"></span><span class="salto-pct"></span></p>'
            f'</div></div></div>')


def prompt(cmd: str, cwd: str = "~") -> str:
    return (f'<p class="cmd" aria-hidden="true"><span class="ps1">m@deangelis</span>'
            f'<span class="ps-sep">:</span><span class="cwd">{e(cwd)}</span>'
            f'<span class="ps-sep">$</span> {cmd}</p>')


# ---------- Pagina ----------

def pagina(t: dict, note=()) -> str:
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
    for nome, url, file_icona, classe, profilo, azione in LINK_MUSICA:
        ls.append(
            f'        <li><a class="ls-riga" href="{e(url)}" {ESTERNO}>'
            f'<span class="ls-perm" aria-hidden="true">{perm}</span>'
            f'<span class="ls-size" aria-hidden="true">-</span>'
            f'<span class="ls-user" aria-hidden="true">mde</span>'
            f'<span class="ls-data" aria-hidden="true">{e(data)}</span>'
            f'<span class="ls-ico">{icona(file_icona, classe)}</span>'
            f'<span class="ls-nome">{e(nome)}</span>'
            f'<span class="ls-freccia" aria-hidden="true">-&gt;</span>'
            f'<span class="ls-url">{e(profilo)}</span>'
            f'<span class="ls-azione" aria-hidden="true">{e(t["azioni_link"][azione])} ↗</span>'
            f'<span class="visivamente-nascosto"> {e(t["nuova_scheda"])}</span></a></li>')
    ls = "\n".join(ls)
    barre = "".join(f'<i class="b{i}"></i>' for i in range(1, 25))
    sezione_diario = blocco_diario(t, note)

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
        <li><a href="/diario/"><span class="n" aria-hidden="true">{len(t["nav"]) + 1}:</span>{e(t["nav_diario"])}</a></li>
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
      {salto(t, "chi-sono")}
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
      {salto(t, "interessi")}
      <h2 id="t-int" class="titolo"><span class="hash" aria-hidden="true">## </span>{e(t["int_titolo"])}</h2>
      {prompt("tree ~/" + e(slug(t["int_titolo"])))}
      <ul class="tree">
{tree}
      </ul>
    </section>

    <section class="blocco" id="musica" aria-labelledby="t-mus">
      {salto(t, "musica")}
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
    </section>
{sezione_diario}
    {prompt('<span class="cursore"></span>')}
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


# ---------- Diario: post scritti in Nota (vedi strumenti/nota.py) ----------
#
# diario/AAAA-MM-GG-titolo.nota  ->  /diario/AAAA-MM-GG-titolo/
# L'indice è un "git log", ogni post un "git show", i tipi sono rami.

DIARIO = ROOT / "diario"
AUTORE = "Michele De Angelis"
GIORNI = "lun mar mer gio ven sab dom".split()
GIORNI_LUNGHI = "lunedì martedì mercoledì giovedì venerdì sabato domenica".split()
MESI_LUNGHI = ("gennaio febbraio marzo aprile maggio giugno luglio agosto "
               "settembre ottobre novembre dicembre").split()
# tipo del post -> (ramo, cosa contiene)
RAMI = {
    "pensiero": ("pensieri", "pensieri del giorno"),
    "cronaca": ("cronache", "storie che stanno succedendo adesso"),
    "passato": ("passato", "come funzionavano le cose una volta"),
}
DIARIO_INTRO = "pensieri del giorno, storie di adesso e cose del passato spiegate da un nerd."


def data_breve(d: datetime.date) -> str:
    return f"{GIORNI[d.weekday()]} {d.day} {MESI['it'][d.month - 1]} {d.year}"


def data_lunga(d: datetime.date) -> str:
    return f"{GIORNI_LUNGHI[d.weekday()]} {d.day} {MESI_LUNGHI[d.month - 1]} {d.year}"


MEDIA = {}   # nome -> media.Media, riempito da carica_diario


def carica_media(errori: list) -> dict:
    cartella = DIARIO / "media"
    trovati = {}
    if not cartella.is_dir():
        return trovati
    for f in sorted(cartella.iterdir()):
        if f.name.startswith("."):
            continue
        if not f.is_file():
            errori.append(f"diario/media/{f.name}: niente sottocartelle in diario/media/")
            continue
        try:
            trovati[f.name] = media.prepara(f.name, f.read_bytes())
        except media.ErroreMedia as err:
            errori.append(str(err))
    return trovati


def carica_diario(bozze: bool) -> list:
    """Legge tutti i post. Un solo errore ferma tutto: niente va online a metà."""
    if not DIARIO.is_dir():
        return []
    errori = []
    MEDIA.clear()
    MEDIA.update(carica_media(errori))
    info = {k: (m.tipo, m.larghezza, m.altezza) for k, m in MEDIA.items()}
    note = []
    for f in sorted(DIARIO.iterdir()):
        if f.name.startswith(".") or f.suffix == ".md" or f.name == "media":
            continue  # appunti, guida e cartella dei media
        if not f.is_file() or f.suffix != ".nota":
            errori.append(f"diario/{f.name}: qui vanno solo file .nota (o .md per gli appunti)")
            continue
        try:
            note.append(nota.leggi(f.name, f.read_text(encoding="utf-8"), info))
        except UnicodeDecodeError:
            errori.append(f"diario/{f.name}: il file deve essere salvato in UTF-8")
        except nota.ErroreNota as err:
            errori.append(f"diario/{err}")
    # i link ad altri post devono portare a un post che esiste (e che è pubblicato,
    # se anche questo lo è)
    stato = {n.slug: n.bozza for n in note}
    for n in note:
        for altro, riga in n.collegamenti:
            if altro not in stato:
                errori.append(f"diario/{n.file}:{riga}: il post {altro} non esiste")
            elif stato[altro] and not n.bozza:
                errori.append(f"diario/{n.file}:{riga}: il post {altro} è ancora una bozza")
    if errori:
        sys.exit("Errori nel diario, non ho pubblicato niente:\n  " + "\n  ".join(errori))
    if not bozze:
        note = [n for n in note if not n.bozza]
    return ordina(note)


def ordina(note: list) -> list:
    """Dal più nuovo al più vecchio: data, poi ora (chi non ha l'ora va a inizio giornata)."""
    return sorted(note, key=lambda n: (n.data, n.ora, n.slug), reverse=True)


def fuso_roma(d: datetime.date) -> str:
    """+02:00 con l'ora legale (dall'ultima domenica di marzo all'ultima di ottobre), se no +01:00."""
    def ultima_domenica(mese):
        giorno = datetime.date(d.year, mese, 31)
        return giorno - datetime.timedelta(days=(giorno.weekday() + 1) % 7)
    return "+02:00" if ultima_domenica(3) <= d < ultima_domenica(10) else "+01:00"


def istante(n) -> str:
    """Data e ora del post in formato ISO 8601 (per <time> e per il feed)."""
    if not n.ora:
        return n.data.isoformat()
    return f"{n.data.isoformat()}T{n.ora}:00{fuso_roma(n.data)}"


def apertura(cmd: str, log: str) -> str:
    """Console che si apre al caricamento della pagina, come quella del menu."""
    return salto({"salti": {"x": (cmd, log)}}, "x").replace('class="salto"', 'class="salto salto-subito"', 1)


def testa(titolo: str, descrizione: str, percorso: str, og_tipo: str = "website",
          noindex: bool = False, extra: str = "", immagine: tuple = ("/img/og.jpg", 1200, 630)) -> str:
    img, img_w, img_h = immagine
    robots = '\n  <meta name="robots" content="noindex">' if noindex else ""
    return f"""<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(titolo)}</title>
  <meta name="description" content="{e(descrizione)}">
  <meta name="referrer" content="no-referrer">
  <meta name="theme-color" content="#14181e">
  <meta name="color-scheme" content="dark">{robots}
  <link rel="canonical" href="{SITE}{percorso}">
  <link rel="alternate" type="application/atom+xml" title="Diario di MDEANGELIS" href="/diario/feed.xml">
  <link rel="icon" href="/img/icona.png" type="image/png">
  <link rel="apple-touch-icon" href="/img/icona.png">
  <link rel="preload" href="/fonts/jetbrains-mono.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="/stile.css">
  <meta property="og:type" content="{og_tipo}">
  <meta property="og:site_name" content="MDEANGELIS">
  <meta property="og:locale" content="it_IT">
  <meta property="og:title" content="{e(titolo)}">
  <meta property="og:description" content="{e(descrizione)}">
  <meta property="og:url" content="{SITE}{percorso}">
  <meta property="og:image" content="{SITE}{img}">
  <meta property="og:image:width" content="{img_w}">
  <meta property="og:image:height" content="{img_h}">
  <meta name="twitter:card" content="summary_large_image">{extra}
</head>"""


def barra_diario(corrente: str) -> str:
    t = TESTI["it"]
    voci = "\n".join(
        f'        <li><a href="/#{a}"><span class="n" aria-hidden="true">{i}:</span>{e(n)}</a></li>'
        for i, (a, n) in enumerate(t["nav"], 1))
    return f"""  <a class="salta" href="#contenuto">{e(t["skip"])}</a>

  <header class="barra">
    <a class="barra-casa" href="/" aria-label="MDEANGELIS, home">
      <img src="/img/icona.png" alt="" width="28" height="28">
      <span class="barra-sessione" aria-hidden="true">[mde] {len(t["nav"]) + 1}:diario</span>
    </a>
    <nav aria-label="{e(t["nav_label"])}">
      <ul>
{voci}
        <li><a class="barra-qui" href="/diario/" aria-current="{corrente}"><span class="n" aria-hidden="true">{len(t["nav"]) + 1}:</span>diario</a></li>
      </ul>
    </nav>
  </header>"""


def piede_diario(file: str) -> str:
    t = TESTI["it"]
    return f"""  <footer class="stato">
    <p class="stato-riga" aria-hidden="true">
      <span class="stato-modo">{e(t["modo"])}</span>
      <span class="stato-file">~/mdeangelis/{e(file)}</span>
      <span class="stato-info">nota v{nota.VERSIONE}  0 js  utf-8</span>
      <span class="stato-pos">100%</span>
    </p>
    <p class="stato-note">© 2026 Michele De Angelis. {e(t["footer"])}
      <a href="/diario/feed.xml">feed atom</a>
      <a href="/">home</a></p>
  </footer>"""


def riferimenti(n, primo: bool) -> str:
    ramo = RAMI[n.tipo][0]
    refs = ['<span class="ref-head">HEAD -&gt; main</span>'] if primo else []
    refs.append(f'<a class="ref-ramo" href="/diario/{ramo}/">{ramo}</a>')
    refs += [f'<span class="ref-tag">tag: {e(x)}</span>' for x in n.tag]
    bozza = ' <span class="ref-bozza">[bozza]</span>' if n.bozza else ""
    return '<span class="log-ref">(' + ", ".join(refs) + ")</span>" + bozza


def voce_log(n, primo: bool) -> str:
    """Un commit del log: intestazione git e, sotto, la scheda cliccabile del post."""
    miniatura = ""
    if n.copertina:
        c = MEDIA[n.copertina]
        miniatura = (f'\n            <img class="log-mini" src="{e(nota.PERCORSO_MEDIA + c.nome)}" alt="" '
                     f'width="{c.larghezza}" height="{c.altezza}" loading="lazy" decoding="async">')
    return f"""        <li class="log-voce">
          <p class="log-commit"><span class="log-parola" aria-hidden="true">commit </span><span class="log-hash" aria-hidden="true">{n.hash[:7]}</span> {riferimenti(n, primo)}</p>
          <p class="log-meta"><span class="log-chiave" aria-hidden="true">Date:   </span><time datetime="{istante(n)}">{data_breve(n.data)}{" " + n.ora if n.ora else ""}</time>, {n.minuti} min di lettura</p>
          <article class="log-scheda{" con-mini" if n.copertina else ""}">
            <div class="log-testo">
              <h2 class="log-titolo"><a href="/diario/{n.slug}/">{e(n.titolo)}</a></h2>
              <p class="log-sommario">{e(n.sommario)}</p>
              <p class="log-apri" aria-hidden="true"><span class="log-cmd">$ git show {n.hash[:7]}</span><span class="log-leggi">leggi l'articolo <span class="log-freccia">-&gt;</span></span></p>
            </div>{miniatura}
          </article>
        </li>"""


def pagina_indice(note: list, tutte: list, ramo=None) -> str:
    """L'indice del diario (ramo None) o di un solo tipo di post."""
    percorso = f"/diario/{ramo}/" if ramo else "/diario/"
    righe_rami = []
    for nome, descr, conta, href in (
            [("main", "tutto", len(tutte), "/diario/")]
            + [(r, d, sum(1 for n in tutte if n.tipo == tipo), f"/diario/{r}/")
               for tipo, (r, d) in RAMI.items()]):
        qui = (ramo or "main") == nome
        corrente = ' aria-current="page"' if qui else ""
        segno = "*" if qui else " "
        righe_rami.append(
            f'        <li><a href="{href}"{corrente}><span class="rami-segno" aria-hidden="true">{segno}</span>'
            f'{nome}</a> <span class="commento"><span aria-hidden="true"># </span>{e(descr)} ({conta})</span></li>')
    righe_rami = "\n".join(righe_rami)

    comando = "git log" + (f" {ramo}" if ramo else "")
    if note:
        corpo = '      <ol class="log">\n' + "\n".join(
            voce_log(n, i == 0 and not ramo) for i, n in enumerate(note)) + "\n      </ol>"
    elif ramo:
        corpo = (f'      <p class="errore-msg">fatal: il ramo \'{ramo}\' non ha ancora commit</p>\n'
                 f'      <p class="commento"><span aria-hidden="true"># </span>niente qui per ora: torna presto.</p>')
    else:
        corpo = ('      <p class="errore-msg">fatal: il tuo branch corrente \'main\' non ha ancora commit</p>\n'
                 '      <p class="commento"><span aria-hidden="true"># </span>il diario è appena nato: il primo post è in arrivo.</p>')

    titolo_pag = (f"{ramo} | Diario | MDEANGELIS" if ramo else "Diario | MDEANGELIS")
    descr_pag = (RAMI_DESCR[ramo].capitalize() + ", dal diario di Michele De Angelis." if ramo
                 else "Il diario di Michele De Angelis: " + DIARIO_INTRO)
    log = f"{len(note)} commit" + (f" su {ramo}" if ramo else ", ramo main")
    h1 = (f'<span class="hash" aria-hidden="true">~/diario/</span>{e(ramo)}' if ramo
          else '<span class="hash" aria-hidden="true">~/</span>diario')
    return f"""{testa(titolo_pag, descr_pag, percorso)}
<body>
{barra_diario("page" if not ramo else "true")}

  <main id="contenuto" class="diario">
    {apertura("cd ~/diario && " + comando, log)}
    <h1 class="titolo">{h1}</h1>
    <p class="commento intro"><span aria-hidden="true"># </span>{e(DIARIO_INTRO)}</p>

    {prompt("git branch", "~/diario")}
    <nav aria-label="Tipi di post">
      <ul class="rami">
{righe_rami}
      </ul>
    </nav>

    {prompt(e(comando), "~/diario")}
{corpo}

    {prompt('<span class="cursore"></span>', "~/diario")}
  </main>

{piede_diario("diario/" + (ramo + "/" if ramo else ""))}
</body>
</html>
"""


RAMI_DESCR = {r: d for r, d in RAMI.values()}


def pagina_post(n, piu_nuovo, piu_vecchio) -> str:
    ramo, descr_ramo = RAMI[n.tipo]
    tag = " ".join(f'<span class="ref-tag">#{e(x)}</span>' for x in n.tag)
    riga_tag = (f'\n        <div><dt>Tag:</dt><dd>{tag}</dd></div>' if n.tag else "")
    avviso = ('\n    <p class="avviso-bozza">[bozza] questo post non è pubblicato: '
              'lo vedi solo nell\'anteprima.</p>' if n.bozza else "")
    vicini = []
    for etichetta, altro in (("successivo", piu_nuovo), ("precedente", piu_vecchio)):
        if altro is not None:
            vicini.append(
                f'        <li><a href="/diario/{altro.slug}/"><span class="vic-dove">{etichetta}</span>'
                f'<span class="log-hash" aria-hidden="true">{altro.hash[:7]}</span>'
                f'<span class="vic-titolo">{e(altro.titolo)}</span></a></li>')
    vicini_html = ""
    if vicini:
        vicini_html = (f'\n    {prompt("git log --oneline -1 HEAD~1", "~/diario")}\n'
                       f'    <nav aria-label="Altri post">\n      <ul class="vicini">\n'
                       + "\n".join(vicini) + "\n      </ul>\n    </nav>")
    immagine = ("/img/og.jpg", 1200, 630)
    copertina = ""
    if n.copertina:
        c = MEDIA[n.copertina]
        immagine = (nota.PERCORSO_MEDIA + c.nome, c.larghezza, c.altezza)
        copertina = (f'\n      <figure class="nota-copertina"><img src="{e(immagine[0])}" alt="" '
                     f'width="{c.larghezza}" height="{c.altezza}" decoding="async"></figure>')
    extra = (f'\n  <meta property="article:published_time" content="{istante(n)}">'
             f'\n  <meta property="article:author" content="{AUTORE}">')
    return f"""{testa(n.titolo + " | Diario | MDEANGELIS", n.sommario, f"/diario/{n.slug}/",
                 og_tipo="article", noindex=n.bozza, extra=extra, immagine=immagine)}
<body>
{barra_diario("true")}

  <main id="contenuto" class="diario">
    {apertura("git show " + n.hash[:7], f"{n.parole} parole, ~{n.minuti} min")}{avviso}
    {prompt("git show " + n.hash[:7], "~/diario")}
    <dl class="commit">
      <div><dt>commit</dt><dd class="log-hash">{n.hash}</dd></div>
      <div><dt>Author:</dt><dd>{AUTORE}</dd></div>
      <div><dt>Date:</dt><dd><time datetime="{istante(n)}">{data_lunga(n.data)}{", ore " + n.ora if n.ora else ""}</time></dd></div>
      <div><dt>Ramo:</dt><dd><a class="ref-ramo" href="/diario/{ramo}/">{ramo}</a> <span class="commento"># {e(descr_ramo)}</span></dd></div>{riga_tag}
      <div><dt>Lettura:</dt><dd>~{n.minuti} min</dd></div>
    </dl>

    <article class="nota" aria-labelledby="t-nota">
      <h1 id="t-nota" class="nota-titolo">{e(n.titolo)}</h1>{copertina}
{n.html}
    </article>
{vicini_html}

    {prompt('cd .. <span class="cursore"></span>', "~/diario")}
    <p class="azioni"><a class="bottone bottone-linea" href="/diario/"><span aria-hidden="true">cd </span>~/diario</a></p>
  </main>

{piede_diario("diario/" + n.file)}
</body>
</html>
"""


def blocco_diario(t: dict, note) -> str:
    """Sezione in home con gli ultimi tre post (solo se ce ne sono)."""
    if not note:
        return ""
    voci = "\n".join(
        f'        <li><a href="/diario/{n.slug}/" lang="it"><span class="log-hash" aria-hidden="true">{n.hash[:7]}</span>'
        f'<span class="vic-titolo">{e(n.titolo)}</span>'
        f'<time class="commento" datetime="{n.data.isoformat()}">{n.data.day} {MESI[t["lang"]][n.data.month - 1]}</time></a></li>'
        for n in note[:3])
    return f"""
    <section class="blocco" id="diario" aria-labelledby="t-dia">
      {salto(t, "diario")}
      <h2 id="t-dia" class="titolo"><span class="hash" aria-hidden="true">## </span>{e(t["dia_titolo"])}</h2>
      <p class="commento"><span aria-hidden="true"># </span>{e(t["dia_intro"] + t["dia_nota"])}</p>
      {prompt("git log --oneline -3", "~/diario")}
      <ul class="vicini oneline">
{voci}
      </ul>
      <p class="azioni"><a class="bottone bottone-linea" href="/diario/"><span aria-hidden="true">cd </span>~/diario<span class="visivamente-nascosto">: {e(t["dia_tutto"])}</span></a></p>
    </section>"""


def assoluti(html: str, url: str) -> str:
    """Nei lettori RSS i link /... e #... non funzionano: diventano indirizzi completi."""
    return (html.replace('href="/', f'href="{SITE}/').replace('src="/', f'src="{SITE}/')
            .replace('href="#', f'href="{url}#'))


def feed(note: list) -> str:
    """Feed Atom: per chi legge con un lettore RSS."""
    def quando(n):
        return istante(n) if n.ora else f"{n.data.isoformat()}T08:00:00{fuso_roma(n.data)}"
    aggiornato = quando(note[0]) if note else "2026-11-12T08:00:00+01:00"
    voci = []
    for n in note:
        url = f"{SITE}/diario/{n.slug}/"
        categorie = "".join(f'\n    <category term="{e(x)}"/>' for x in (n.tipo,) + n.tag)
        voci.append(f"""  <entry>
    <title>{e(n.titolo)}</title>
    <link rel="alternate" type="text/html" href="{url}"/>
    <id>{url}</id>
    <published>{quando(n)}</published>
    <updated>{quando(n)}</updated>{categorie}
    <summary>{e(n.sommario)}</summary>
    <content type="html">{e(assoluti(n.html, url))}</content>
  </entry>""")
    return f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="it">
  <title>Diario di MDEANGELIS</title>
  <subtitle>{e(DIARIO_INTRO)}</subtitle>
  <link rel="alternate" type="text/html" href="{SITE}/diario/"/>
  <link rel="self" type="application/atom+xml" href="{SITE}/diario/feed.xml"/>
  <id>{SITE}/diario/</id>
  <updated>{aggiornato}</updated>
  <author><name>{AUTORE}</name><uri>{SITE}/</uri></author>
  <generator>genera.py + nota v{nota.VERSIONE}</generator>
{chr(10).join(voci)}
</feed>
"""


def sitemap(note: list) -> str:
    alt = ('\n    <xhtml:link rel="alternate" hreflang="it" href="{s}/"/>'
           '\n    <xhtml:link rel="alternate" hreflang="en" href="{s}/en/"/>').format(s=SITE)
    url = [f"  <url>\n    <loc>{SITE}/</loc>{alt}\n  </url>",
           f"  <url>\n    <loc>{SITE}/en/</loc>{alt}\n  </url>",
           f"  <url>\n    <loc>{SITE}/diario/</loc>\n  </url>"]
    url += [f"  <url>\n    <loc>{SITE}/diario/{n.slug}/</loc>\n    <lastmod>{n.data.isoformat()}</lastmod>\n  </url>"
            for n in note if not n.bozza]
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(url) + "\n</urlset>\n")


def scrivi(percorso: Path, testo: str) -> None:
    percorso.parent.mkdir(parents=True, exist_ok=True)
    percorso.write_text(testo, encoding="utf-8")


def main() -> None:
    # Le bozze si vedono solo nelle anteprime di Vercel (o con DIARIO_BOZZE=1 in locale).
    bozze = os.environ.get("VERCEL_ENV") == "preview" or os.environ.get("DIARIO_BOZZE") == "1"
    note = carica_diario(bozze)           # prima di scrivere qualsiasi file
    pubblicate = [n for n in note if not n.bozza]

    scrivi(OUT / "index.html", pagina(TESTI["it"], pubblicate))
    scrivi(OUT / "en" / "index.html", pagina(TESTI["en"], pubblicate))
    scrivi(OUT / "404.html", pagina_404())

    cartella = OUT / "diario"
    if cartella.exists():                 # via le pagine dei post cancellati o rinominati
        shutil.rmtree(cartella)
    scrivi(cartella / "index.html", pagina_indice(note, note))
    for tipo, (ramo, _) in RAMI.items():
        scrivi(cartella / ramo / "index.html",
               pagina_indice([n for n in note if n.tipo == tipo], note, ramo))
    for i, n in enumerate(note):
        piu_nuovo = note[i - 1] if i > 0 else None
        piu_vecchio = note[i + 1] if i + 1 < len(note) else None
        scrivi(cartella / n.slug / "index.html", pagina_post(n, piu_nuovo, piu_vecchio))
    scrivi(cartella / "feed.xml", feed(pubblicate))
    for nome in sorted({m for n in note for m in n.media}):   # solo i file usati, già ripuliti
        destinazione = cartella / "media" / nome
        destinazione.parent.mkdir(parents=True, exist_ok=True)
        destinazione.write_bytes(MEDIA[nome].dati)
    scrivi(OUT / "sitemap.xml", sitemap(note))

    bozze_txt = f", {len(note) - len(pubblicate)} bozze" if bozze else ""
    print(f"Pagine generate in {OUT}: {len(pubblicate)} post{bozze_txt}")


if __name__ == "__main__":
    main()
