# RutaSIT Arequipa — Laboratorio 04: Fundamentos de arquitectura de software

Construcción de Software · EPIS-UNSA · 2026-B · **Grupo 06**

## Integrantes

| Nombre | Rol en el laboratorio |
|--------|-----------------------|
| Estefanero Palma Rodrigo | Arquitecto/analista: drivers, matriz de decisión, ADR-001 |
| Sullca Mamani Mauro Snayder | Diagramador: Mermaid, PlantUML, vista de despliegue |
| Riveros Vilca Alberth Edwar | Verificador de IA y documentación: bitácora, ADR-002/003, README |

## Caso

RutaSIT Arequipa permite a los pasajeros ver en un mapa la ubicación de los buses del
Sistema Integrado de Transporte y el tiempo estimado de llegada a su paradero, y avisa
al operador de desvíos o congestión. 300 buses envían su posición cada 10 s. El atributo
de calidad crítico es el rendimiento en tiempo real: el ETA debe estar disponible en
≤ 15 s (p95). El MVP debe estar en producción en 1 mes con 3 developers y un solo VPS.

## Arquitectura elegida

Monolito modular en Django, con PostgreSQL + PostGIS como almacenamiento y Redis como
caché de posiciones y ETA. Un solo despliegue, cinco módulos (Ingesta, Seguimiento, ETA,
Alertas, Rutas) que se comunican únicamente por interfaces públicas.

Fuente del diagrama: [`docs/architecture/diagramas/arquitectura.mmd`](docs/architecture/diagramas/arquitectura.mmd)

```mermaid
flowchart TB
    BU["Bus (GPS)"]
    PA["Pasajero"]
    OP["Operador"]
    subgraph APP["RutaSIT — Monolito modular (un solo despliegue)"]
        API["Capa de presentación: API REST + PWA"]
        M1["Ingesta de<br/>posiciones"]
        M2["Seguimiento<br/>y mapa"]
        M3["Cálculo<br/>de ETA"]
        M4["Alertas"]
        M5["Rutas y<br/>paraderos"]
        INF["Capa de infraestructura: repositorios y adaptadores externos"]
    end
    DB[("PostgreSQL + PostGIS<br/>(un esquema por módulo)")]
    RD[("Redis<br/>(caché de posiciones y ETA)")]
    MP["Proveedor de mapas OSM"]
    BU & PA & OP --> API
    API --> M1 & M2 & M3 & M4 & M5
    M1 & M2 & M3 & M4 & M5 --> INF
    INF --> DB
    INF --> RD
    INF --> MP
    classDef mod fill:#E8F5E9,stroke:#2E7D32,color:#000
    classDef ext fill:#F2F2F2,stroke:#7F7F7F,color:#000,stroke-dasharray: 4 3
    classDef usr fill:#FDEDEC,stroke:#C8310E,color:#000
    class M1,M2,M3,M4,M5 mod
    class MP ext
    class BU,PA,OP usr
```

Trazabilidad con los drivers: M1 = RF-01, M2 = RF-02 y RF-06, M3 = RF-03, M4 = RF-04,
M5 = RF-05.

## Decisiones arquitectónicas

| ADR | Decisión | Autor |
|-----|----------|-------|
| [ADR-001](docs/architecture/adr/001-estilo-arquitectonico.md) | Estilo arquitectónico: monolito modular | Rol A |
| [ADR-002](docs/architecture/adr/002-protocolo-ingesta-gps.md) | Protocolo de ingesta GPS: HTTPS POST en lugar de MQTT | Rol C |
| [ADR-003](docs/architecture/adr/003-actualizacion-tiempo-real.md) | Actualización en tiempo real: polling 10 s sobre Redis | Rol C |

## Documentación de arquitectura

- [Drivers y escenarios de calidad](docs/architecture/drivers.md) — RF, atributos de calidad, restricciones y escenarios QA
- [Matriz de decisión](docs/architecture/matriz-decision.md) — alternativas, pesos y cálculo ponderado
- [Bitácora de uso de IA](docs/architecture/bitacora-ia.md) — interacciones y decisiones verificadas durante los laboratorios

