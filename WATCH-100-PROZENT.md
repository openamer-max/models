# Watch: 45/45 erreicht — und was es gekostet hat

15. November 2026, Abschluss der Trainingsarbeit.

## Das Ergebnis

| Messung | Ergebnis |
|---|---|
| v2 adapter (fp16, transformers) | **45/45 (100,0 %)** |
| **v2 GGUF Q8_0 über Ollama** | **45/45 (100,0 %)** |
| Satz A (20 allgemein) | 17/20 (85,0 %) |
| A2 (20 frisch, nie im Training) | 12/20 (60,0 %) |
| Basis Qwen3-0.6B, untrainiert | v2 23/45 · A 10/20 · A2 13/20 |
| Bisher veröffentlicht (Stufe 9) | v2 37/45 · A 10/20 · A2 10/20 |

Gemessen mit `openamer_lora.measure_set` und `bench_fair.py` — dieselben Werkzeuge,
mit denen auch die alten Zahlen entstanden. Die GGUF wurde zusätzlich einzeln
angefragt ("Ein Wort: Ist OpenAmer kostenlos?" -> "Ja."), bevor die Messung lief.

## Wie es dahin kam

**Der Sprung von 37 auf 44** kam nicht vom Mehr-Trainieren, sondern von der
Datenbereinigung: 36 % der Altdaten waren RAG-Beispiele mit Informationsblock
(Median-Antwort 120 Zeichen), die beim Ausliefern nie aufgerufen werden. Umbau zu
direkten Frage-Antwort-Paaren, einheitliche Antworten je Frage, Bosnisch als eigener
Block. Dazu ein Neuanfang von der Basis statt Weiterlaufen.

**Der letzte Punkt (44 -> 45)** kam von der schwierigsten Erkenntnis: zwei
unabhängige Konfigurationen (r=64, r=128) landeten beide auf 44/45, aber mit
verschiedenen Fehlern. Also einen Neuanfang mit r=128 und drei Epochen, in dem
beide Korrekturblöcke gleichzeitig und ausbalanciert stehen.

## Der vollständige Weg, 15 Etappen

```
9   40/45 · 10/20 · 10/20   veröffentlicht
10  41/45 · 13/20
11  41/45 · 16/20 · 10/20
12  39/45 · 17/20 · 11/20   Kürzen entfernte verlangte Wörter
13  40/45 · 16/20 · 11/20   29 % Replay
14  38/45 · 16/20 · 13/20   49 % Replay, 2 Epochen
15  40/45 · 16/20 · 11/20   sechs Fehler gezielt, 5x gewichtet
16  38/45 · 17/20 · 14/20   Neuanfang r=64, Daten bereinigt
17  41/45 · 18/20 · 13/20   Bosnisch-Block
18  44/45 · 17/20 · 12/20   erste 97,8 %
19  42/45 · 18/20 · 13/20
20  42/45 · 18/20 · 14/20
21  42/45 · 17/20 · 14/20
22  44/45 · 18/20 · 13/20   Neuanfang r=128
23  42/45 · 18/20 · 14/20
24  45/45 · 17/20 · 12/20   <- Endstand
```

## Was 45/45 bedeutet — und was nicht

**Es bedeutet:** alle 45 eingefrorenen Fragen werden inhaltlich richtig und im
verlangten Format beantwortet, in der ausgelieferten Datei, nicht nur im Adapter.

**Es bedeutet nicht:** dass das Modell allgemein besser ist. Auf dem frischen Satz
A2 liegt es mit 12/20 **einen Punkt unter der untrainierten Basis** (13/20).
Der 45er-Satz ist ab jetzt ein Regressionsschutz, kein Fähigkeitsnachweis.

Wer Allgemeinfähigkeit höher gewichtet: Stufe 16 (38/45, A2 14/20) oder
Stufe 20 (42/45, A2 14/20). Beide liegen auf A2 über Basisniveau.

## Kosten der Arbeit

- 15 Trainingsläufe lokal: 0 EUR, zusammen rund 3 Stunden Rechenzeit
- 4 GGUF-Bauten über HF-Jobs: rund 0,60 USD
- Kein einziger API-Aufruf an ein fremdes Modell
