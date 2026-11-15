"""Compara las 3 ejecuciones (ejecucion1..3) de H1, H7 y H9. Uso: python3 prompts/no-determinismo/comparar.py > prompts/no-determinismo/comparacion.txt"""
import json,pathlib,difflib,itertools
base=pathlib.Path(__file__).parent
for caso in ("H1","H7","H9"):
    rs=[json.loads((base/f"ejecucion{i}"/f"{caso}.txt").read_text()) for i in (1,2,3)]
    txt=[(base/f"ejecucion{i}"/f"{caso}.txt").read_text() for i in (1,2,3)]
    print("==",caso)
    for i,r in enumerate(rs,1):
        print(f" ejec{i}: invest_ok={r['invest_ok']} escenarios={len(r['escenarios'])} tipos={[e['tipo'] for e in r['escenarios']]} preguntas={len(r['preguntas'])} chars={len(txt[i-1])}")
        print("   titulos:",[e['titulo'] for e in r['escenarios']])
    print(" iguales byte a byte:", txt[0]==txt[1]==txt[2],
          "| similitud texto (1v2,1v3,2v3):",[round(difflib.SequenceMatcher(None,a,b).ratio(),2) for a,b in itertools.combinations(txt,2)])