### Reto opcional B: documentación viva de diagramas

La [Action de diagramas](.github/workflows/diagramas.yml) se ejecuta en cada push y
pull request. Valida `docs/architecture/c4/workspace.dsl`, vuelve a exportar las cinco
vistas a PlantUML y Mermaid y regenera sus PNG en `docs/architecture/c4/img/`. Si la
validación o el render falla, la ejecución queda fallida; en pushes, la Action publica
los artefactos generados cuando detecta cambios.

## Reflexión sobre el uso de la IA

La IA nos aceleró el arranque, pero no reemplazó la decisión arquitectónica. El caso más
claro fue la recomendación de Claude en el prompt 1: propuso un monolito modular orientado
a eventos con Redis y WebSocket/SSE, y la justificaba con que un canal persistente ahorraba
datos al pasajero. Ninguna de las dos cosas se apoyaba en algo medido, y la primera chocaba
con R-02 y ponía en riesgo R-01. Cuando le pedimos la crítica adversarial en el prompt 2,
la misma herramienta se contradijo y retiró su recomendación. Ahí entendimos que aceptar
la primera respuesta de una IA sin contrastarla con los drivers del proyecto es el error
más probable, y que hay que leer siempre la crítica además de la propuesta. DeepSeek
tTambién falló: su diagrama Mermaid renderizaba bien pero dibujaba dependencias directas
entre módulos, rompiendo el aislamiento que acordamos en ADR-001. Y en el prompt 5, Gemini
afirmó datos muy concretos sobre el SIT de Arequipa (fechas, nombres de apps, ausencia de
GTFS) sin citar ninguna fuente verificable, por lo que decidimos no depender de ninguna API
externa. En resumen, nos sirvió como generador de alternativas y de estructura, pero cada
recomendación tuvo que filtrarse contra nuestras restricciones, y los tres casos de
desviación fueron distintos: sobrearquitectura, diagramas que rompen una decisión ya tomada,
y datos inventados con apariencia de certeza.

## Diseño UML (Lab 05)

Diseño detallado del módulo de seguimiento y tiempo de llegada (historia HU-01).

### Máquina de estados de Viaje
```mermaid
stateDiagram-v2
    [*] --> PROGRAMADO : programar()
    PROGRAMADO --> EN_RUTA : iniciar() [hora de salida cumplida]
    EN_RUTA --> DESVIADO : marcarDesviado() [a mas de 150 m de la ruta]
    DESVIADO --> EN_RUTA : reanudar() [vuelve a la ruta]
    EN_RUTA --> DETENIDO : marcarDetenido() [velocidad 0 por mas de 3 min]
    DETENIDO --> EN_RUTA : reanudar() [velocidad mayor a 0]
    EN_RUTA --> FINALIZADO : finalizar() [llego al ultimo paradero]
    DESVIADO --> FINALIZADO : finalizar() [el operador cierra el viaje]
    DETENIDO --> FINALIZADO : finalizar() [el operador cierra el viaje]
    FINALIZADO --> [*]
```

### Documentos y diagramas
- [Historia de usuario](docs/design/historia.md)
- [Diagrama de clases](docs/design/clases.puml) · [imagen](docs/design/img/clases-eta.png)
- [Diagrama de secuencia](docs/design/secuencia-consultar-eta.puml) · [imagen](docs/design/img/secuencia-consultar-eta.png)
- [Máquina de estados](docs/design/estados-viaje.mmd) · [imagen](docs/design/img/estados-viaje.png)
- [Diagrama de actividades](docs/design/actividades-detectar-desvio.puml) · [imagen](docs/design/img/actividades-detectar-desvio.png)
- [Diagrama de paquetes](docs/design/paquetes.puml) · [imagen](docs/design/img/paquetes.png)
- [Round-trip](docs/design/round-trip.md) · [Consistencia](docs/design/consistencia.md) · [Bitácora de IA](docs/design/bitacora-ia.md)
- [ADR-004](docs/architecture/adr/004-ingesta-coordina-seguimiento-y-alertas.md)

