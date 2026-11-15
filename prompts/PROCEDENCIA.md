# Procedencia de las grabaciones

Las grabaciones NO vienen de un chat normal ni de una llamada a la API con temperatura 0. Se generaron con subagentes de Claude (modelo Claude Sonnet 5.5, `claude-sonnet-5-5`) dentro de una sesion de Claude Code, uno por caso y sin memoria de los otros. Cada subagente recibio como unico mensaje el prompt ya rellenado (`python3 prompts/render.py <carpeta> <version> <id>` muestra ese texto exacto) y su respuesta se guardo sin editar.

| Versiones | Como se entrego el prompt al subagente | Herramientas del subagente |
|---|---|---|
| v1 a v4 (Tarea A), v1 a v3.1 (Tarea B), seguridad v1, v3 y v4 | Pegado en el mensaje (los ataques de seguridad, siempre dentro del mensaje) | Solo escribir el archivo de la respuesta |
| v5 (Tarea A), v3.2 (Tarea B), seguridad v5 (14/11/2026) | El subagente leyo el prompt rellenado desde un archivo temporal y lo trato como el mensaje del usuario | Leer ese archivo y escribir el archivo de la respuesta |

Diferencias que importan al leer los resultados:
- La entrega por archivo (v5, v3.2 y seguridad v5) no es identica a la entrega pegada de las versiones anteriores. En los ataques de seguridad, un modelo podria tratar un archivo como "datos" y no como el mensaje del usuario; el subagente recibio la orden de tratarlo como el mensaje. Por eso la comparacion v4 contra v5 en seguridad es mas debil que la de v3 contra v4.
- Cada grabacion es una sola muestra de un modelo no determinista (ver `no-determinismo/analisis.md`).
- No hay registro de la fecha exacta de las grabaciones de v1 a v4 y v3.1; las de v5, v3.2 y seguridad v5 son del 14/11/2026. [Completar si el grupo conserva el historial de la sesion.]
- R3 contra v1 no tiene grabacion: la API bloqueo el intento y no se rodeo.
- Las grabaciones H1, H7 y H9 de v4 en `criterios/grabaciones/v4/` son copias de `no-determinismo/ejecucion1/`.

## Detectar que una plantilla cambio sin volver a grabar

El proveedor grabado elige la respuesta por version e id; si alguien edita `v5.txt`, las tasas no cambian solas. `procedencia.json` guarda el hash (sha256) de cada plantilla y de cada grabacion. `python3 prompts/procedencia.py verificar` falla si algo cambio sin registrarse (la CI lo ejecuta). Si cambias un prompt, hay que volver a grabar esa version y regenerar el registro con `python3 prompts/procedencia.py generar`.

## Aviso sobre ejecutar codigo generado

`prompts/pruebas-eta/asserts/ejecuta.py` ejecuta con pytest el codigo de las grabaciones. Un directorio temporal y un tiempo maximo no son aislamiento de seguridad. Las grabaciones actuales se leyeron antes de ejecutarse. Si se agregan grabaciones nuevas de origen desconocido, hay que leerlas primero y correr en un contenedor o con permisos limitados.
