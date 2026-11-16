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

## Ergebnis (Token im Prompt, ✗ = nicht gefunden)

| Modell | Parameter | Größen | größter Treffer | Anteil am Maximum | Treffer |
|---|---|---|---|---|---|
| Watch | 0,60B | 3,070 · 12,038 · 24,008 · 39,322 | **39,322** | 96 % | 4/4 |
| Phone | 3,1B | 3,713 · 12,681 · 24,651 · 30,655 | **30,655** | 94 % | 4/4 |
| Tab | 7,6B | 3,701 · 12,669 · 24,639 · 30,643 | **30,643** | 94 % | 4/4 |
| Desktop | 14,8B | 3,715 · 12,683 · 24,653 · 30,657 | **30,657** | 94 % | 4/4 |
| Pro | 23,6B | 2,648 · 10,200 · 20,280 · 25,336 | **25,336** | 77 % | 4/4 |
| Ultra | 32,8B | 3,125 · 12,093 · 24,063 · 30,067 | **30,067** | 92 % | 4/4 |

Ultra wurde nach dem ersten Durchlauf neu gebaut: Fassung 1 erzwang `num_gpu 0`
(alles CPU), schaffte 9.966 Token bei rund 17 Token/s und brach bei 16k mit HTTP
500 ab. Fassung 2 legt 10 von 64 Schichten in den VRAM und ist rund **12×
schneller** (200 Token/s) — damit 4 von 4 Treffern bis **30.067 Token**. Die alten
Werte stehen als `historie_fassung_1` in der Rohdatei.

Vergleichsbasis (unser Feintuning-Basismodell Qwen2.5-14B): richtig bei 2.508
und 9.880 Token (`reports/kontext_basis2.json`).

## Was das belegt

Der Kontext wird nicht abgeschnitten, und ein Fakt an 50 % Tiefe bleibt bis
39.322 Token auffindbar. Die Modelle tragen ihren dokumentierten Kontext.

## Was das **nicht** belegt

- **Kein Verständnisbeweis.** Ein Faktenabruf ist der einfachste Kontexttest.
  Wer ihn besteht, kann an einer Aufgabe scheitern, die den ganzen Text
  verstehen muss.
- **Pro erreicht nur 77 %** (25.336 von 32.768): Neben 23,6 GB Gewichten bleibt
  auf 32 GB RAM kein Platz für einen größeren KV-Cache, Ollama deckelt dort.
- **Ultra ist nicht widerlegt, nur nicht gemessen.**

## Zwei Fehler im Prüfstand (dokumentiert, weil sie zu falschen Ergebnissen führten)

1. **`num_ctx` gleich der Zielgröße** schneidet den Prompt ab. Gemessen:
   `num_ctx=2048` verarbeitete 1.026 statt 2.128 Token — die Nadel fiel weg,
   das Modell antwortete „123456". Die erste Messreihe zeigte deshalb
   fälschlich „0 von 9 richtig". Der Fehler lag im Prüfstand, nicht im Modell.
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
python tools/kontexttest.py --modell watch --groessen 2500,10000,20000,32768

# eigenes Basismodell vergleichen
python tools/kontexttest.py --modell basis --name qwen2.5:14b-instruct-q4_K_M \
  --groessen 8192 --aus reports/kontext_basis.json
```