## Arquitectura C4 (Lab 06)

Modelo C4 de RutaSIT Arequipa escrito en Structurizr DSL (`docs/architecture/c4/workspace.dsl`). Todas las vistas salen de ese único archivo.

### Contexto del sistema (nivel 1)
```mermaid
graph LR
  linkStyle default fill:#ffffff

  subgraph diagram ["System Context View: RutaSIT"]
    style diagram fill:#ffffff,stroke:#ffffff

    1["<div style='font-weight: bold'>Pasajero</div><div style='font-size: 70%; margin-top: 0px'>[Person]</div><div style='font-size: 80%; margin-top:10px'>Persona que consulta dónde<br />está su bus y cuánto demora<br />en llegar.</div>"]
    style 1 fill:#08427b,stroke:#052e56,color:#ffffff
    2["<div style='font-weight: bold'>Operador</div><div style='font-size: 70%; margin-top: 0px'>[Person]</div><div style='font-size: 80%; margin-top:10px'>Personal del SIT que<br />supervisa los buses y atiende<br />las alertas.</div>"]
    style 2 fill:#08427b,stroke:#052e56,color:#ffffff
    3["<div style='font-weight: bold'>Dispositivos GPS de los buses</div><div style='font-size: 70%; margin-top: 0px'>[Software System]</div><div style='font-size: 80%; margin-top:10px'>Envían la posición de cada<br />bus cada 10 segundos.</div>"]
    style 3 fill:#999999,stroke:#6b6b6b,color:#ffffff
    4["<div style='font-weight: bold'>Proveedor de mapas</div><div style='font-size: 70%; margin-top: 0px'>[Software System]</div><div style='font-size: 80%; margin-top:10px'>Entrega los mapas y calcula<br />el tiempo de recorrido entre<br />dos puntos.</div>"]
    style 4 fill:#999999,stroke:#6b6b6b,color:#ffffff
    5["<div style='font-weight: bold'>RutaSIT</div><div style='font-size: 70%; margin-top: 0px'>[Software System]</div><div style='font-size: 80%; margin-top:10px'>Muestra la ubicación de los<br />buses y el tiempo de llegada<br />a cada paradero.</div>"]
    style 5 fill:#1168bd,stroke:#0b4884,color:#ffffff

    1-. "<div>Consulta dónde está su bus y<br />cuánto demora en llegar</div><div style='font-size: 70%'></div>" .->5
    2-. "<div>Supervisa los buses y atiende<br />las alertas</div><div style='font-size: 70%'></div>" .->5
    3-. "<div>Envía la posición del bus</div><div style='font-size: 70%'>[HTTPS/JSON]</div>" .->5
    5-. "<div>Pide mapas y tiempos de<br />recorrido</div><div style='font-size: 70%'>[HTTPS]</div>" .->4

  end
```

### Vistas del modelo
- [Contexto (nivel 1)](docs/architecture/c4/img/structurizr-Contexto.png)
- [Contenedores (nivel 2)](docs/architecture/c4/img/structurizr-Contenedores.png)
- [Componentes (nivel 3)](docs/architecture/c4/img/structurizr-Componentes.png)
- [Dinámica: consultar la llegada del bus](docs/architecture/c4/img/structurizr-ConsultarLlegada.png)
- [Despliegue en producción](docs/architecture/c4/img/structurizr-Despliegue.png)

### Documentos
- [Inventario](docs/architecture/c4/inventario.md) · [Comparación](docs/architecture/c4/comparacion.md) · [Revisión con la lista oficial](docs/architecture/c4/revision-c4.md) · [Explicación para público no técnico](docs/architecture/c4/explicacion.md) · [Bitácora de IA](docs/architecture/c4/bitacora-ia.md)
- Nivel 4 (código): [clases.puml](docs/design/clases.puml) del Laboratorio 05.
