# Revisión con la lista oficial de C4 — RutaSIT Arequipa

Se aplicó la lista de revisión (Tabla 3 de la guía) a las cinco vistas. Una parte se revisó a mano mirando las imágenes y otra con el script `revisar_vistas.py` (36 elementos y 42 relaciones revisados).

| Vista | General (título, alcance y leyenda) | Elementos (nombre, tipo, descripción y tecnología) | Relaciones (etiqueta, dirección y protocolo) | Evidencia y observaciones |
|-------|-------------------------------------|----------------------------------------------------|---------------------------------------------|---------------------------|
| Contexto | Sí | Sí | Sí | Título "Nivel 1" y leyenda. Las flechas de las personas no llevan protocolo: a nivel 1 no se exige |
| Contenedores | Sí | Sí | Sí | Cada caja indica tecnología y cada flecha su protocolo (HTTPS/JSON, SQL/TCP, Redis protocol) |
| Componentes | Sí | Sí | Sí | Los 5 módulos coinciden con paquetes.puml. Las llamadas internas dicen "Python (llamada interna)" |
| Dinámica | Sí | Sí | Sí | 5 pasos numerados, todos de relaciones que existen en el modelo |
| Despliegue | Sí | Sí | **No del todo** | Aparece una flecha directa de la PWA a la API que no pasa por Nginx. Viene de la relación del modelo; la ruta real sí pasa por Nginx. Se deja documentado |

## Hallazgos del segundo revisor (script con IA)

| Vista | Hallazgo | Verificación del equipo |
|-------|----------|-------------------------|
| Contexto | 2 relaciones (Pasajero y Operador hacia RutaSIT) no indican tecnología ni protocolo | **Falso positivo.** En el nivel 1 no se exigen tecnologías para las personas |
| Todas | Todas tienen título y leyenda | Correcto (cumple) |
| Todas | Los 36 elementos tienen nombre y descripción; los contenedores y componentes tienen tecnología | Correcto (cumple) |
| Contenedores | Ver también en `comparacion.md`: en el export de PlantUML los sistemas externos se ven igual que los internos | Correcto. Es una limitación del export. Se documenta |
