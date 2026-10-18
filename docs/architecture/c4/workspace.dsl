workspace "RutaSIT Arequipa" "Modelo C4 de la plataforma de seguimiento en tiempo real de los buses del Sistema Integrado de Transporte" {

    !identifiers hierarchical

    model {
        pasajero = person "Pasajero" "Persona que consulta dónde está su bus y cuánto demora en llegar."
        operador = person "Operador" "Personal del SIT que supervisa los buses y atiende las alertas."

        gps = softwareSystem "Dispositivos GPS de los buses" "Envían la posición de cada bus cada 10 segundos." "Externo"
        mapas = softwareSystem "Proveedor de mapas" "Entrega los mapas y calcula el tiempo de recorrido entre dos puntos." "Externo"

        rutasit = softwareSystem "RutaSIT" "Muestra la ubicación de los buses y el tiempo de llegada a cada paradero." {
            pwa = container "Aplicación web progresiva" "Mapa y consulta de llegadas para el pasajero; panel de alertas para el operador." "JavaScript + Service Worker" "Web Browser"
            api = container "API RutaSIT" "Monolito modular que recibe posiciones, calcula tiempos de llegada y genera alertas." "Python / Django" {
                ingesta = component "Módulo Ingesta" "Recibe la posición que envía cada bus." "Django app"
                seguimiento = component "Módulo Seguimiento" "Guarda los viajes y sus posiciones y controla su estado." "Django app"
                eta = component "Módulo ETA" "Calcula el tiempo de llegada a cada paradero." "Django app"
                alertas = component "Módulo Alertas" "Avisa al operador de desvíos y de buses sin señal." "Django app"
                rutas = component "Módulo Rutas" "Administra las rutas y los paraderos." "Django app"
            }
            db = container "Base de datos" "Rutas, paraderos, viajes, posiciones y alertas (un esquema por módulo)." "PostgreSQL + PostGIS" "Database"
            cache = container "Caché" "Última posición de cada bus y tiempos de llegada ya calculados." "Redis" "Cache"
        }

        pasajero -> rutasit "Consulta dónde está su bus y cuánto demora en llegar"
        operador -> rutasit "Supervisa los buses y atiende las alertas"
        gps -> rutasit "Envía la posición del bus" "HTTPS/JSON"
        rutasit -> mapas "Pide mapas y tiempos de recorrido" "HTTPS"

        pasajero -> rutasit.pwa "Usa" "HTTPS"
        operador -> rutasit.pwa "Usa" "HTTPS"
        rutasit.pwa -> rutasit.api "Hace consultas" "HTTPS/JSON (REST)"
        gps -> rutasit.api "Envía su posición" "HTTPS/JSON"
        rutasit.api -> rutasit.db "Lee y guarda viajes, posiciones y alertas" "SQL/TCP"
        rutasit.api -> rutasit.cache "Guarda y lee posiciones y tiempos de llegada" "Redis protocol"
        rutasit.pwa -> mapas "Carga los mapas" "HTTPS"
        rutasit.api -> mapas "Pide el tiempo de recorrido" "HTTPS/JSON"

        rutasit.pwa -> rutasit.api.seguimiento "Consulta la posición de los buses" "HTTPS/JSON"
        rutasit.pwa -> rutasit.api.eta "Consulta el tiempo de llegada" "HTTPS/JSON"
        rutasit.pwa -> rutasit.api.rutas "Consulta rutas y paraderos" "HTTPS/JSON"
        rutasit.pwa -> rutasit.api.alertas "Consulta las alertas (operador)" "HTTPS/JSON"
        gps -> rutasit.api.ingesta "Envía su posición" "HTTPS/JSON"
        rutasit.api.ingesta -> rutasit.api.seguimiento "Registra la posición del viaje" "Python (llamada interna)"
        rutasit.api.ingesta -> rutasit.api.alertas "Avisa si hay un desvío" "Python (llamada interna)"
        rutasit.api.eta -> rutasit.api.seguimiento "Busca los viajes activos y su última posición" "Python (llamada interna)"
        rutasit.api.eta -> rutasit.api.rutas "Lee los paraderos" "Python (llamada interna)"
        rutasit.api.eta -> rutasit.api.alertas "Avisa si los buses no tienen señal" "Python (llamada interna)"
        rutasit.api.alertas -> rutasit.api.seguimiento "Lee los viajes" "Python (llamada interna)"
        rutasit.api.seguimiento -> rutasit.api.rutas "Usa la ruta del viaje" "Python (llamada interna)"
        rutasit.api.seguimiento -> rutasit.db "Lee y guarda viajes y posiciones" "SQL/TCP"
        rutasit.api.rutas -> rutasit.db "Lee y guarda rutas y paraderos" "SQL/TCP"
        rutasit.api.alertas -> rutasit.db "Guarda las alertas" "SQL/TCP"
        rutasit.api.ingesta -> rutasit.cache "Guarda la última posición" "Redis protocol"
        rutasit.api.eta -> rutasit.cache "Guarda y lee tiempos de llegada" "Redis protocol"
        rutasit.api.eta -> mapas "Pide el tiempo de recorrido" "HTTPS/JSON"

        produccion = deploymentEnvironment "Producción" {
            celular = deploymentNode "Celular o PC del usuario" "" "Android / navegador web" {
                pwaInstancia = containerInstance rutasit.pwa
            }
            vps = deploymentNode "VPS en la nube" "" "Ubuntu 24.04, 2 vCPU, 4 GB RAM" {
                proxy = infrastructureNode "Nginx" "Recibe las peticiones y aplica HTTPS." "Nginx"
                monitoreo = infrastructureNode "Grafana" "Muestra el estado del servidor y de la aplicación." "Grafana"
                servidorApp = deploymentNode "Servidor de aplicación" "" "Django" {
                    apiInstancia = containerInstance rutasit.api
                }
                servidorBd = deploymentNode "Servidor de base de datos" "" "PostgreSQL + PostGIS" {
                    dbInstancia = containerInstance rutasit.db
                }
                servidorCache = deploymentNode "Servidor de caché" "" "Redis" {
                    cacheInstancia = containerInstance rutasit.cache
                }
            }
            celular.pwaInstancia -> vps.proxy "Envía las consultas" "HTTPS"
            vps.proxy -> vps.servidorApp.apiInstancia "Reenvía las peticiones" "HTTP"
            vps.servidorApp.apiInstancia -> vps.monitoreo "Envía métricas" "HTTP"
        }
    }

    views {
        systemContext rutasit "Contexto" "Nivel 1: RutaSIT y su entorno." {
            include *
            autolayout lr
        }
        container rutasit "Contenedores" "Nivel 2: contenedores de RutaSIT." {
            include *
            autolayout lr
        }
        component rutasit.api "Componentes" "Nivel 3: módulos de la API." {
            include *
            autolayout lr
        }
        dynamic rutasit.api "ConsultarLlegada" "Dinámico: el pasajero consulta cuándo llega el bus a su paradero." {
            rutasit.pwa -> rutasit.api.eta "Consulta el tiempo de llegada"
            rutasit.api.eta -> rutasit.api.seguimiento "Busca los viajes activos y su última posición"
            rutasit.api.eta -> mapas "Pide el tiempo de recorrido"
            rutasit.api.eta -> rutasit.api.alertas "Avisa si los buses no tienen señal"
            rutasit.api.eta -> rutasit.cache "Guarda el tiempo calculado"
            autolayout lr
        }
        deployment rutasit produccion "Despliegue" "Despliegue en producción (MVP)." {
            include *
            autolayout lr
        }

        styles {
            element "Person" {
                shape person
                background #08427B
                color #ffffff
            }
            element "Software System" {
                background #1168BD
                color #ffffff
            }
            element "Externo" {
                background #999999
            }
            element "Container" {
                background #438DD5
                color #ffffff
            }
            element "Component" {
                background #85BBF0
                color #000000
            }
            element "Database" {
                shape cylinder
            }
            element "Cache" {
                shape cylinder
            }
            element "Web Browser" {
                shape WebBrowser
            }
        }
    }
}
