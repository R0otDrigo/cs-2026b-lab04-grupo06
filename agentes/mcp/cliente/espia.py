"""'Espía' de stdio: se ubica entre el host y el servidor MCP, reenvía los mensajes JSON-RPC
sin modificarlos y los registra en un archivo JSONL (como un Wireshark mínimo).
Uso: python cliente/espia.py servidor_mcp/rutasit_mcp.py
El archivo de salida es trazas/mcp_trafico.jsonl o el que indique la variable MCP_TRAZA."""
import json, os, pathlib, subprocess, sys, threading, time

RAIZ = pathlib.Path(__file__).resolve().parents[1]
LOG = pathlib.Path(os.environ.get("MCP_TRAZA", RAIZ / "trazas" / "mcp_trafico.jsonl"))
LOG.parent.mkdir(parents=True, exist_ok=True)
t0, candado = time.perf_counter(), threading.Lock()
servidor = subprocess.Popen([sys.executable, *sys.argv[1:]], stdin=subprocess.PIPE, stdout=subprocess.PIPE)


def registrar(direccion, linea):
    try:
        msg = json.loads(linea)
    except ValueError:
        return
    with candado, open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps({"t": round(time.perf_counter() - t0, 4), "dir": direccion, "msg": msg},
                           ensure_ascii=False) + "\n")


def servidor_a_host():
    for linea in servidor.stdout:
        registrar("servidor->host", linea)
        sys.stdout.buffer.write(linea)
        sys.stdout.buffer.flush()


threading.Thread(target=servidor_a_host, daemon=True).start()
for linea in sys.stdin.buffer:
    registrar("host->servidor", linea)
    servidor.stdin.write(linea)
    servidor.stdin.flush()
servidor.stdin.close()
servidor.wait()
