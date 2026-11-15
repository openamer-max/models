"""Misst einen Adapter direkt (ohne GGUF/Ollama) auf beiden Saetzen.

Fuer 0,6B ist das der schnellste Weg: Basis laden, Adapter drauf, 65 Fragen
durchlaufen. Kein Merge, keine Quantisierung, keine Ollama-Schleife.

Auswertung identisch zu bench_fair: require ist eine Liste von Gruppen, forbid
eine Liste von Gruppen, Wortgrenzen sind Pflicht.

Aufruf:
    python measure_adapter.py --adapter out_watch10/adapter --tag watch10
"""
import argparse
import os
import json
import re
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

# Datenverzeichnis: ueber OPENAMER_TRAIN_DIR setzbar, sonst das aktuelle.
BASIS = Path(os.environ.get("OPENAMER_TRAIN_DIR", Path.cwd()))
SYSTEM = ("Du bist OpenAmer, ein lokaler KI-Assistent. Du antwortest knapp und "
          "sachlich auf Deutsch. Wenn du etwas nicht weisst, sagst du das.")


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
            return False, "fehlt:" + "/".join(g)[:36]
    for g in gruppen(fall.get("forbid")):
        for phrase in g:
            if re.search(r"\b" + re.escape(phrase.lower()) + r"\b", t):
                return False, "verboten:" + phrase[:24]
    return True, ""


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--adapter", default=None,
                   help="Adapter-Ordner; ohne Angabe wird die reine Basis gemessen")
    p.add_argument("--basis", default="Qwen/Qwen3-0.6B")
    p.add_argument("--tag", required=True)
    a = p.parse_args()

    tok = AutoTokenizer.from_pretrained(a.basis)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    modell = AutoModelForCausalLM.from_pretrained(
        a.basis, dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None)
    if a.adapter:
        modell = PeftModel.from_pretrained(modell, str(BASIS / a.adapter))
        print(f"  Adapter geladen: {a.adapter}")
    else:
        print("  ohne Adapter: reine Basis zum Vergleich")
    modell.eval()
    print(f"  GPU: {torch.cuda.is_available()}")

    def frage(text):
        msgs = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": text}]
        geruest = tok.apply_chat_template(msgs, tokenize=False,
                                          add_generation_prompt=True,
                                          enable_thinking=False)
        ids = tok(geruest, return_tensors="pt").to(modell.device)
        with torch.no_grad():
            aus = modell.generate(**ids, max_new_tokens=160, do_sample=False,
                                  temperature=None, top_p=None, top_k=None,
                                  pad_token_id=tok.eos_token_id)
        neu = aus[0][ids["input_ids"].shape[1]:]
        return tok.decode(neu, skip_special_tokens=True).strip()

    ergebnisse = {}
    for satz, datei in (("v2", BASIS / "data/testset_pro_v2.json"),
                        ("allgemein", BASIS / "benchmarks/allgemein.json"),
                        ("a2", BASIS / "benchmarks/allgemein_a2.json")):
        roh = json.loads(datei.read_text(encoding="utf-8"))
        faelle = roh if isinstance(roh, list) else roh["faelle"]
        treffer, details = 0, []
        for i, fall in enumerate(faelle, 1):
            text = frage(fall["q"])
            ok, grund = bewerte(text, fall)
            treffer += int(ok)
            details.append({"i": i, "q": fall["q"], "ok": ok, "grund": grund,
                            "antwort": text[:200]})
            print(f"   [{satz} {i:2}/{len(faelle)}] {'OK ' if ok else 'daneben'} "
                  f"{fall['q'][:40]}" + ("" if ok else f"  ({grund})"), flush=True)
        ergebnisse[satz] = {"treffer": treffer, "von": len(faelle),
                            "prozent": round(100 * treffer / len(faelle), 1),
                            "details": details}
        print(f"  -> {satz}: {treffer}/{len(faelle)} ({ergebnisse[satz]['prozent']} %)",
              flush=True)

    (BASIS / "reports").mkdir(exist_ok=True)
    ziel = BASIS / f"reports/adapter_{a.tag}.json"
    ziel.write_text(json.dumps(ergebnisse, ensure_ascii=False, indent=1), encoding="utf-8")
    print("  gespeichert:", ziel)


if __name__ == "__main__":
    main()
