workspace "RutaSIT Arequipa" "Modelo C4 de la plataforma de seguimiento en tiempo real de los buses del Sistema Integrado de Transporte" {

    !identifiers hierarchical

    model {
        pasajero = person "Pasajero" "Persona que consulta dónde está su bus y cuánto demora en llegar."
        operador = person "Operador" "Personal del SIT que supervisa los buses y atiende las alertas."

        gps = softwareSystem "Dispositivos GPS de los buses" "Envían la posición de cada bus cada 10 segundos." "Externo"
        mapas = softwareSystem "Proveedor de mapas" "Entrega los mapas y calcula el tiempo de recorrido entre dos puntos." "Externo"

        rutasit = softwareSystem "RutaSIT" "Muestra la ubicación de los buses y el tiempo de llegada a cada paradero."

        pasajero -> rutasit "Consulta dónde está su bus y cuánto demora en llegar"
        operador -> rutasit "Supervisa los buses y atiende las alertas"
        gps -> rutasit "Envía la posición del bus" "HTTPS/JSON"
        rutasit -> mapas "Pide mapas y tiempos de recorrido" "HTTPS"
    }

    views {
        systemContext rutasit "Contexto" "Nivel 1: RutaSIT y su entorno." {
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
