# OpenAmer-Max — Modelle

Fünf Stufen der OpenAmer-Max-Familie, **nach Parameterzahl benannt**, nicht nach
Marketing. Jede Stufe ist trainiert, gegen denselben eingefrorenen Prüfstand
gemessen (45 Fälle) und über vier Kanäle verfügbar.

| Stufe | Parameter | Größe | Prüfstand v2 | Bezug |
|---|---|---|---|---|
| **Watch** | ≤ 1B (0,60B) | 639 MB Q8_0 | **37/45 (82,2 %)** | [HF](https://huggingface.co/openamer-max/openamer-max-watch) · [Release watch-v1](https://github.com/openamer-max/models/releases/tag/watch-v1) · [Ollama](https://ollama.com/amersacirovic/openamer-max-watch) |
| **Phone** | 1–5B (3,09B) | 2,5 GB Q6_K | **43/45 (95,6 %)** | [HF](https://huggingface.co/openamer-max/openamer-max-phone) · [Release phone-v1](https://github.com/openamer-max/models/releases/tag/phone-v1) · [Ollama](https://ollama.com/amersacirovic/openamer-max-phone) |
| **Tab** | 5–10B (7,62B) | 4,4 GB Q4_K_M | **42/45 (93,3 %)** | [HF](https://huggingface.co/openamer-max/openamer-max-tab) · [Release tab-v1](https://github.com/openamer-max/models/releases/tag/tab-v1) · [Ollama](https://ollama.com/amersacirovic/openamer-max-tab) |
| **Desktop** | 10–20B (14,70B) | 8,4 GB Q4_K_M | **44/45 (97,8 %)** | [HF](https://huggingface.co/openamer-max/openamer-max-desktop) · [Release desktop-v1](https://github.com/openamer-max/models/releases/tag/desktop-v1) · [Ollama](https://ollama.com/amersacirovic/openamer-max-desktop) |
| **Pro** | 20–30B (24,00B) | 13,4 GB Q4_K_M | **43/45 (95,6 %)** | [HF](https://huggingface.co/openamer-max/openamer-max-pro) · [Release pro-v1](https://github.com/openamer-max/models/releases/tag/pro-v1) · [Ollama](https://ollama.com/amersacirovic/openamer-max-pro) |
| **Ultra** | 30–100B (32,00B) | 18,5 GB Q4_K_M | **41/45 (91,1 %)** | [HF](https://huggingface.co/openamer-max/openamer-max-ultra) · [Release ultra-v1](https://github.com/openamer-max/models/releases/tag/ultra-v1) · [Ollama](https://ollama.com/amersacirovic/openamer-max-ultra) |

**Ehrlich dazu:** Ultra (32B) erreicht 41/45 und liegt damit **zwei Punkte unter Desktop** — die größte Stufe ist nicht die beste. Mit 2.890 Trainingssätzen ist die Datenmenge für 32 Milliarden Parameter zu klein. Desktop (14,7B) liegt mit 44/45 vor Pro (24B) mit 43/45 — mehr
Parameter bringen auf diesem Prüfstand keinen Punkt. Wer das Gegenteil behauptet,
hat nicht gemessen.

`Ultra` (30–100B) · `Mega` (100–500B) · `Giga` (500B–1T) · `Tera` (1–10T) folgen
stufenweise — jede erst, wenn sie ihren eigenen Prüfstand besteht.

## Ein Befehl, ohne Download

Die Stufen liegen in der Ollama-Registry. Kein GGUF herunterladen, kein Modelfile
schreiben:

```bash
ollama run amersacirovic/openamer-max-watch     # 639 MB, laeuft auf jeder CPU
ollama run amersacirovic/openamer-max-phone     # 2,5 GB
ollama run amersacirovic/openamer-max-tab       # 4,4 GB
ollama run amersacirovic/openamer-max-desktop   # 8,4 GB
ollama run amersacirovic/openamer-max-pro       # 13,4 GB
```

Wer die rohe Datei braucht (eigene Quantisierung, Prüfsummen), nimmt das Release
oder HuggingFace — beide enthalten die unveränderte GGUF samt SHA256.

### Zwei Einstellungen, die für die ganze Familie gelten

**`repeat_penalty 1.0`** — mit 1.1 drehte die Phone-Stufe eine Verneinung um
(„Ne radi na Androidu" statt „na iPhoneu"). Das war unsere eigene Einstellung,
kein Modell- und kein Quantisierungsfehler.
**`temperature 0`** für Faktenfragen; das Modell ist auf knappe, korrekte Antworten
trainiert.

## OpenAmer-Max-Watch (0.6B, Q8_0, 639 MB)

Kleinstes Modell der Familie: läuft offline auf einem Gerät, antwortet in
**0,04–0,38 s**, braucht keine GPU.

Gemessen an der ausgelieferten Datei:

| Prüfung | Ergebnis |
|---|---|
| Eingefrorener Prüfstand, 23 ungesehene Fälle, kontaminationsfrei | **23/23 (100 %)** |
| Antwort-Token-Genauigkeit (Validierung) | **99,63 %** |
| Frischtest, 9 nie trainierte Fragen | **8/9** |
| 16 Sonden durch Ollama | **15/16** |

**Wichtig:** `think: false` ist Pflicht — ohne das verbraucht Qwen3 alle Tokens im
Denkblock und antwortet nie.

**Grenzen, ehrlich:** kein freier deutscher Fließtext, kein Allgemeinwissen, keine
vierstelligen Multiplikationen; Bosnisch nur bei direkten Formulierungen.

```bash
curl -L -o openamer-max-watch.gguf   https://github.com/openamer-max/models/releases/download/watch-v1/openamer-max-watch-q8.gguf
ollama create OpenAmer-Max-Watch -f Modelfile
```

Auch verfügbar auf
[HuggingFace](https://huggingface.co/openamer-max/openamer-max-watch) und
[Kaggle](https://www.kaggle.com/datasets/amersacirovic/openamer-max-watch).

---

## Unterstützen

Wenn dir diese Modelle helfen: ein ⭐ hier hilft mehr als du denkst — daran erkennen
Sponsoren, dass ein Projekt Aufmerksamkeit hat.

**PayPal (QR-Code im Release, `paypal-qr.png`):**
<https://www.paypal.com/qrcodes/managed/bfb5b6b5-c04c-4836-af60-987dff8cff61>

---

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
