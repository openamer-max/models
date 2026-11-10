# OpenAmer-Max

Ein **eigenes 3B-Sprachmodell** für OpenAmer — läuft lokal in [Ollama](https://ollama.com),
ohne Cloud, ohne API-Key, ohne Anbieter.

Entstanden aus **Qwen2.5-3B-Instruct** (Apache 2.0) durch QLoRA-Feintuning,
verschmolzen mit der Basis (`merge_and_unload`) und nach GGUF gewandelt.

## Version 1.1 — was sich geändert hat

Die erste Fassung war auf reine Fakten-Fragen trainiert. Ergebnis: ein
FAQ-Automat, der auf „Was ist 17 mal 23?" mit *„Das weiss ich nicht"* antwortete
und Programmier-Fragen ablehnte. 1.1 ist auf gemischten Daten trainiert
(53 % allgemeine Aufgaben) und kann beides.

| Prüfstand | 1.0 | 1.1 |
|---|---|---|
| Fakten über OpenAmer (23 Fälle) | 22/23 (95,7 %) | 21/23 (91,3 %) |
| Allgemeine Fähigkeiten (15 Sonden) | 7/15 (46,7 %) | **14/15 (93,3 %)** |
| Alltag, Format, Logik, Langtext (23) | 14/23 (60,9 %) | 15/23 (65,2 %) |

Tempo: 73–86 Tokens/s auf einer RTX 5060 Laptop (8 GB).

## Dateien

| Datei | Größe | Zweck |
|---|---|---|
| `openamer-max.q4.gguf` | 1,93 GB | **Empfohlen.** 4,99 Bit/Gewicht, schnell, wenig RAM |
| `openamer-max.f16.gguf.part-*` | 3 Teile, 6,18 GB | Volle Genauigkeit, zum Selbst-Quantisieren |

Die F16 liegt in drei Teilen, weil GitHub pro Datei nur 2 GiB erlaubt.

## Installation

```bash
# 1. Herunterladen
curl -L -o openamer-max.q4.gguf \
  https://github.com/openamer-max/models/releases/latest/download/openamer-max.q4.gguf

# 2. Bei Ollama anmelden
ollama create openamer-max -f - <<'EOF'
FROM ./openamer-max.q4.gguf
PARAMETER temperature 0.7
PARAMETER num_ctx 8192
EOF

# 3. Loslegen
ollama run openamer-max "Was ist OpenAmer?"
```

### F16 (volle Genauigkeit)

```bash
for i in 0 1 2; do
  curl -L -O https://github.com/openamer-max/models/releases/latest/download/openamer-max.f16.gguf.part-$i
done
cat openamer-max.f16.gguf.part-* > openamer-max.f16.gguf

ollama create openamer-max-f16 -f - <<'EOF'
FROM ./openamer-max.f16.gguf
EOF
```

## Was das Modell kann

- **46 belegte Fakten** über OpenAmer — Kosten, Plattformen, Funktionsweise, Grenzen
- **Rechnen** mit kleinen Zahlen, **Programmieren** (Python, JavaScript, Rust)
- **Texte** schreiben, verbessern, übersetzen, zusammenfassen
- **Format-Anweisungen** einhalten (JSON, Stichpunkte, genau N Sätze)
- **Ehrlich** „Das weiss ich nicht" bei Unwissbarem — erfindet keine OpenAmer-Fakten
- **Lehnt gefährliche Anfragen ab** (Sprengstoff, Hacking, Gewalt)
- **Deutsch** und **Bosnisch/Kroatisch/Serbisch**

## Grenzen — ehrlich

- **3B Parameter.** Gut für Chat, Identität und Fakten. Nicht für mehrstufige
  Agentenarbeit.
- **Lange Texte** werden unzuverlässig ausgewertet: aus einem 130-Wörter-Text
  die richtige Zahl zu ziehen gelingt nur in einem Drittel der Fälle.
- **Mehrschrittiges Rechnen im Gesprächsverlauf** geht schief (4711+89 → 4700).
- **Bosnisch ist fragil.** Direkte Fakten-Fragen kommen korrekt, freie Fragen
  driften gelegentlich in Nachbarsprachen. Die Basis Qwen2.5 hat wenig
  Balkan-Daten; 3B reicht nicht, das auszugleichen.
- **Arithmetik** über kleine Zahlen hinaus ist unsicher — dafür ist ein
  Rechenwerkzeug der richtige Weg, nicht das Modell.

## Herkunft, nachvollziehbar

Basis `Qwen/Qwen2.5-3B-Instruct` → QLoRA-Adapter (r=16, α=32, 4 Epochen auf
1763 Beispielen) → `merge_and_unload` → GGUF f16 → `llama-quantize Q4_K_M`.
Trainingsdaten: 730 Fakten mit RAG-Kontext, 92 Fakten ohne Kontext, 223
bosnische Sätze, 718 allgemeine Aufgaben (Rechnen, Code, Format, Alltag,
Grammatik, Ablehnen, Smalltalk).

## Lizenz

Basis: Qwen2.5-3B-Instruct, **Apache 2.0** — kommerzielle Nutzung, Veränderung
und Weitergabe erlaubt. Der Feintuning-Anteil steht unter derselben Lizenz.
Der Copyright-Hinweis der Basis bleibt bestehen (Apache 2.0, Abschnitt 4).

## Mehr

- Projekt: https://openamer-max.github.io/
- App im Browser: https://openamer-max.github.io/app/
- Entwickler: Amer Sacirovic, Schweiz
