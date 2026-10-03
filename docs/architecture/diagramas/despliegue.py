from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import Users
from diagrams.onprem.network import Nginx, Internet
from diagrams.programming.framework import Django
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.monitoring import Grafana
from diagrams.generic.device import Mobile

graph_attr = {"fontsize": "20", "bgcolor": "white", "pad": "0.3"}

with Diagram("RutaSIT - Vista de despliegue", filename="img/despliegue",
            show=False, direction="LR", graph_attr=graph_attr,
            outformat="png"):
    pasajeros = Users("Pasajeros y\noperadores")
    pwa = Mobile("PWA en\ncelular")
    gps = Mobile("GPS de\n300 buses")

    with Cluster("Servidor en la nube (VPS)"):
        proxy = Nginx("Nginx\n(HTTPS)")
        with Cluster("Monolito modular"):
            app = Django("Django API\n(5 módulos)")
        cache = Redis("Redis\n(caché de posiciones)")
        db = PostgreSQL("PostgreSQL\n+ PostGIS")
        mon = Grafana("Monitoreo")

    mapas = Internet("Proveedor de mapas\n(OSM, externo)")

    pasajeros >> pwa >> Edge(label="HTTPS") >> proxy
    gps >> Edge(label="POST posición\ncada 10 s") >> proxy
    proxy >> app
    app >> Edge(label="lee/escribe") >> cache
    app >> Edge(label="persiste") >> db
    pwa >> Edge(label="teselas", style="dashed") >> mapas
    app >> Edge(style="dotted") >> mon