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

  const stato = {
    nome: null,          // file aperto
    sha: null,           // versione letta (null = post nuovo, mai salvato)
    salvato: "",         // testo all'ultimo salvataggio
    attesa: null,        // timer dell'anteprima automatica
    controllo: null,     // timer del controllo "è online?"
  };

  const testo = $("testo");
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

  function modificato() {
    return stato.nome !== null && testo.value !== stato.salvato;
  }

  function aggiornaBottoni() {
    const aperto = stato.nome !== null;
    $("b-salva").disabled = !aperto || (!modificato() && stato.sha !== null);
    $("b-anteprima").disabled = !aperto;
    testo.disabled = !aperto;
    $("file-aperto").textContent = aperto
      ? (stato.nome + (modificato() ? " [modificato]" : ""))
      : "nessun file aperto";
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
    for (const p of dati.post) {
      ul.append(voce(p.titolo, p.data + (p.ora ? " " + p.ora : "") + " · " + p.tipo,
        p.bozza ? "bozza" : "", () => apri(p.nome), p.nome === stato.nome));
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

  async function apri(nome) {
    if (!lasciare()) return;
    avvisa("apro " + nome + "…");
    const dati = await chiama("post", undefined, "&nome=" + encodeURIComponent(nome));
    if (dati.stato !== 200) { avvisa(dati.errore || "non riesco ad aprirlo", "errore"); return; }
    stato.nome = dati.nome;
    stato.sha = dati.sha;
    stato.salvato = dati.testo;
    testo.value = dati.testo;
    $("riga-nome").hidden = true;
    aggiornaBottoni();
    caricaElenco();
    avvisa("aperto " + nome);
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
    stato.nome = nome;
    stato.sha = null;
    stato.salvato = "";
    testo.value = dati.testo || "";
    $("riga-nome").hidden = false;
    $("nome-file").value = nome;
    aggiornaBottoni();
    testo.focus();
    avvisa("nuovo post, non ancora salvato");
    anteprima();
  });

  $("nome-file").addEventListener("change", () => {
    if (stato.sha === null) {
      stato.nome = $("nome-file").value.trim();
      aggiornaBottoni();
      anteprima();
    }
  });

  // ------------------------------------------------------------ anteprima

  function mostraErrore(dati) {
    const p = document.createElement("p");
    p.className = "ed-errore";
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = dati.riga ? "riga " + dati.riga : "errore";
    b.addEventListener("click", () => vaiARiga(dati.riga));
    p.append(b, document.createTextNode(" " + (dati.errore || "errore")));
    vista.replaceChildren(p);
  }

  function vaiARiga(n) {
    if (!n) return;
    mostraScheda("scrivi");
    const righe = testo.value.split("\n");
    let pos = 0;
    for (let i = 0; i < n - 1 && i < righe.length; i++) pos += righe[i].length + 1;
    testo.focus();
    testo.setSelectionRange(pos, pos + (righe[n - 1] || "").length);
    const alto = (n - 3) * parseFloat(getComputedStyle(testo).lineHeight || "20");
    testo.scrollTop = Math.max(0, alto);
  }

  async function anteprima() {
    if (stato.nome === null) return;
    clearTimeout(stato.attesa);
    const dati = await chiama("anteprima", { nome: stato.nome, testo: testo.value });
    if (dati.stato !== 200) { mostraErrore({ errore: dati.errore }); return false; }
    if (!dati.ok) { mostraErrore(dati); avvisa("c'è un errore alla riga " + dati.riga, "errore"); return false; }

    const art = document.createElement("article");
    art.className = "nota";
    const testa = document.createElement("header");
    testa.className = "ed-testa-anteprima";
    const h1 = document.createElement("h1");
    h1.className = "nota-titolo";
    h1.textContent = dati.titolo;
    const meta = document.createElement("p");
    meta.className = "ed-meta";
    meta.textContent = dati.data + (dati.ora ? " " + dati.ora : "") + " · " + dati.tipo +
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
    if (!modificato()) avvisa("nessun errore");
    return true;
  }

  testo.addEventListener("input", () => {
    aggiornaBottoni();
    clearTimeout(stato.attesa);
    stato.attesa = setTimeout(anteprima, 1500);
  });

  // ------------------------------------------------------------ salva

  async function salva() {
    if (stato.nome === null) return;
    $("b-salva").disabled = true;
    avvisa("controllo e salvo…");
    const testoOra = testo.value;
    const dati = await chiama("salva", { nome: stato.nome, testo: testoOra, sha: stato.sha });
    if (!dati.ok) {
      aggiornaBottoni();
      if (dati.riga !== undefined) mostraErrore(dati);
      avvisa("non salvato: " + (dati.errore || "errore") + (dati.riga ? " (riga " + dati.riga + ")" : ""), "errore");
      return;
    }
    stato.sha = dati.sha;
    stato.salvato = testoOra;
    $("riga-nome").hidden = true;
    aggiornaBottoni();
    caricaElenco();
    if (dati.bozza) {
      avvisa("salvato come bozza: non è online", "ok");
    } else {
      avvisa("salvato: il sito si aggiorna in circa un minuto…", "ok");
      controllaOnline(dati.indirizzo, 0);
    }
  }

  function controllaOnline(indirizzo, giri) {
    clearTimeout(stato.controllo);
    const nome = stato.nome;
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
        controllaOnline(indirizzo, giri + 1);
      } else {
        avvisa("la pubblicazione ci sta mettendo più del solito: controlla la build su Vercel", "errore");
      }
    }, 10000);
  }

  // ------------------------------------------------------------ media

  function inserisci(s) {
    if (stato.nome === null) { avvisa("apri prima un post", "errore"); return; }
    mostraScheda("scrivi");
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
    if (stato.nome !== null) {
      inserisci(dati.tipo === "audio" ? "![titolo del brano](" + nome + ")" : "![descrivi cosa si vede](" + nome + ")");
    }
  });

  // ------------------------------------------------------------ schede (telefono)

  function mostraScheda(quale) {
    const vedi = quale === "vedi";
    $("s-scrivi").setAttribute("aria-selected", String(!vedi));
    $("s-vedi").setAttribute("aria-selected", String(vedi));
    document.body.dataset.scheda = vedi ? "vedi" : "scrivi";
  }
  $("s-scrivi").addEventListener("click", () => mostraScheda("scrivi"));
  $("s-vedi").addEventListener("click", () => { mostraScheda("vedi"); anteprima(); });

  // ------------------------------------------------------------ comandi

  $("b-nuovo").addEventListener("click", nuovoPost);
  $("b-anteprima").addEventListener("click", () => { mostraScheda("vedi"); anteprima(); });
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
