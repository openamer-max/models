# Kontextmessung — wie viel Text tragen die Modelle wirklich?

Gemessen am 16.11.2026 auf einem Laptop (RTX 5060, 8 GB VRAM, 32 GB RAM).
Nicht aus Modellkarten abgeschrieben, sondern ausgeführt.

## Verfahren

Ein Fakt steht bei 50 % Tiefe in einem langen Text, das Modell muss ihn
zurückgeben. Kontextfenster mit Reserve (`num_ctx = 2 × Zielgröße`),
`temperature 0`, `think: false`, Antwort nur der Code.

```
Text: [Fülltext × n]  Der geheime Code lautet QX-7741.  [Fülltext × n]
Frage: Wie lautet der geheime Code aus dem Text oben?
```

Prüfstand: [`tools/kontexttest.py`](../tools/kontexttest.py)
Rohdaten: [`reports/kontext_*.json`](../reports/)

## Ergebnis

| Modell | Parameter | getestet bis | Anteil am Maximum | Dauer | Ergebnis |
|---|---|---|---|---|---|
| Watch | 0,60B | **39.322 Token** | 96 % von 40.960 | 222,6 s | richtig |
| Phone | 3,1B | **30.655 Token** | 94 % von 32.768 | 17,6 s | richtig |
| Tab | 7,6B | **30.643 Token** | 94 % von 32.768 | 28,5 s | richtig |
| Desktop | 14,8B | **30.657 Token** | 94 % von 32.768 | 108,4 s | richtig |
| Pro | 23,6B | **25.336 Token** | 77 % von 32.768 | 102,4 s | richtig |
| Ultra | 32,8B | nicht messbar | — | ~32 min/Anfrage | offen |

Zusätzlich geprüft bei ~2,5k, ~10k und ~20k Token: alle fünf messbaren Modelle
richtig. Vergleichsbasis: Qwen2.5-14B (unser Feintuning-Basismodell) richtig bei
2.508 und 9.880 Token.

## Was das belegt

Der Kontext wird nicht abgeschnitten, und ein Fakt an 50 % Tiefe bleibt bis
39.322 Token auffindbar. Die Modelle tragen ihren dokumentierten Kontext.

## Was das **nicht** belegt

- **Kein Verständnisbeweis.** Ein Faktenabruf ist der einfachste Kontexttest.
  Wer ihn besteht, kann an einer Aufgabe scheitern, die den ganzen Text
  verstehen muss.
- **Pro erreicht nur 77 %.** Neben 23,6 GB Gewichten bleibt auf 32 GB RAM kein
  Platz für einen größeren KV-Cache; Ollama deckelt dort.
- **Ultra ist nicht widerlegt, nur nicht gemessen.** Sein Modelfile erzwingt
  `num_gpu 0`: 19,9 GB auf der CPU, rund 17 Token/s Prompt-Verarbeitung,
  32.768 Token ≈ 32 Minuten. Auf dieser Hardware nicht praktikabel.

## Zwei Fehler im Prüfstand (dokumentiert, weil sie zu falschen Ergebnissen führten)

1. **`num_ctx` gleich der Zielgröße** schneidet den Prompt ab. Gemessen:
   `num_ctx=2048` verarbeitete 1.026 statt 2.128 Token — die Nadel fiel weg,
   das Modell antwortete „123456". Die erste Messreihe zeigte deshalb
   fälschlich „0 von 9 richtig". Mit Reserve: richtig. Der Fehler lag im
   Prüfstand, nicht im Modell.
2. **Bei 32k-Ziel schnitt Ollama erneut ab** (16.386 statt ~39k), weil die
   Modelle bei 32.768 deckeln. Die Zielgröße muss unter der Deckelung liegen —
   daher 25.000 statt 32.768 bei Phone/Tab/Desktop/Pro.

## Die entscheidende Zahl

```
größter gemessener Kontext   39.322 Token (Watch)
Agent-Mindestanforderung     64.000 Token (Konstante in agent/model_metadata.py)
```

Auch am oberen Ende gemessen bleibt die Familie **unter der Agent-Grenze**.
OpenAmer Agent kann auf diesen Modellen nicht laufen — unabhängig von
Konfiguration oder Hardware.

## Nachrechnen

```bash
# ein Modell prüfen (Ollama muss laufen)
python tools/kontexttest.py --modell watch --groessen 25000

# eigenes Basismodell vergleichen
python tools/kontexttest.py --modell basis --name qwen2.5:14b-instruct-q4_K_M \
  --groessen 8192 --aus reports/kontext_basis.json
```
