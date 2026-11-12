# Come si scrive un post del diario

Ogni post è un file di testo in questa cartella, scritto nel formato **Nota**
(versione 2). L'interprete è `strumenti/nota.py`, fatto da zero, senza librerie
esterne. Il post di esempio `2026-11-12-hello-world.nota` usa quasi tutto quello
che trovi qui sotto.

## 1. Il nome del file

```
AAAA-MM-GG-titolo-breve.nota
```

Esempio: `2026-11-20-il-modem-a-56k.nota`. Solo minuscole, cifre e trattini.
Il nome diventa l'indirizzo: `mdeangelis.me/diario/2026-11-20-il-modem-a-56k/`.

## 2. L'intestazione

```
titolo: Come funzionava il modem a 56k
data: 2026-11-20
ora: 21:30
tipo: passato
tag: retro, reti
sommario: Il fischio, la linea occupata e la bolletta.
copertina: modem.jpg
bozza: si
---
```

| chiave      | obbligatoria | valori                                               |
|-------------|--------------|------------------------------------------------------|
| `titolo`    | sì           | fino a 120 caratteri                                 |
| `data`      | sì           | AAAA-MM-GG, uguale a quella del nome del file        |
| `ora`       | no           | HH:MM, ora italiana: mette in ordine i post dello stesso giorno (il più recente in alto). Senza ora il post va a inizio giornata |
| `tipo`      | sì           | `pensiero`, `cronaca` oppure `passato`               |
| `tag`       | no           | fino a 8, separati da virgola, minuscole e trattini  |
| `sommario`  | no           | una riga; se manca usa l'inizio del testo            |
| `copertina` | no           | un'immagine di `diario/media/`: va in cima al post e nell'anteprima quando condividi il link |
| `bozza`     | no           | `si` = non pubblicato (si vede solo in anteprima)    |

La riga `---` chiude l'intestazione.

## 3. Il testo

### Paragrafi e titoli

```
Un paragrafo. Le righe vicine si uniscono,
una riga vuota separa i paragrafi.
Una riga che finisce con \
va a capo senza aprire un nuovo paragrafo.

# Titoletto
## Sotto-titoletto

---            (linea di separazione)
```

### Dentro una frase

| scrivi                         | ottieni                         |
|--------------------------------|---------------------------------|
| `*grassetto*`                  | **grassetto**                   |
| `_corsivo_`                    | *corsivo*                       |
| `~~barrato~~`                  | ~~barrato~~                     |
| `==evidenziato==`              | testo evidenziato               |
| `` `codice` ``                 | `codice`                        |
| `[[Ctrl]]+[[C]]`               | tasti della tastiera            |
| `[testo](https://sito.it)`     | link esterno, si apre a parte   |
| `[testo](/diario/2026-11-12-hello-world/)` | link a un altro post |
| `[testo](/#musica)`            | link a una pagina del sito      |
| `[testo](#s-titoletto)`        | link a un titoletto di questo post |
| `testo[^1]`                    | rimando a una nota a piè di pagina |

- I link ad altri post e ai titoletti vengono controllati: se il post non esiste
  (o è ancora in bozza) la pubblicazione si ferma.
- L'indirizzo di un titoletto è `#s-` seguito dal titolo in minuscolo, senza
  accenti e con i trattini: `# Perché il 56k` diventa `#s-perche-il-56k`.
- Per scrivere un segno speciale così com'è mettici davanti `\`:
  `\*`, `\_`, `\~`, `\=`, `\|`, `\[`, `\!`. Per iniziare una riga con
  `2026. anno` senza farne un elenco: `2026\. anno`.

### Elenchi

```
- una voce
- un'altra

1. primo passo
2. secondo passo

- [x] cosa fatta
- [ ] cosa da fare
```

### Citazioni e riquadri

```
> una citazione
>
> secondo paragrafo della citazione

> [!nota]
> Un'informazione in più.
```

Riquadri disponibili: `[!nota]`, `[!consiglio]`, `[!attenzione]`, `[!curiosita]`.

### Tabelle

```
| Anno | Velocità | Nome |
|------|:--------:|-----:|
| 1991 | 14,4k    | V.32bis |
| 1998 | 56k      | V.90 |
```

La seconda riga è obbligatoria. `:---:` centra la colonna, `---:` la allinea
a destra. Per una `|` dentro una cella scrivi `\|`.

### Codice

````
```python
print("ciao")
```
````

### Note a piè di pagina

```
Il Bell 103 trasmetteva a 300 bit al secondo[^bell].

[^bell]: Lo presentò AT&T nel 1962.
```

La definizione può stare dove vuoi (di solito in fondo). Le note vengono
numerate da sole nell'ordine in cui le richiami.

### Immagini e audio

1. Metti il file in `diario/media/`. Nome in minuscolo, con trattini:
   `modem-us-robotics.jpg`. Formati: `jpg`, `png`, `webp`, `gif` per le
   immagini, `mp3`, `ogg` per l'audio.
2. Nel post, **su una riga da sola**:

```
![cosa si vede nella foto](modem-us-robotics.jpg)
![cosa si vede nella foto](modem-us-robotics.jpg "una didascalia, anche con *stile*")
![Titolo del brano](demo-notturno.mp3 "una nota sul brano")
```

- Il testo tra `[ ]` è obbligatorio: è quello che legge chi non vede l'immagine.
- Più immagini su righe consecutive (senza riga vuota in mezzo) diventano una
  galleria. Un clic apre la foto a grandezza piena.
- Dimensioni massime: 6 MB per le immagini, 25 MB per l'audio. Per il web
  basta una foto larga 1600-2000 pixel.

**Privacy**: prima di andare online i file vengono ripuliti. Dalle foto
spariscono posizione GPS, modello del telefono, data e qualsiasi altro
metadato (resta solo l'orientamento, così le foto non escono girate); dagli MP3
spariscono i tag ID3. Il formato viene riconosciuto leggendo il file, non dal
nome: un file che non è davvero un'immagine viene rifiutato. Online vanno solo
i file usati da almeno un post.

## 4. Pubblicare

1. Crea il file qui in `diario/` (anche dal sito di GitHub, pure dal telefono).
   Le immagini vanno in `diario/media/`.
2. Fai commit su `main`.
3. Vercel lancia i test, genera le pagine e pubblica in circa un minuto.

Se c'è un errore la pubblicazione si ferma e il sito resta com'era. Il log
della build su Vercel dice file e riga, per esempio:

```
diario/2026-11-20-il-modem-a-56k.nota:3: tipo «storia» non valido: usa pensiero, cronaca, passato
diario/2026-11-20-il-modem-a-56k.nota:14: file «modem.jgp» non trovato in diario/media/
diario/media/foto.jpg: file troppo grande (9 MB, massimo 6 MB): riducilo prima di caricarlo
```

Per provare in locale:

```
python3 strumenti/genera.py                 # solo i post pubblicati
DIARIO_BOZZE=1 python3 strumenti/genera.py  # anche le bozze
python3 -m unittest discover -s strumenti   # i test
```
