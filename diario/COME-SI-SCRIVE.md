# Come si scrive un post del diario

Ogni post è un file di testo in questa cartella, scritto nel formato **Nota**
(l'interprete è `strumenti/nota.py`, fatto da zero, senza librerie esterne).

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
tipo: passato
tag: retro, reti
sommario: Il fischio, la linea occupata e la bolletta.
bozza: si
---
```

| chiave     | obbligatoria | valori                                           |
|------------|--------------|--------------------------------------------------|
| `titolo`   | sì           | fino a 120 caratteri                             |
| `data`     | sì           | AAAA-MM-GG, uguale a quella del nome del file    |
| `tipo`     | sì           | `pensiero`, `cronaca` oppure `passato`           |
| `tag`      | no           | fino a 8, separati da virgola, minuscole e trattini |
| `sommario` | no           | una riga; se manca usa l'inizio del testo        |
| `bozza`    | no           | `si` = non pubblicato (si vede solo in anteprima) |

La riga `---` chiude l'intestazione.

## 3. Il testo

```
Un paragrafo. Le righe vicine si uniscono,
una riga vuota separa i paragrafi.

# Titoletto
## Sotto-titoletto

> una citazione

- una voce di elenco
- un'altra

---            (linea di separazione)

*grassetto*  _corsivo_  `codice`  [testo del link](https://indirizzo.it)
```

Blocchi di codice:

````
```python
print("ciao")
```
````

- Per scrivere un asterisco vero: `\*`. Stessa cosa per `\_`, `` \` ``, `\[`.
- Una riga che finisce con `\` va a capo senza aprire un nuovo paragrafo.
- I link accettano solo indirizzi `https://`.
- L'HTML scritto a mano non passa: viene mostrato come testo.

## 4. Pubblicare

1. Crea il file qui in `diario/` (anche dal sito di GitHub, pure dal telefono).
2. Fai commit su `main`.
3. Vercel lancia i test, genera le pagine e pubblica in circa un minuto.

Se c'è un errore la pubblicazione si ferma e il sito resta com'era. Il log
della build su Vercel dice file e riga, per esempio:

```
diario/2026-11-20-il-modem-a-56k.nota:3: tipo «storia» non valido: usa pensiero, cronaca, passato
```

Per provare in locale:

```
python3 strumenti/genera.py                 # solo i post pubblicati
DIARIO_BOZZE=1 python3 strumenti/genera.py  # anche le bozze
```
