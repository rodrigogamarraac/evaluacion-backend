## La parte mas orgullosa

La parte de la que estoy mas orgulloso es la implementacion de la disponibilidad de tickets usando la api. este se calcula en event_repository.py y se entrega al front en event_service.py

## Parte no muy feliz

La parte de la cual no estoy muy feliz es el hecho de que si un admin cambia un evento desde django admin, la api puede mostrar datos viejos por un tiempo por lo que redis cachea los datos y la info se actualiza recien cuando el TTL expira.
