# Historia de usuario — RutaSIT Arequipa

HU-01: Como pasajero, quiero consultar el tiempo estimado de llegada del bus a mi
       paradero para decidir si lo espero o busco otra ruta.

## Criterios de aceptación

- Dado un bus en ruta que envió su posición hace menos de 30 s, cuando consulto la
  llegada a mi paradero, entonces veo los minutos estimados y la hora de la última
  actualización, y el dato está disponible en 15 s o menos desde que llegó la posición.
- Dado que ningún bus de la ruta envía su posición hace más de 30 s, cuando consulto la
  llegada, entonces veo "ETA no disponible" junto con la última posición marcada
  "sin señal", y el sistema avisa al operador.
- Dado un paradero sin buses en servicio, cuando lo consulto, entonces veo el mensaje
  "No hay buses en servicio hacia este paradero".
