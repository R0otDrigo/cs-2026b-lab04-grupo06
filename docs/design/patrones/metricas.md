# Métricas antes / después (Lab 07)

> Medición real con `radon 6.0.1` y `metricas_equiv.py` (misma regla McCabe).
> - Antes: `radon cc -s -a src/rutasit/antes/`
> - Después: `radon cc -s -a src/rutasit/{gps,eta,estados,eventos,ia,servicio}.py`
> - SLOC: `radon raw -s` sobre los 6 módulos del Lab 07.
>
> El repositorio conserva los módulos del Lab 05 (`dominio.py`, `puertos.py`,
> `adaptadores.py`, `servicios.py`) y sus 13 pruebas; no se incluyen en la métrica
> del Lab 07.

| Métrica | Antes | Después |
|---|---|---|
| Complejidad de `consultar_eta` | **22 (D)** | **3 (A)** |
| Complejidad máxima de cualquier método | 22 | 5 |
| Complejidad promedio | 6,25 (B) | 1,64 (A) |
| Líneas de código (SLOC) | 85 | 266 |
| Archivos | 1 | 6 (`gps`, `eta`, `estados`, `eventos`, `ia`, `servicio`) |
| Agregar un operador GPS o un algoritmo de ETA | modificar el servicio | registrar una clase en la fábrica |
| Pruebas | 13 passed + 1 xfailed (caracterización sobre `antes`) | 40 passed + 1 xfailed (Lab 07); 53 passed + 1 xfailed con las 13 del Lab 05 |

## Trade-off (5 a 8 líneas)
Ganamos que `consultar_eta` bajó de 22 a 3 y que ya no se modifica el servicio para agregar un operador GPS, un algoritmo
de ETA o un suscriptor; además encontramos un error real (la versión antes consumía el GPS antes de validar el algoritmo).
Costó pasar de 85 a 266 líneas y de 1 a 6 archivos: hay más indirección y el equipo debe conocer los patrones.
La versión antes habría sido suficiente si RutaSIT tuviera un solo operador GPS, un solo algoritmo y nunca usara IA.
Los patrones se justifican por los cambios previstos (más operadores del SIT, nuevos algoritmos de ETA, más avisos).
La suite del Lab 07 queda en 40 passed + 1 xfailed; al conservar las 13 pruebas del Lab 05, la suite completa da
53 passed + 1 xfailed.

## Salida real de radon (resumen)

```text
$ radon cc -s -a src/rutasit/antes/
...
8 blocks (classes, functions, methods) analyzed.
Average complexity: B (6.25)

$ radon cc -s -a src/rutasit/gps.py src/rutasit/eta.py src/rutasit/estados.py \
    src/rutasit/eventos.py src/rutasit/ia.py src/rutasit/servicio.py
...
113 blocks (classes, functions, methods) analyzed.
Average complexity: A (1.6371681415929205)

$ radon cc -s src/rutasit/servicio.py
    M 62:4 ServicioEta.consultar_eta - A (3)
```

## Patrón rechazado
- **Singleton** para `FabricaGps`: introduce estado global y no permite inyectar GPS simulados en pruebas.
- **Abstract Factory**: no existen familias de objetos que deban crearse juntos.
