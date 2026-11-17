// Editor del diario di mdeangelis.me. Nessuna libreria: solo il browser.
// Tutto passa da /api/editor, che controlla l'accesso a ogni richiesta.
"use strict";

(function () {
  const $ = (id) => document.getElementById(id);
  const API = "/api/editor?a=";

  // L'anteprima arriva dal server già generata dall'interprete del sito, che
  // ammette solo una lista chiusa di tag. Trusted Types (dove c'è) obbliga a
  // passare da qui per qualsiasi innerHTML.
  const politica = window.trustedTypes
    ? window.trustedTypes.createPolicy("editor", { createHTML: (s) => s })
    : { createHTML: (s) => s };

  // Un post si apre in coppia: italiano e (se c'è) traduzione inglese, affiancati.
  const docs = {
    it: { el: $("testo-it"), etichetta: $("file-it"), nome: null, sha: null, salvato: "" },
    en: { el: $("testo-en"), etichetta: $("file-en"), nome: null, sha: null, salvato: "" },
  };
  const stato = {
    attivo: "it",        // la colonna dove stai scrivendo: barra e anteprima lavorano lì
    nomi: new Set(),     // file che esistono già nel repository
    attesa: null,        // timer dell'anteprima automatica
    controllo: null,     // timer del controllo "è online?"
  };

  let testo = docs.it.el;   // la textarea attiva (la usano barra, media e anteprima)
  const vista = $("vista");

  function avvisa(msg, tipo) {
    const s = $("stato");
    s.textContent = msg;
    s.dataset.tipo = tipo || "";
  }

  async function chiama(azione, corpo, extra) {
    const opzioni = corpo === undefined ? {} : {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(corpo),
    };
    let r;
    try {
      r = await fetch(API + azione + (extra || ""), { credentials: "same-origin", ...opzioni });
    } catch (e) {
      throw new Error("rete non raggiungibile");
    }
    if (r.status === 401) {
      avvisa("sessione scaduta: ricarico la pagina per rifare l'accesso…", "errore");
      setTimeout(() => location.reload(), 1500);
      throw new Error("accesso scaduto");
    }
    let dati = {};
    try { dati = await r.json(); } catch (e) { /* risposta vuota */ }
    dati.stato = r.status;
    return dati;
  }

  // un documento "esiste" se è aperto e o è già salvato o c'è del testo da salvare
  function inUso(d) { return d.nome !== null && (d.sha !== null || d.el.value !== ""); }
  function modificatoDoc(d) { return d.nome !== null && d.el.value !== d.salvato; }
  function modificato() { return modificatoDoc(docs.it) || modificatoDoc(docs.en); }
  function aperto() { return docs.it.nome !== null; }

  function attiva(l) {
    if (docs[l].el.disabled) return;
    stato.attivo = l;
    testo = docs[l].el;
    for (const k of ["it", "en"]) docs[k].el.closest(".ed-colonna").classList.toggle("ed-attiva-col", k === l);
  }

  function aggiornaBottoni() {
    const ok = aperto();
    const enInUso = inUso(docs.en);
    docs.it.el.disabled = !ok;
    docs.en.el.disabled = !ok || !enInUso;
    $("crea-en").hidden = !ok || enInUso;
    $("b-salva").disabled = !ok || !(modificato() || docs.it.sha === null);
    $("b-anteprima").disabled = !ok;
    for (const k of ["it", "en"]) {
      const d = docs[k];
      d.etichetta.textContent = d.nome === null ? "—"
        : d.nome + (inUso(d) ? (modificatoDoc(d) ? " [modificato]" : "") : " (non ancora creata)");
    }
    $("file-aperto").textContent = ok
      ? docs.it.nome.replace(/\.nota$/, "") + (modificato() ? " [modificato]" : "")
      : "nessun file aperto";
    if (testo.disabled) attiva("it");
  }

  // ------------------------------------------------------------ elenco

  function voce(nomeTesto, dettaglio, etichetta, azione, attivo) {
    const li = document.createElement("li");
    const b = document.createElement("button");
    b.type = "button";
    b.className = "ed-voce" + (attivo ? " ed-attiva" : "");
    const t = document.createElement("span");
    t.className = "ed-voce-titolo";
    t.textContent = nomeTesto;
    const d = document.createElement("span");
    d.className = "ed-voce-info";
    d.textContent = dettaglio;
    b.append(t, d);
    if (etichetta) {
      const e = document.createElement("span");
      e.className = "ed-etichetta";
      e.textContent = etichetta;
      b.append(e);
    }
    b.addEventListener("click", azione);
    li.append(b);
    return li;
  }

  async function caricaElenco() {
    const dati = await chiama("elenco");
    const ul = $("elenco-post");
    ul.replaceChildren();
    if (dati.stato !== 200) {
      ul.append(Object.assign(document.createElement("li"), { className: "ed-vuoto", textContent: dati.errore || "errore" }));
      return;
    }
    stato.nomi = new Set(dati.post.map((p) => p.nome));
    const en = new Map(dati.post.filter((p) => p.lingua === "en").map((p) => [p.nome.replace(/\.en\.nota$/, ".nota"), p]));
    for (const p of dati.post.filter((x) => x.lingua !== "en")) {
      const t = en.get(p.nome);
      const lingue = t ? (t.bozza ? " · EN in bozza" : " · EN") : "";
      ul.append(voce(p.titolo, p.data + (p.ora ? " " + p.ora : "") + " · " + p.tipo + lingue,
        p.bozza ? "bozza" : "", () => apri(p.nome), p.nome === docs.it.nome));
    }
    if (!dati.post.length) {
      ul.append(Object.assign(document.createElement("li"), { className: "ed-vuoto", textContent: "nessun post" }));
    }
    stato.media = dati.media;
    stato.titoli = Object.fromEntries(dati.post.map((p) => [p.nome, p.titolo]));
    $("n-media").textContent = "(" + dati.media.length + ")";
    if ($("d-media").open) disegnaGalleria();
  }

  // ------------------------------------------------------------ apri, nuovo

  function lasciare() {
    return !modificato() || confirm("Ci sono modifiche non salvate. Le perdi?");
  }

  function imposta(l, nome, sha, contenuto) {
    const d = docs[l];
    d.nome = nome; d.sha = sha; d.salvato = contenuto; d.el.value = contenuto;
  }

  async function apri(nome) {
    if (!lasciare()) return;
    const it = nome.replace(/\.en\.nota$/, ".nota");
    const en = it.replace(/\.nota$/, ".en.nota");
    avvisa("apro " + it + "…");
    const dati = await chiama("post", undefined, "&nome=" + encodeURIComponent(it));
    if (dati.stato !== 200) { avvisa(dati.errore || "non riesco ad aprirlo", "errore"); return; }
    imposta("it", dati.nome, dati.sha, dati.testo);
    imposta("en", en, null, "");
    if (stato.nomi.has(en)) {
      const t = await chiama("post", undefined, "&nome=" + encodeURIComponent(en));
      if (t.stato === 200) imposta("en", t.nome, t.sha, t.testo);
    }
    $("riga-nome").hidden = true;
    attiva(nome.endsWith(".en.nota") ? "en" : "it");
    aggiornaBottoni();
    caricaElenco();
    avvisa("aperto " + it + (docs.en.sha ? " con la traduzione inglese" : ""));
    anteprima();
  }

  function slug(s) {
    return s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase()
      .replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 50).replace(/-+$/, "") || "post";
  }

  function oggiRoma() {
    const parti = new Intl.DateTimeFormat("en-CA", {
      timeZone: "Europe/Rome", year: "numeric", month: "2-digit", day: "2-digit",
      hour: "2-digit", minute: "2-digit", hourCycle: "h23",
    }).formatToParts(new Date());
    const p = Object.fromEntries(parti.map((x) => [x.type, x.value]));
    return { data: p.year + "-" + p.month + "-" + p.day, ora: p.hour + ":" + p.minute };
  }

  function nuovoPost() {
    if (!lasciare()) return;
    const d = $("d-nuovo");
    $("n-titolo").value = "";
    $("n-nome").value = "";
    $("n-nome").dataset.toccato = "";
    d.showModal();
    $("n-titolo").focus();
  }

  $("n-titolo").addEventListener("input", () => {
    if (!$("n-nome").dataset.toccato) {
      $("n-nome").value = oggiRoma().data + "-" + slug($("n-titolo").value) + ".nota";
    }
  });
  $("n-nome").addEventListener("input", () => { $("n-nome").dataset.toccato = "1"; });
  $("n-annulla").addEventListener("click", () => $("d-nuovo").close());

  $("f-nuovo").addEventListener("submit", async (ev) => {
    const nome = $("n-nome").value.trim();
    if (!/^\d{4}-\d{2}-\d{2}-[a-z0-9]+(-[a-z0-9]+)*\.nota$/.test(nome)) {
      ev.preventDefault();
      avvisa("nome del file: AAAA-MM-GG-titolo-breve.nota, solo minuscole, cifre e trattini", "errore");
      return;
    }
    const t = oggiRoma();
    const titolo = $("n-titolo").value.trim().replace(/\s+/g, " ");
    const dati = await chiama("nuovo", { titolo: titolo, data: nome.slice(0, 10), ora: t.ora });
    imposta("it", nome, null, "");
    docs.it.el.value = dati.testo || "";
    imposta("en", nome.replace(/\.nota$/, ".en.nota"), null, "");
    $("riga-nome").hidden = false;
    $("nome-file").value = nome;
    attiva("it");
    aggiornaBottoni();
    docs.it.el.focus();
    avvisa("nuovo post, non ancora salvato");
    anteprima();
  });

  $("nome-file").addEventListener("change", () => {
    if (docs.it.sha === null) {
      docs.it.nome = $("nome-file").value.trim();
      docs.en.nome = docs.it.nome.replace(/\.nota$/, ".en.nota");
      aggiornaBottoni();
      anteprima();
    }
  });

  // ------------------------------------------------------------ traduzione inglese

  // nuova traduzione: copia del testo italiano, in bozza, da sostituire con l'inglese
  $("b-crea-en").addEventListener("click", () => {
    if (!aperto()) return;
    const copia = docs.it.el.value.replace(/\r\n/g, "\n");
    const fine = copia.indexOf("\n---");
    let testa = fine === -1 ? copia : copia.slice(0, fine);
    const corpo = fine === -1 ? "" : copia.slice(fine);
    testa = /^bozza:/m.test(testa) ? testa.replace(/^bozza:.*$/m, "bozza: si") : testa + "\nbozza: si";
    docs.en.el.value = testa + corpo;
    mostraColonna("en", true);
    aggiornaBottoni();
    attiva("en");
    docs.en.el.focus();
    docs.en.el.setSelectionRange(0, 0);
    avvisa("traduzione inglese creata in bozza: sostituisci il testo italiano con l'inglese e salva");
    anteprima();
  });

  // ------------------------------------------------------------ colonne visibili

  function mostraColonna(col, si) {
    const b = document.querySelector('.ed-vista-btn[data-col="' + col + '"]');
    b.setAttribute("aria-pressed", String(si));
    document.querySelector('#area [data-col="' + col + '"]').hidden = !si;
    const visibili = [...document.querySelectorAll("#area > [data-col]")].filter((x) => !x.hidden).length;
    $("area").dataset.colonne = String(Math.max(1, visibili));
  }

  for (const b of document.querySelectorAll(".ed-vista-btn")) {
    b.addEventListener("click", () => {
      const si = b.getAttribute("aria-pressed") !== "true";
      const accese = [...document.querySelectorAll('.ed-vista-btn[aria-pressed="true"]')].length;
      if (!si && accese <= 1) return;   // almeno una colonna resta
      mostraColonna(b.dataset.col, si);
      if (b.dataset.col === "vista" && si) anteprima();
    });
  }

  // ------------------------------------------------------------ anteprima

  function mostraErrore(dati, l) {
    const p = document.createElement("p");
    p.className = "ed-errore";
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = (l === "en" ? "EN " : "") + (dati.riga ? "riga " + dati.riga : "errore");
    b.addEventListener("click", () => vaiARiga(dati.riga, l));
    p.append(b, document.createTextNode(" " + (dati.errore || "errore")));
    vista.replaceChildren(p);
    mostraColonna("vista", true);
  }

  function vaiARiga(n, l) {
    if (!n) return;
    attiva(l || stato.attivo);
    mostraColonna(stato.attivo, true);
    const righe = testo.value.split("\n");
    let pos = 0;
    for (let i = 0; i < n - 1 && i < righe.length; i++) pos += righe[i].length + 1;
    testo.focus();
    testo.setSelectionRange(pos, pos + (righe[n - 1] || "").length);
    const alto = (n - 3) * parseFloat(getComputedStyle(testo).lineHeight || "20");
    testo.scrollTop = Math.max(0, alto);
  }

  async function anteprima() {
    if (!aperto() || stato.inModifica) return;
    clearTimeout(stato.attesa);
    const l = inUso(docs[stato.attivo]) ? stato.attivo : "it";
    const d = docs[l];
    const dati = await chiama("anteprima", { nome: d.nome, testo: d.el.value });
    if (dati.stato !== 200) { mostraErrore({ errore: dati.errore }, l); return false; }
    if (!dati.ok) {
      mostraErrore(dati, l);
      avvisa("c'è un errore " + (l === "en" ? "nell'inglese " : "") + "alla riga " + dati.riga, "errore");
      return false;
    }

    const art = document.createElement("article");
    art.className = "nota";
    art.lang = l;
    const testa = document.createElement("header");
    testa.className = "ed-testa-anteprima";
    const h1 = document.createElement("h1");
    h1.className = "nota-titolo";
    h1.textContent = dati.titolo;
    const meta = document.createElement("p");
    meta.className = "ed-meta";
    meta.textContent = l.toUpperCase() + " · " + dati.data + (dati.ora ? " " + dati.ora : "") + " · " + dati.tipo +
      " · " + dati.minuti + " min" + (dati.tag.length ? " · #" + dati.tag.join(" #") : "") +
      (dati.bozza ? " · BOZZA (non pubblicato)" : " · si pubblica al salvataggio");
    testa.append(h1, meta);
    const corpo = document.createElement("div");
    corpo.innerHTML = politica.createHTML(dati.html);
    if (dati.copertina) {
      const f = document.createElement("figure");
      f.className = "nota-copertina";
      const img = document.createElement("img");
      img.src = "/diario/media/" + encodeURIComponent(dati.copertina);
      img.alt = "";
      f.append(img);
      art.append(testa, f);
    } else {
      art.append(testa);
    }
    art.append(...corpo.childNodes);
    // i link dell'anteprima non devono portare via dall'editor
    for (const a of art.querySelectorAll("a[href]")) {
      const h = a.getAttribute("href");
      if (!h.startsWith("#")) { a.target = "_blank"; a.rel = "noopener noreferrer"; }
    }
    vista.replaceChildren(art);
    vista.dataset.lingua = l;
    for (const blocco of art.querySelectorAll("[data-riga]")) {
      blocco.classList.add("ed-modificabile");
      blocco.title = "clic per modificare qui (Invio conferma, Esc annulla)";
      for (const s of blocco.querySelectorAll(".spunta")) s.contentEditable = "false";
    }
    // non coprire il messaggio di un salvataggio appena fatto
    if (!modificato() && $("stato").dataset.tipo !== "ok") avvisa("nessun errore");
    return true;
  }

  for (const l of ["it", "en"]) {
    const el = docs[l].el;
    el.addEventListener("focus", () => {
      if (stato.attivo !== l) { attiva(l); anteprima(); }
    });
    el.addEventListener("input", () => {
      aggiornaBottoni();
      clearTimeout(stato.attesa);
      stato.attesa = setTimeout(anteprima, 1500);
    });
  }

  // ------------------------------------------------------------ salva

  async function salvaDoc(l) {
    const d = docs[l];
    const contenuto = d.el.value;
    const dati = await chiama("salva", { nome: d.nome, testo: contenuto, sha: d.sha });
    if (!dati.ok) {
      if (dati.riga !== undefined) mostraErrore(dati, l);
      avvisa("non salvato" + (l === "en" ? " (inglese)" : "") + ": " + (dati.errore || "errore")
        + (dati.riga ? " (riga " + dati.riga + ")" : ""), "errore");
      return null;
    }
    d.sha = dati.sha;
    d.salvato = contenuto;
    return dati;
  }

  async function salva() {
    if (!aperto()) return;
    $("b-salva").disabled = true;
    avvisa("controllo e salvo…");
    // prima l'italiano: la traduzione ha bisogno che esista (e sia pubblicato, se la pubblichi)
    const fatti = [];
    for (const l of ["it", "en"]) {
      const d = docs[l];
      const daSalvare = l === "it" ? (modificatoDoc(d) || d.sha === null) : (inUso(d) && modificatoDoc(d));
      if (!daSalvare) continue;
      const dati = await salvaDoc(l);
      if (!dati) { aggiornaBottoni(); return; }
      fatti.push([l, dati]);
    }
    $("riga-nome").hidden = true;
    aggiornaBottoni();
    caricaElenco();
    const online = fatti.filter(([, x]) => !x.bozza);
    const cosa = fatti.map(([l]) => l.toUpperCase()).join(" e ");
    if (!fatti.length) {
      avvisa("niente da salvare");
    } else if (!online.length) {
      avvisa("salvato " + cosa + " come bozza: non è online", "ok");
    } else {
      avvisa("salvato " + cosa + ": il sito si aggiorna in circa un minuto…", "ok");
      const [l, x] = online[online.length - 1];
      controllaOnline(docs[l].nome, x.indirizzo, 0);
    }
  }

  function controllaOnline(nome, indirizzo, giri) {
    clearTimeout(stato.controllo);
    stato.controllo = setTimeout(async () => {
      const dati = await chiama("stato", undefined, "&nome=" + encodeURIComponent(nome));
      if (dati.online && giri >= 3) {
        const s = $("stato");
        s.replaceChildren(document.createTextNode("online: "));
        const a = document.createElement("a");
        a.href = indirizzo; a.target = "_blank"; a.rel = "noopener noreferrer";
        a.textContent = indirizzo;
        s.append(a);
        s.dataset.tipo = "ok";
      } else if (giri < 18) {
        controllaOnline(nome, indirizzo, giri + 1);
      } else {
        avvisa("la pubblicazione ci sta mettendo più del solito: controlla la build su Vercel", "errore");
      }
    }, 10000);
  }

  // ------------------------------------------------------------ media

  function inserisci(s) {
    if (!aperto()) { avvisa("apri prima un post", "errore"); return; }
    const i = testo.selectionStart;
    const prima = testo.value.slice(0, i);
    const a_capo = prima && !prima.endsWith("\n") ? "\n\n" : "";
    testo.setRangeText(a_capo + s + "\n", i, testo.selectionEnd, "end");
    testo.focus();
    testo.dispatchEvent(new Event("input"));
  }

  function nomeMedia(file, estensione) {
    const base = file.name.replace(/\.[^.]*$/, "");
    return slug(base).slice(0, 50) + "." + estensione;
  }

  // Foto grandi: ridimensionate nel browser a 2000 pixel sul lato lungo (WebP).
  // Ridisegnarle sulla tela toglie anche tutti i metadati.
  async function riduci(file) {
    const bmp = await createImageBitmap(file, { imageOrientation: "from-image" });
    const scala = Math.min(1, 2000 / Math.max(bmp.width, bmp.height));
    const tela = document.createElement("canvas");
    tela.width = Math.round(bmp.width * scala);
    tela.height = Math.round(bmp.height * scala);
    tela.getContext("2d").drawImage(bmp, 0, 0, tela.width, tela.height);
    bmp.close();
    return await new Promise((ok) => tela.toBlob(ok, "image/webp", 0.85));
  }

  function base64(blob) {
    return new Promise((ok, ko) => {
      const r = new FileReader();
      r.onload = () => ok(String(r.result).split(",")[1]);
      r.onerror = ko;
      r.readAsDataURL(blob);
    });
  }

  async function caricaFile(ev) {
    const file = ev.target.files[0];
    ev.target.value = "";
    if (!file) return;
    const LIMITE = 3000000;
    let blob = file;
    let est = (file.name.split(".").pop() || "").toLowerCase();
    if (est === "jpeg") est = "jpg";
    try {
      if (file.type.startsWith("image/") && file.type !== "image/gif" && file.size > LIMITE) {
        avvisa("riduco la foto…");
        blob = await riduci(file);
        est = "webp";
      }
    } catch (e) {
      avvisa("non riesco a ridurre questa foto: riducila prima di caricarla", "errore");
      return;
    }
    if (blob.size > LIMITE) {
      avvisa("file troppo grande: massimo 3 MB per il caricamento", "errore");
      return;
    }
    const nome = nomeMedia(file, est);
    avvisa("carico " + nome + "…");
    const dati = await chiama("carica", { nome: nome, dati: await base64(blob) });
    if (!dati.ok) { avvisa("non caricato: " + (dati.errore || "errore"), "errore"); return; }
    avvisa("caricato " + nome + " (pulito dai metadati)", "ok");
    stato.scelto = nome;
    await caricaElenco();
    // dalla galleria resta lì per sceglierlo; dalla barra laterale va subito nel testo
    if (ev.target.id === "carica" && aperto()) {
      inserisci(dati.tipo === "audio" ? "![titolo del brano](" + nome + ")" : "![descrivi cosa si vede](" + nome + ")");
    }
  }
  $("carica").addEventListener("change", caricaFile);
  $("carica-g").addEventListener("change", caricaFile);

  // ------------------------------------------------------------ galleria dei media

  stato.media = [];
  stato.scelto = null;

  function kb(n) { return n >= 1048576 ? (n / 1048576).toFixed(1) + " MB" : Math.max(1, Math.round(n / 1024)) + " KB"; }

  function disegnaGalleria() {
    const cerca = $("g-cerca").value.trim().toLowerCase();
    const tipo = $("g-tipo").value, uso = $("g-uso").value;
    const ul = $("g-griglia");
    ul.replaceChildren();
    const visibili = stato.media.filter((m) =>
      (!cerca || m.nome.includes(cerca)) && (!tipo || m.tipo === tipo) &&
      (!uso || (uso === "usati") === (m.usato_da.length > 0)));
    for (const m of visibili) {
      const li = document.createElement("li");
      const b = document.createElement("button");
      b.type = "button";
      b.className = "ed-miniatura" + (stato.scelto === m.nome ? " ed-attiva" : "");
      b.title = m.nome;
      if (m.tipo === "immagine") {
        const img = document.createElement("img");
        img.src = "/diario/media/" + encodeURIComponent(m.nome);
        img.alt = "";
        img.loading = "lazy";
        img.decoding = "async";
        b.append(img);
      } else {
        const s = document.createElement("span");
        s.className = "ed-audio-icona";
        s.textContent = "♪";
        b.append(s);
      }
      const n = document.createElement("span");
      n.className = "ed-miniatura-nome";
      n.textContent = m.nome;
      const info = document.createElement("span");
      info.className = "ed-miniatura-info";
      info.textContent = kb(m.dimensione) + (m.usato_da.length ? " · in " + m.usato_da.length + " post" : " · non usato");
      b.append(n, info);
      b.addEventListener("click", () => { stato.scelto = m.nome; disegnaGalleria(); });
      li.append(b);
      ul.append(li);
    }
    if (!visibili.length) {
      ul.append(Object.assign(document.createElement("li"), { className: "ed-vuoto",
        textContent: stato.media.length ? "nessun file con questi filtri" : "nessun file caricato" }));
    }
    dettaglio(stato.media.find((m) => m.nome === stato.scelto));
  }

  function dettaglio(m) {
    const box = $("g-dettaglio");
    box.replaceChildren();
    if (!m) {
      box.append(Object.assign(document.createElement("p"), { className: "ed-vuoto", textContent: "Scegli un file per vederlo qui." }));
      return;
    }
    const src = "/diario/media/" + encodeURIComponent(m.nome);
    const misure = document.createElement("p");
    misure.className = "ed-meta";
    misure.textContent = m.tipo + " · " + kb(m.dimensione);
    if (m.tipo === "immagine") {
      const img = document.createElement("img");
      img.src = src; img.alt = ""; img.className = "ed-dettaglio-img";
      img.addEventListener("load", () => {
        misure.textContent = "immagine · " + img.naturalWidth + "×" + img.naturalHeight + " px · " + kb(m.dimensione);
      });
      box.append(img);
    } else {
      const a = document.createElement("audio");
      a.src = src; a.controls = true; a.preload = "none";
      box.append(a);
    }
    const h = document.createElement("h3");
    h.textContent = m.nome;
    box.append(h, misure);

    const azioni = document.createElement("div");
    azioni.className = "ed-bottoni";
    const ins = document.createElement("button");
    ins.type = "button";
    ins.className = "ed-primario";
    ins.textContent = "inserisci nel testo";
    ins.disabled = !aperto();
    ins.addEventListener("click", () => {
      $("d-media").close();
      inserisci(m.tipo === "audio" ? "![titolo del brano](" + m.nome + ")" : "![descrivi cosa si vede](" + m.nome + ")");
    });
    azioni.append(ins);
    if (m.tipo === "immagine") {
      const cop = document.createElement("button");
      cop.type = "button";
      cop.textContent = "usa come copertina";
      cop.disabled = !aperto();
      cop.addEventListener("click", () => { $("d-media").close(); copertina(m.nome); });
      azioni.append(cop);
    }
    box.append(azioni);

    const uso = document.createElement("p");
    uso.className = "ed-nota-piccola";
    if (!m.usato_da.length) {
      uso.textContent = "Non è usato da nessun post: online non va finché un post non lo usa.";
      box.append(uso);
    } else {
      uso.textContent = "Usato in:";
      const ul = document.createElement("ul");
      ul.className = "ed-usato";
      for (const p of m.usato_da) {
        const li = document.createElement("li");
        const b = document.createElement("button");
        b.type = "button";
        b.className = "ed-link";
        b.textContent = (p.endsWith(".en.nota") ? "EN · " : "") + (stato.titoli[p] || p);
        b.addEventListener("click", () => { $("d-media").close(); apri(p); });
        li.append(b);
        ul.append(li);
      }
      box.append(uso, ul);
    }
  }

  // copertina: nell'intestazione del testo attivo (sostituisce quella che c'è)
  function copertina(nome) {
    if (!aperto()) return;
    const v = testo.value;
    const fine = v.indexOf("\n---");
    if (fine === -1) { avvisa("manca la riga --- che chiude l'intestazione", "errore"); return; }
    const testa = v.slice(0, fine);
    const m = /^copertina:.*$/m.exec(testa);
    if (m) {
      scrivi(m.index, m.index + m[0].length, "copertina: " + nome);
    } else {
      scrivi(fine, fine, "\ncopertina: " + nome);
    }
    avvisa("copertina: " + nome, "ok");
  }

  $("b-galleria").addEventListener("click", () => {
    disegnaGalleria();
    $("d-media").showModal();
    $("g-cerca").focus();
  });
  $("g-chiudi").addEventListener("click", () => $("d-media").close());
  for (const id of ["g-cerca", "g-tipo", "g-uso"]) $(id).addEventListener("input", disegnaGalleria);

  // ------------------------------------------------------------ modifica nell'anteprima
  // Paragrafi, titoletti e voci di elenco si possono correggere direttamente
  // nell'anteprima: al termine il blocco torna testo Nota e sostituisce le sue righe.

  stato.inModifica = null;

  function scappa(s) {
    return s.replace(/\\/g, "\\\\").replace(/([*_`\[\]])/g, "\\$1")
      .replace(/~~/g, "\\~\\~").replace(/==/g, "\\=\\=").replace(/\+\+/g, "\\+\\+");
  }

  function inNota(nodo) {
    let out = "";
    for (const n of nodo.childNodes) {
      if (n.nodeType === Node.TEXT_NODE) { out += scappa(n.nodeValue.replace(/ /g, " ")); continue; }
      if (n.nodeType !== Node.ELEMENT_NODE) continue;
      const tag = n.tagName.toLowerCase();
      if (n.classList.contains("spunta")) continue;
      const dentro = () => inNota(n);
      if (tag === "strong" || tag === "b") out += "*" + dentro() + "*";
      else if (tag === "em" || tag === "i") out += "_" + dentro() + "_";
      else if (tag === "u") out += "++" + dentro() + "++";
      else if (tag === "del" || tag === "s" || tag === "strike") out += "~~" + dentro() + "~~";
      else if (tag === "mark") out += "==" + dentro() + "==";
      else if (tag === "code") out += "`" + n.textContent + "`";
      else if (tag === "kbd") out += "[[" + n.textContent + "]]";
      else if (tag === "br") out += "\\\n";
      else if (tag === "sup" && n.classList.contains("rimando")) {
        const a = n.querySelector("a");
        const m = a && /^#nota-(.+)$/.exec(a.getAttribute("href") || "");
        if (m) out += "[^" + m[1] + "]";
      } else if (tag === "a") out += "[" + dentro() + "](" + (n.getAttribute("href") || "") + ")";
      else if (tag === "div" || tag === "p") out += (out ? " " : "") + dentro();
      else out += dentro();
    }
    return out;
  }

  function pulisci(s) {
    return s.split("\\\n").map((x) => x.replace(/\s+/g, " ").trim()).join("\\\n");
  }

  function iniziaModifica(blocco) {
    if (stato.inModifica) return;
    stato.inModifica = { blocco: blocco, prima: pulisci(inNota(blocco)), lingua: vista.dataset.lingua };
    blocco.contentEditable = "true";
    blocco.classList.add("ed-in-modifica");
    blocco.focus();
  }

  function fineModifica(conferma) {
    const m = stato.inModifica;
    if (!m) return;
    stato.inModifica = null;
    m.blocco.contentEditable = "false";
    m.blocco.classList.remove("ed-in-modifica");
    const dopo = pulisci(inNota(m.blocco));
    if (!conferma || dopo === m.prima) { anteprima(); return; }
    if (!dopo) { avvisa("blocco vuoto: per cancellarlo usa la colonna del testo", "errore"); anteprima(); return; }
    const d = docs[m.lingua];
    const [da, a] = m.blocco.dataset.riga.split("-").map(Number);
    const righe = d.el.value.split("\n");
    if (!(da >= 1 && a >= da && a <= righe.length)) { anteprima(); return; }
    const tag = m.blocco.tagName.toLowerCase();
    const prima = righe[da - 1];
    const pref = tag === "li" ? (/^(- \[[ xX]\] |- |\d{1,3}\. )/.exec(prima) || [""])[0]
      : (tag === "h2" || tag === "h3") ? (/^#{1,2} /.exec(prima) || [""])[0] : "";
    let inizio = 0;
    for (let i = 0; i < da - 1; i++) inizio += righe[i].length + 1;
    let fine = inizio;
    for (let i = da - 1; i < a; i++) fine += righe[i].length + (i < a - 1 ? 1 : 0);
    attiva(m.lingua);
    scrivi(inizio, fine, pref + dopo);
    avvisa("modificato dall'anteprima (righe " + da + (a > da ? "-" + a : "") + ")", "ok");
  }

  vista.addEventListener("click", (ev) => {
    const blocco = ev.target.closest(".ed-modificabile");
    if (stato.inModifica) {
      if (ev.target.closest("a")) ev.preventDefault();   // mentre scrivi i link non si aprono
      return;
    }
    if (!blocco || ev.ctrlKey || ev.metaKey) return;      // Ctrl+clic su un link lo apre
    ev.preventDefault();
    iniziaModifica(blocco);
  });
  vista.addEventListener("keydown", (ev) => {
    if (!stato.inModifica) return;
    if (ev.key === "Escape") { ev.preventDefault(); fineModifica(false); }
    else if (ev.key === "Enter" && !ev.shiftKey) { ev.preventDefault(); fineModifica(true); }
    else if ((ev.ctrlKey || ev.metaKey) && !ev.altKey) {
      const k = ev.key.toLowerCase();
      const cmd = { b: "bold", i: "italic", u: "underline" }[k];
      if (cmd) { ev.preventDefault(); document.execCommand(cmd); }
    }
  });
  vista.addEventListener("focusout", (ev) => {
    if (stato.inModifica && ev.target === stato.inModifica.blocco) fineModifica(true);
  });
  // incollando arriva solo testo, niente formattazione da altre pagine
  vista.addEventListener("paste", (ev) => {
    if (!stato.inModifica) return;
    ev.preventDefault();
    document.execCommand("insertText", false, (ev.clipboardData.getData("text/plain") || "").replace(/\s+/g, " "));
  });

  // ------------------------------------------------------------ traduzione della selezione

  stato.traduzione = null;

  function urlGoogle(testoDa, da, a) {
    return "https://translate.google.com/?sl=" + da + "&tl=" + a + "&op=translate&text=" + encodeURIComponent(testoDa);
  }

  async function traduciSelezione() {
    if (!aperto()) return;
    let sel = "", lingua = stato.attivo, origine = null;
    const dalTesto = document.activeElement === testo || !window.getSelection().toString().trim();
    if (dalTesto) {
      sel = testo.value.slice(testo.selectionStart, testo.selectionEnd);
      origine = { lingua: stato.attivo, a: testo.selectionStart, b: testo.selectionEnd };
    } else {
      sel = window.getSelection().toString();
      lingua = vista.dataset.lingua || stato.attivo;
    }
    if (!sel.trim()) { avvisa("seleziona prima il testo da tradurre", "errore"); return; }
    const verso = lingua === "en" ? ["en", "it"] : ["it", "en"];
    stato.traduzione = { testo: sel, da: verso[0], a: verso[1], origine: origine };
    avvisa("traduco…");
    const dati = await chiama("traduci", { testo: sel, da: verso[0], a: verso[1] });
    if (dati.stato === 501) {
      window.open(urlGoogle(sel, verso[0], verso[1]), "_blank", "noopener,noreferrer");
      avvisa("aperto Google Traduttore in un'altra scheda (la traduzione dentro l'editor non è ancora attiva)");
      return;
    }
    if (!dati.ok) { avvisa(dati.errore || "traduzione non riuscita", "errore"); return; }
    $("tr-verso").textContent = verso[0].toUpperCase() + " → " + verso[1].toUpperCase();
    $("tr-originale").textContent = sel.length > 300 ? sel.slice(0, 300) + "…" : sel;
    $("tr-testo").value = dati.testo;
    const altra = docs[verso[1]];
    $("tr-altra").disabled = !inUso(altra);
    $("tr-altra").textContent = "metti nella colonna " + verso[1].toUpperCase();
    $("tr-sostituisci").disabled = !origine;
    $("d-traduci").showModal();
    avvisa("tradotto con Google Translate", "ok");
  }

  $("tr-chiudi").addEventListener("click", () => $("d-traduci").close());
  $("tr-google").addEventListener("click", () => {
    const t = stato.traduzione;
    if (t) window.open(urlGoogle(t.testo, t.da, t.a), "_blank", "noopener,noreferrer");
  });
  $("tr-copia").addEventListener("click", async () => {
    try { await navigator.clipboard.writeText($("tr-testo").value); avvisa("traduzione copiata", "ok"); }
    catch (e) { $("tr-testo").select(); avvisa("premi Ctrl+C per copiare", "errore"); }
  });
  $("tr-sostituisci").addEventListener("click", () => {
    const t = stato.traduzione;
    if (!t || !t.origine) return;
    $("d-traduci").close();
    attiva(t.origine.lingua);
    scrivi(t.origine.a, t.origine.b, $("tr-testo").value);
  });
  $("tr-altra").addEventListener("click", () => {
    const t = stato.traduzione;
    if (!t) return;
    $("d-traduci").close();
    mostraColonna(t.a, true);
    attiva(t.a);
    scrivi(testo.selectionStart, testo.selectionEnd, $("tr-testo").value);
  });

  // ------------------------------------------------------------ barra di formattazione
  // Ogni bottone scrive la sintassi Nota (vedi diario/COME-SI-SCRIVE.md).

  function scrivi(inizio, fine, nuovo, selDa, selA) {
    testo.focus();
    testo.setSelectionRange(inizio, fine);
    // execCommand tiene Ctrl+Z funzionante; dove non c'è si ripiega su setRangeText
    if (!document.execCommand || !document.execCommand("insertText", false, nuovo)) {
      testo.setRangeText(nuovo, inizio, fine, "end");
      testo.dispatchEvent(new Event("input"));
    }
    if (selDa !== undefined) testo.setSelectionRange(inizio + selDa, inizio + selA);
  }

  function avvolgi(prima, dopo, segnaposto) {
    const a = testo.selectionStart, b = testo.selectionEnd;
    let sel = testo.value.slice(a, b);
    // gli spazi ai bordi restano fuori dai segni, altrimenti la formattazione non vale
    const sx = sel.length - sel.trimStart().length, dx = sel.length - sel.trimEnd().length;
    const interno = sel.trim() || segnaposto;
    const nuovo = sel.slice(0, sx) + prima + interno + dopo + (dx ? sel.slice(sel.length - dx) : "");
    scrivi(a, b, nuovo, sx + prima.length, sx + prima.length + interno.length);
  }

  function righeSelezionate() {
    const v = testo.value;
    const a = v.lastIndexOf("\n", testo.selectionStart - 1) + 1;
    let b = v.indexOf("\n", Math.max(testo.selectionEnd - (testo.selectionEnd > testo.selectionStart ? 1 : 0), a));
    if (b === -1) b = v.length;
    return { a: a, b: b, righe: v.slice(a, b).split("\n") };
  }

  function prefissa(fn) {
    const r = righeSelezionate();
    const nuovo = r.righe.map((riga, i) => fn(riga, i)).join("\n");
    scrivi(r.a, r.b, nuovo, nuovo.length, nuovo.length);
  }

  function blocco(contenuto, selDa, selA) {
    // un blocco (tabella, codice, riquadro...) sta tra due righe vuote
    const a = testo.selectionStart, b = testo.selectionEnd;
    const prima = testo.value.slice(0, a), dopo = testo.value.slice(b);
    const sopra = !prima ? "" : prima.endsWith("\n\n") ? "" : prima.endsWith("\n") ? "\n" : "\n\n";
    const sotto = dopo.startsWith("\n\n") ? "" : dopo.startsWith("\n") ? "\n" : "\n\n";
    const nuovo = sopra + contenuto + sotto;
    scrivi(a, b, nuovo, sopra.length + (selDa || 0), sopra.length + (selA === undefined ? contenuto.length : selA));
  }

  const FORMATI = {
    grassetto: () => avvolgi("*", "*", "grassetto"),
    corsivo: () => avvolgi("_", "_", "corsivo"),
    sottolineato: () => avvolgi("++", "++", "sottolineato"),
    barrato: () => avvolgi("~~", "~~", "barrato"),
    evidenziato: () => avvolgi("==", "==", "evidenziato"),
    tasto: () => avvolgi("[[", "]]", "Ctrl"),
    codice: () => {
      const sel = testo.value.slice(testo.selectionStart, testo.selectionEnd);
      if (sel.includes("\n")) {
        blocco("```\n" + sel + "\n```", 4, 4 + sel.length);
      } else {
        avvolgi("`", "`", "codice");
      }
    },
    titolo: () => prefissa((r) => "# " + r.replace(/^#{1,2} /, "")),
    sottotitolo: () => prefissa((r) => "## " + r.replace(/^#{1,2} /, "")),
    elenco: () => prefissa((r) => r.startsWith("- ") ? r.slice(2) : "- " + r),
    numerato: () => prefissa((r, i) => /^\d+\. /.test(r) ? r.replace(/^\d+\. /, "") : (i + 1) + ". " + r),
    spunta: () => prefissa((r) => r.startsWith("- [ ] ") ? r.slice(6) : "- [ ] " + r.replace(/^- /, "")),
    citazione: () => prefissa((r) => r.startsWith("> ") ? r.slice(2) : "> " + r),
    link: () => {
      const a = testo.selectionStart, b = testo.selectionEnd;
      const sel = testo.value.slice(a, b).trim() || "testo del link";
      const nuovo = "[" + sel + "](https://)";
      scrivi(a, b, nuovo, sel.length + 3, nuovo.length - 1);
    },
    immagine: () => $("b-galleria").click(),
    tabella: () => blocco(
      "| Colonna 1 | Colonna 2 | Colonna 3 |\n" +
      "|-----------|-----------|-----------|\n" +
      "| testo     | testo     | testo     |\n" +
      "| testo     | testo     | testo     |", 2, 11),
    nota: () => {
      let n = 1;
      while (testo.value.includes("[^" + n + "]")) n++;
      // il rimando va dove sei, la definizione in fondo al post: una sola modifica (un solo Ctrl+Z)
      const a = testo.selectionEnd;
      const resto = testo.value.slice(a).replace(/\s+$/, "");
      const rimando = "[^" + n + "]";
      const segnaposto = "testo della nota";
      const nuovo = rimando + resto + "\n\n" + rimando + ": " + segnaposto + "\n";
      const fine = nuovo.length - 1;
      scrivi(a, testo.value.length, nuovo, fine - segnaposto.length, fine);
    },
    linea: () => blocco("---", 3, 3),
    traduci: () => traduciSelezione(),
  };

  $("strumenti").addEventListener("click", (ev) => {
    const b = ev.target.closest("button[data-f]");
    if (!b || testo.disabled) return;
    FORMATI[b.dataset.f]();
  });

  $("riquadro").addEventListener("change", (ev) => {
    const tipo = ev.target.value;
    ev.target.value = "";
    if (!tipo || testo.disabled) return;
    const sel = testo.value.slice(testo.selectionStart, testo.selectionEnd).trim() || "Scrivi qui il testo del riquadro.";
    const corpo = sel.split("\n").map((r) => "> " + r).join("\n");
    blocco("> [!" + tipo + "]\n" + corpo, ("> [!" + tipo + "]\n> ").length, ("> [!" + tipo + "]\n").length + corpo.length);
  });

  for (const el of [docs.it.el, docs.en.el]) el.addEventListener("keydown", (ev) => {
    if (!(ev.ctrlKey || ev.metaKey) || ev.altKey) return;
    const k = ev.key.toLowerCase();
    if (ev.shiftKey && k === "t") { ev.preventDefault(); traduciSelezione(); return; }
    const scorciatoie = { b: "grassetto", i: "corsivo", u: "sottolineato", k: "link" };
    if (scorciatoie[k] && !ev.shiftKey) {
      ev.preventDefault();
      FORMATI[scorciatoie[k]]();
    }
  });

  // ------------------------------------------------------------ comandi

  $("b-nuovo").addEventListener("click", nuovoPost);
  $("b-anteprima").addEventListener("click", () => { mostraColonna("vista", true); anteprima(); });
  $("b-salva").addEventListener("click", salva);

  document.addEventListener("keydown", (ev) => {
    if ((ev.ctrlKey || ev.metaKey) && ev.key.toLowerCase() === "s") {
      ev.preventDefault();
      if (!$("b-salva").disabled) salva();
    } else if ((ev.ctrlKey || ev.metaKey) && ev.key === "Enter") {
      ev.preventDefault();
      anteprima();
    }
  });

  window.addEventListener("beforeunload", (ev) => {
    if (modificato()) { ev.preventDefault(); ev.returnValue = ""; }
  });

  // ------------------------------------------------------------ avvio

  (async function () {
    try {
      const io = await chiama("io");
      if (io.stato !== 200) { avvisa("accesso negato", "errore"); return; }
      $("chi").textContent = io.email.split("@")[0];
      await caricaElenco();
      avvisa("pronto");
    } catch (e) {
      avvisa(e.message, "errore");
    }
  })();
})();
