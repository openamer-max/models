"""Kontexttest pro Modell: Nadel im Heuhaufen bei wachsender Laenge.

Warum so: die Metadaten sagen, was das Modell *kann* (32.768 / 40.960), aber nicht,
was es *nutzt*. Getestet wird echtes Verhalten - ein Fakt steht an 50 % Tiefe in
einem langen Text, das Modell soll ihn zurueckgeben.

Lehre aus dem ersten Anlauf: stand der Code mitten im Fuellertext und die Frage war
knapp formuliert, antworteten selbst 14B-Modelle falsch ("42"). Mit eigener Zeile
fuer den Code und ausdruecklicher Frage (Validierung: 152/836/2356 Token richtig)
misst der Test das Modell, nicht die Fragestellung.

Aufruf:  python kontexttest.py --modell watch --groessen 2048,8192,16384
"""
import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

API = "http://127.0.0.1:11434/api/generate"
CODE = "QX-7741"
FUELLER = ("Die Wartung der Anlage erfolgt nach Plan. Der Techniker prueft die "
           "Leitungen, notiert Messwerte und schliesst die Pruefung ab. ")
FRAGE = ("\nFrage: Wie lautet der geheime Code aus dem Text oben? "
         "Antworte nur mit dem Code selbst, ohne weiteren Text.")


def baue_prompt(ziel_token):
    """Text mit dem Code bei 50 % Tiefe, ungefaehr ziel_token Token lang."""
    n = max(1, int((ziel_token * 4) / len(FUELLER)))
    mitte = n // 2
    return (FUELLER * mitte + f"\nDer geheime Code lautet {CODE}.\n"
            + FUELLER * (n - mitte) + FRAGE)


def frage(model, prompt, ziel_token, timeout=2400):
    # num_ctx muss RESERVE haben: bei num_ctx = Zielgroesse schneidet Ollama den
    # Prompt ab (gemessen: 1026 statt 2128 Token) und die Nadel faellt weg. Das
    # erzeugte falsche Modellfehler - der Fehler lag im Pruefstand.
    num_ctx = min(max(int(ziel_token * 2), 4096), 81920)
    # think=false: Qwen3 legt die Ausgabe sonst in ein separates Feld.
    daten = json.dumps({
        "model": model, "prompt": prompt, "stream": False, "think": False,
        "options": {"num_ctx": num_ctx, "num_predict": 32, "temperature": 0.0},
    }).encode()
    req = urllib.request.Request(API, data=daten, method="POST",
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as a:
        d = json.loads(a.read().decode())
    ant = d.get("response") or ""
    return {
        "dauer_s": round(time.time() - t0, 1),
        "prompt_token": d.get("prompt_eval_count"),
        "prompt_tok_s": round((d.get("prompt_eval_count") or 0) /
                              max(d.get("prompt_eval_duration") or 1, 1) * 1e9, 1),
        "antwort": ant.strip()[:60],
        "richtig": CODE in ant,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modell", required=True)
    ap.add_argument("--groessen", default="2048,8192")
    ap.add_argument("--aus", default="")
    ap.add_argument("--name", default="",
                    help="voller Modellname statt amersacirovic/openamer-max-<modell>")
    a = ap.parse_args()

    name = a.name or f"amersacirovic/openamer-max-{a.modell}"
    ergebnisse = []
    print(f"=== {name}", flush=True)
    for groesse in [int(x) for x in a.groessen.split(",")]:
        prompt = baue_prompt(groesse)
        try:
            r = frage(name, prompt, groesse)
            r["ziel"] = groesse
            print(f"  ziel {groesse:6} | prompt {r['prompt_token']:6} tok | "
                  f"{r['dauer_s']:7.1f}s | {r['prompt_tok_s']:8.1f} tok/s | "
                  f"{'RICHTIG' if r['richtig'] else 'falsch  '} | {r['antwort'][:34]}",
                  flush=True)
        except urllib.error.URLError as e:
            r = {"ziel": groesse, "fehler": str(e)[:90], "richtig": False}
            print(f"  ziel {groesse:6} | FEHLER: {str(e)[:70]}", flush=True)
        except Exception as e:
            r = {"ziel": groesse, "fehler": str(e)[:90], "richtig": False}
            print(f"  ziel {groesse:6} | ABBRUCH: {str(e)[:70]}", flush=True)
        ergebnisse.append(r)

    ziel = Path(a.aus or f"reports/kontext_{a.modell}.json")
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(json.dumps({"modell": name, "ergebnisse": ergebnisse},
                               ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  geschrieben: {ziel}", flush=True)


if __name__ == "__main__":
    main()
