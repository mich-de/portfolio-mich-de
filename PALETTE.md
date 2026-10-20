Design System: Palette Colori "Abstract Geometric Dark"
Documentazione della palette colori derivata dal design geometrico astratto su sfondo scuro.Temi principali: Grigio Tech, Arancione Vivace, Bianco Puro.

Tabella Colori
Nome Colore Variabile CSS Hex Code Descrizione
Deep Charcoal --bg-primary #111216 Sfondo principale del sito (Dark Mode).
Grigio Base --gray-primary #A0A0A0 Elementi neutrali, testi secondari.
Argento Chiaro --gray-light #D6D6D6 Riflessi, bordi attivi e highlights.
Slate Scuro --gray-dark #4A4F55 Linee di profondità, ombre interne.
Arancione Vivace --color-primary #FF9F1C Colore primario (CTA, link, figure principali).
Albicocca Chiaro --color-highlight #FFBF69 Accenti luminosi, glow, stati hover.
Ambra Scura --color-shade #B87611 Ombre, elementi passivi o retro.
Arancione Intenso --color-accent #FF6B00 Punti focali, notifiche, dettagli piccoli.
Bianco Puro --white-primary #FFFFFF Titoli, testo principale, figure chiave.
Grigio Chiaro --white-muted #B0B0B0 Dettagli secondari, placeholder.
Implementazione CSS
Per utilizzare questa palette nel tuo progetto, definisci le seguenti variabili nel tuo file CSS o SCSS.

  /*--- SHINE (SPARKLING) ---*/
  --shine-base:   #18181B (Light) / #FFFFFF (Dark);
  --shine-accent: #334155 (Light) / #94a3b8 (Dark);
}

/*Esempio di utilizzo*/
body {
  background-color: var(--bg-primary);
  color: var(--white-primary);
}

.animate-text-shine {
  background: linear-gradient(to right, var(--shine-base), var(--shine-accent), var(--shine-base));
}

Note Accessibilità
Assicurati di verificare il contrasto tra il testo e lo sfondo (#111216).

Il testo var(--white-primary) su var(--bg-primary) ha un contrasto eccellente.
Il testo var(--gray-primary) su var(--bg-primary) è adatto per paragrafi lunghi.
L'arancione var(--color-primary) è ottimo per bottoni o icone, ma usarlo per testo su sfondo scuro potrebbe richiedere una verifica del contrasto WCAG.

## Branding Logo (MDEANGELIS)

Il logo testuale utilizza una combinazione tipografica e un'animazione "Sparkle":

* **M / MDE**: `font-sans` (Bold).
* **ANGELIS**: `font-display` (Normal/Light).
* **Effetto Shine**: Un gradiente lineare che scorre sul testo per simulare un riflesso metallico.
  * **Light Mode**: Testo Scuro con riflesso Slate.
  * **Dark Mode**: Testo Bianco con riflesso Argento.

## Stile Titoli Sezione (H2)

I titoli delle sezioni (Chi Sono, Interessi, Contatti) usano un gradiente coerente con il brand:
`from-accent via-chart-1 to-chart-3` (Arancione Intenso → Arancione Vivace → Ambra Scura)

## Sfondo Sezioni

Tutte le sezioni usano `bg-background` per uniformità. La Hero section include orbs sfocati (`blur-[150px]`, `opacity: 10%`) per un leggero effetto glow che sfuma dolcemente nelle sezioni successive.
