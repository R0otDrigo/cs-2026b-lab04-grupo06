# Métricas antes / después (Lab 07)

> Tabla generada con `radon cc -s -a src/rutasit/antes/ ` y `radon cc -s -a src/rutasit/`.
> Valores de este documento calculados con `metricas_equiv.py` (misma regla McCabe). **Vuelva a correr radon real y pegue su salida.**

| Métrica | Antes | Después |
|---|---|---|
| Complejidad de `consultar_eta` | **22 (D)** | **5 (A)** |
| Complejidad máxima de cualquier método | 22 | 5 |
| Complejidad promedio | 6,25 (B) | 1,89 (A) |
| Líneas de código (SLOC) | 85 | 266 |
| Archivos | 1 | 6 (`gps`, `eta`, `estados`, `eventos`, `ia`, `servicio`) |
| Agregar un operador GPS o un algoritmo de ETA | modificar el servicio MD | registrar una clase en la fábrica MD|

## Trade-off (5 a 8 líneas)
Ganamos que `consultar_eta` bajó de 22 a 3 y que ya no se modifica el servicio para agregar un operador GPS, un algoritmo
de ETA o un suscriptor; además encontramos un error real (la versión antes consumía el GPS antes de validar el algoritmo).
Costó pasar de 85 a 266 líneas y de 1 a 6 archivos: hay más indirección y el equipo debe conocer los patrones.
La versión antes habría sido suficiente si RutaSIT tuviera un solo operador GPS, un solo algoritmo y nunca usara IA.
Los patrones se justifican por los cambios previstos (más operadores del SIT, nuevos algoritmos de ETA, más avisos).

## Patrón rechazado
- **Singleton** para `FabricaGps`: introduce estado global y no permite inyectar GPS simulados en pruebas.
- **Abstract Factory**: no existen familias de objetos que deban crearse juntos.
