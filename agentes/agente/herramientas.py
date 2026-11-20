"""Herramientas del agente. Cada una es una función pequeña, con descripción y parámetros explícitos.
Todas operan DENTRO del directorio de trabajo (sandbox)."""
import ast, datetime, pathlib, subprocess, re, sys

BASICAS = ("listar_archivos", "leer_archivo", "buscar", "ejecutar_pruebas", "editar_archivo",
           "ver_cambios", "ejecutar_comando")
EXTENDIDAS = ("mapa_repo", "anotar", "leer_notas")          # E4: herramienta nueva y memoria de notas


class Herramientas:
    def __init__(self, raiz: str, extendidas: bool = False):
        self.raiz = pathlib.Path(raiz).resolve()
        self.extendidas = extendidas

    # --- utilidades ---
    def _ruta(self, ruta: str) -> pathlib.Path:
        p = (self.raiz / ruta).resolve()
        if self.raiz not in p.parents and p != self.raiz:
            raise PermissionError(f"Ruta fuera del sandbox: {ruta}")
        return p

    def catalogo(self) -> dict:
        """Descripción de las herramientas que se envía al modelo (como en un MCP server)."""
        c = {
            "listar_archivos": "listar_archivos(carpeta='.'): lista los archivos .py y .md",
            "leer_archivo": "leer_archivo(ruta): devuelve el contenido con números de línea",
            "buscar": "buscar(patron): busca una expresión regular en los archivos .py",
            "ejecutar_pruebas": "ejecutar_pruebas(): ejecuta pytest y devuelve el resumen",
            "editar_archivo": "editar_archivo(ruta, antes, despues): reemplaza un fragmento exacto (una sola vez)",
            "ver_cambios": "ver_cambios(): muestra el diff respecto de la versión original",
            "ejecutar_comando": "ejecutar_comando(comando): ejecuta un comando de shell (sujeto a la política)",
        }
        if self.extendidas:
            c.update({
                "mapa_repo": ("mapa_repo(carpeta='src'): devuelve, sin leer el código completo, cada módulo .py "
                              "con sus clases, métodos y funciones (firma y número de línea). Parámetro: carpeta "
                              "(texto, ruta relativa dentro del sandbox). Úsela antes de leer archivos."),
                "anotar": ("anotar(texto): agrega una línea a notas.md (hipótesis, archivos revisados, pendientes). "
                           "Parámetro: texto (máx. 300 caracteres). Devuelve 'OK: nota N'."),
                "leer_notas": "leer_notas(): devuelve las notas guardadas en notas.md o '(sin notas)'.",
            })
        return c

    # --- herramientas ---
    def listar_archivos(self, carpeta="."):
        base = self._ruta(carpeta)
        return "\n".join(sorted(str(p.relative_to(self.raiz).as_posix()) for p in base.rglob("*")
                                if p.suffix in (".py", ".md") and "__pycache__" not in p.parts))

    def leer_archivo(self, ruta):
        lineas = self._ruta(ruta).read_text(encoding="utf-8").splitlines()
        return "\n".join(f"{i:3d}| {l}" for i, l in enumerate(lineas, 1))

    def buscar(self, patron):
        rx, hallazgos = re.compile(patron), []
        for p in sorted(self.raiz.rglob("*.py")):
            for i, l in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                if rx.search(l):
                    hallazgos.append(f"{p.relative_to(self.raiz).as_posix()}:{i}: {l.strip()}")
        return "\n".join(hallazgos) or "(sin resultados)"

    def ejecutar_pruebas(self):
        # sys.executable: el mismo intérprete que ejecuta el agente ("python" no existe en algunas máquinas).
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider"],
                           cwd=self.raiz, capture_output=True, text=True, timeout=120)
        salida = (r.stdout + r.stderr).strip().splitlines()
        fallos = [l for l in salida if l.startswith(("FAILED", "E "))][:6]
        return "\n".join(fallos + salida[-1:])

    def editar_archivo(self, ruta, antes, despues):
        p = self._ruta(ruta)
        texto = p.read_text(encoding="utf-8")
        if texto.count(antes) != 1:
            return f"ERROR: el fragmento aparece {texto.count(antes)} veces; debe aparecer exactamente 1"
        p.write_text(texto.replace(antes, despues), encoding="utf-8")
        return f"OK: {ruta} modificado"

    def ver_cambios(self, original="../trabajo_original"):
        import difflib
        base, salida = self._ruta_libre(original), []
        for p in sorted(self.raiz.rglob("*.py")):
            rel = p.relative_to(self.raiz); q = base / rel
            a = q.read_text(encoding="utf-8").splitlines() if q.exists() else []
            salida += difflib.unified_diff(a, p.read_text(encoding="utf-8").splitlines(),
                                           f"a/{rel.as_posix()}", f"b/{rel.as_posix()}", lineterm="", n=1)
        return "\n".join(salida) or "(sin cambios)"

    def _ruta_libre(self, ruta):
        return (self.raiz / ruta).resolve()

    def ejecutar_comando(self, comando):
        r = subprocess.run(comando, shell=True, cwd=self.raiz, capture_output=True, text=True, timeout=60)
        return (r.stdout + r.stderr).strip()[-2000:]

    # --- E4: herramienta nueva ---
    def mapa_repo(self, carpeta="src"):
        base, lineas = self._ruta(carpeta), []
        for p in sorted(base.rglob("*.py")):
            if "__pycache__" in p.parts:
                continue
            try:
                arbol = ast.parse(p.read_text(encoding="utf-8"))
            except SyntaxError as e:
                lineas.append(f"{p.relative_to(self.raiz).as_posix()}: ERROR de sintaxis en la línea {e.lineno}")
                continue
            elementos = []
            for nodo in arbol.body:
                if isinstance(nodo, ast.ClassDef):
                    metodos = [f"{m.name}({', '.join(a.arg for a in m.args.args if a.arg != 'self')})"
                               for m in nodo.body if isinstance(m, ast.FunctionDef) and not m.name.startswith("__")]
                    elementos.append(f"  class {nodo.name} (l.{nodo.lineno}): " + (", ".join(metodos) or "-"))
                elif isinstance(nodo, ast.FunctionDef):
                    elementos.append(f"  def {nodo.name}({', '.join(a.arg for a in nodo.args.args)}) (l.{nodo.lineno})")
            if elementos:
                lineas.append(p.relative_to(self.raiz).as_posix())
                lineas += elementos
        return "\n".join(lineas) or "(sin módulos)"

    # --- E4: memoria de notas (pizarra) ---
    def anotar(self, texto):
        texto = str(texto).strip().replace("\n", " ")
        if not texto:
            return "ERROR: la nota está vacía"
        if len(texto) > 300:
            return "ERROR: la nota supera 300 caracteres; resúmala"
        notas = self.raiz / "notas.md"
        previas = notas.read_text(encoding="utf-8").splitlines() if notas.exists() else ["# Notas del agente"]
        n = sum(1 for l in previas if l.startswith("- "))
        hora = datetime.datetime.now().strftime("%H:%M:%S")
        notas.write_text("\n".join(previas + [f"- [{hora}] {texto}"]) + "\n", encoding="utf-8")
        return f"OK: nota {n + 1}"

    def leer_notas(self):
        notas = self.raiz / "notas.md"
        return notas.read_text(encoding="utf-8").strip() if notas.exists() else "(sin notas)"
