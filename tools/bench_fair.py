"""Fairer Vergleich: allgemeiner Satz (A) und Kontext-Satz (B).

A --satz allgemein : 20 Fragen, die jedes faehige Modell ohne Vorwissen loesen kann
                     (Rechnen, Logik, Sprache, Wissen, Anweisungen, Ehrlichkeit).
                     Damit ist ein Vergleich zwischen fremden Modellen und unseren
                     Stufen sinnvoll - der 45er-Satz prueft nur Produktwissen.
B --satz kontext   : dieselben 45 Faelle wie der Hauspruefstand, aber die Fakten
                     liegen im System-Prompt. Gemessen wird Anweisungsbefolgung
                     und Ehrlichkeit, nicht Gedaechtnis.

Zwei Ziele:
  --openrouter <id>  fremdes Modell ueber OpenRouter (kostenlos moeglich)
  --ollama <name>    lokales Modell (unsere Stufen)

Der Takt ist absichtlich langsam: das Free-Tier drosselt pro Minute, und ein
429-Sturm kostet mehr Zeit als gleichmaessiges Warten.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

# Datenverzeichnis: ueber OPENAMER_TRAIN_DIR setzbar, sonst das aktuelle.
BASIS = Path(os.environ.get("OPENAMER_TRAIN_DIR", Path.cwd()))
TAKT = float(os.environ.get("BENCH_TAKT", "12"))


def gruppen(feld):
    raus = []
    for e in feld or []:
        if isinstance(e, str):
            raus.append([e])
        elif isinstance(e, (list, tuple)):
            raus.append([str(x) for x in e])
    return raus


def bewerte(text, fall):
    t = (text or "").lower()
    for g in gruppen(fall.get("require")):
        if not any(w.lower() in t for w in g):
            return False, "fehlt:" + "/".join(g)[:40]
    for g in gruppen(fall.get("forbid")):
        for phrase in g:
            if re.search(r"\b" + re.escape(phrase.lower()) + r"\b", t):
                return False, "verboten:" + phrase[:30]
    return True, ""


def frage_openrouter(schluessel, modell, system, frage, versuche=6):
    nutzlast = json.dumps({
        "model": modell,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": frage}],
        "max_tokens": 400, "temperature": 0,
    }).encode()
    for n in range(versuche):
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions", data=nutzlast,
            headers={"Authorization": f"Bearer {schluessel}",
                     "Content-Type": "application/json",
                     "HTTP-Referer": "https://openamer-max.github.io",
                     "X-Title": "OpenAmer fair benchmark"})
        try:
            d = json.load(urllib.request.urlopen(req, timeout=180))
            return d["choices"][0]["message"]["content"] or ""
        except urllib.error.HTTPError as e:
            if e.code == 429:
                warte = int(e.headers.get("Retry-After") or 30 * (n + 1))
                print(f"     429 - warte {warte}s", flush=True)
                time.sleep(warte)
                continue
            raise RuntimeError(f"HTTP {e.code}: {e.read().decode()[:120]}")
    raise RuntimeError("429 auch nach Wiederholungen")


def frage_ollama(name, system, frage):
    nutzlast = json.dumps({
        "model": name,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": frage}],
        "stream": False, "think": False,
        "options": {"temperature": 0, "num_predict": 400, "repeat_penalty": 1.0},
    }).encode()
    req = urllib.request.Request("http://127.0.0.1:11434/api/chat", data=nutzlast,
                                 headers={"Content-Type": "application/json"})
    d = json.load(urllib.request.urlopen(req, timeout=600))
    return d.get("message", {}).get("content", "")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--satz", choices=("allgemein", "kontext", "a2"), required=True)
    p.add_argument("--openrouter")
    p.add_argument("--ollama")
    a = p.parse_args()

    if a.satz in ("allgemein", "a2"):
        datei = "allgemein.json" if a.satz == "allgemein" else "allgemein_a2.json"
        faelle = json.loads((BASIS / "benchmarks" / datei).read_text(encoding="utf-8"))
        system = "Du bist ein sachlicher Assistent. Antworte knapp und korrekt auf Deutsch."
    else:
        roh = json.loads((BASIS / "data/testset_pro_v2.json").read_text(encoding="utf-8"))
        faelle = roh if isinstance(roh, list) else roh["faelle"]
        system = ("Du bist ein Assistent. Nutze ausschliesslich die folgenden Fakten. "
                  "Wenn eine Frage dadurch nicht beantwortet wird, sage, dass du es "
                  "nicht weisst.\n\n"
                  + (BASIS / "benchmarks/faktenblatt.md").read_text(encoding="utf-8"))

    ziel = a.openrouter or a.ollama
    schluessel = None
    if a.openrouter:
        schluessel = Path.home().joinpath(".openrouter_key").read_text().strip()

    print(f"=== {a.satz} · {ziel} · {len(faelle)} Faelle", flush=True)
    treffer, details = 0, []
    for i, fall in enumerate(faelle, 1):
        try:
            if a.openrouter:
                text = frage_openrouter(schluessel, a.openrouter, system, fall["q"])
            else:
                text = frage_ollama(a.ollama, system, fall["q"])
        except Exception as e:
            print(f"  [{i:2}] Fehler: {str(e)[:80]}", flush=True)
            details.append({"i": i, "ok": None, "fehler": str(e)[:100]})
            continue
        ok, grund = bewerte(text, fall)
        treffer += int(ok)
        details.append({"i": i, "ok": ok, "grund": grund, "antwort": text[:200]})
        print(f"  [{i:2}/{len(faelle)}] {'OK ' if ok else 'daneben'} · {fall['q'][:44]}"
              + ("" if ok else f"  ({grund})"), flush=True)
        if a.openrouter:
            time.sleep(TAKT)

    ergebnis = {"satz": a.satz, "ziel": ziel, "treffer": treffer,
                "von": len(faelle), "prozent": round(100 * treffer / len(faelle), 1),
                "details": details}
    reports = BASIS / "reports"
    reports.mkdir(exist_ok=True)
    name = re.sub(r"[^a-zA-Z0-9]+", "_", ziel)[:40]
    (reports / f"bench_{a.satz}_{name}.json").write_text(
        json.dumps(ergebnis, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  -> {treffer}/{len(faelle)} ({ergebnis['prozent']} %)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
