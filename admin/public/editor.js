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
    const um = $("elenco-media");
    um.replaceChildren();
    for (const m of dati.media) {
      um.append(voce(m.nome, Math.max(1, Math.round(m.dimensione / 1024)) + " KB", "inserisci",
        () => inserisci("![descrivi cosa si vede](" + m.nome + ")"), false));
    }
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
    if (!aperto()) return;
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

  $("carica").addEventListener("change", async (ev) => {
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
    caricaElenco();
    if (aperto()) {
      inserisci(dati.tipo === "audio" ? "![titolo del brano](" + nome + ")" : "![descrivi cosa si vede](" + nome + ")");
    }
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
    immagine: () => $("carica").click(),
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
    const scorciatoie = { b: "grassetto", i: "corsivo", u: "sottolineato", k: "link" };
    if (scorciatoie[k]) {
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
