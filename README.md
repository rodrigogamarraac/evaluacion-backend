# Backend

**Opción A — Conciertos / Venta de Entradas para Eventos**.

Este repositorio implementa el backend para el frontend estático proporcionado. Todo el stack se ejecuta con un solo comando usando Docker Compose:

- Nginx en el puerto 80
- Django Admin detrás de Gunicorn
- FastAPI detrás de Gunicorn/Uvicorn workers
- PostgreSQL como única fuente de datos
- Redis para cache de la API
- Frontend estático servido en `/`

## Cómo ejecutar el proyecto

```bash
cp .env.example .env

docker compose up --build
```

Después de iniciar el proyecto, abrir:

- Frontend: `http://localhost/`
- Django Admin: `http://localhost/admin/`
- Listado de FastAPI: `http://localhost/api/v1/events/`
- Esquema OpenAPI: `http://localhost/api/openapi.json`
- Prueba de 404: `http://localhost/apiaaaaaa`

Credenciales por defecto del administrador desde `.env.example`:

- usuario: `admin`
- contraseña: `admin123`

## Contrato de la API

El frontend proporcionado llama a los siguientes endpoints:

GET /api/v1/events/?q=&sort=&page=&page_size=
GET /api/v1/events/{id}
GET /api/v1/healthz

### Django Admin

Django se utiliza únicamente para el panel administrativo. Los usuarios administradores pueden gestionar venues, eventos, tipos de ticket, órdenes y tickets. El administrador de eventos permite editar `TicketType` de forma inline, y el administrador de órdenes permite editar `Ticket` de forma inline.

### Esquema de base de datos

Todas las tablas del dominio se almacenan dentro del schema `content`. Las entidades del dominio utilizan UUID como claves primarias e incluyen los campos de timestamp `created_at` y `modified_at`.

### API pública con FastAPI

FastAPI es de solo lectura. No depende de Django en tiempo de ejecución; únicamente lee desde PostgreSQL y utiliza Redis para cache.

### Lógica de negocio

La disponibilidad se calcula de la siguiente manera:

available = capacidad del tipo de ticket - tickets activos pagados

A nivel de evento:

event available = suma de capacidades de los tipos de ticket - cantidad de tickets activos de órdenes pagadas

El cálculo se realiza en una sola consulta SQL usando agregación, lo cual permite obtener una lectura consistente bajo el comportamiento normal de lectura de PostgreSQL. Las escrituras se realizan mediante Django Admin, por lo que la API solo necesita ser correcta bajo lecturas concurrentes.

### Estrategia de cache

FastAPI almacena en Redis las respuestas del listado de eventos y del detalle de eventos.

Las claves de cache incluyen query, sort, page, page size, event id y timezone. El tiempo de vida del cache se controla mediante `CACHE_TTL_SECONDS`.

Si Redis no está disponible, la capa de cache captura el error y FastAPI continúa sirviendo datos desde PostgreSQL. Esto se conoce como degradación controlada o graceful degradation.

Como las escrituras se realizan desde Django Admin y FastAPI es de solo lectura, la invalidación del cache usa expiración por TTL corto. Esta estrategia es simple y evita acoplar FastAPI con señales internas de Django.

### Estrategia de búsqueda

La búsqueda pública utiliza `ILIKE` de PostgreSQL sobre el título del evento, la descripción del evento, el nombre del venue y la ciudad del venue. Elasticsearch no se utiliza intencionalmente.

### Manejo de zona horaria

Los endpoints de listado y detalle de eventos aceptan un query parameter llamado `timezone`. Por defecto utiliza UTC. Las fechas de respuesta se convierten a la zona horaria solicitada.

Ejemplo:

GET /api/v1/events/?timezone=America/La_Paz

## SOLID / Estructura del proyecto

FastAPI está dividido en capas claras:

- `api/v1/events.py`: solo maneja las rutas
- `services/event_service.py`: lógica de negocio y composición de respuestas
- `repositories/event_repository.py`: SQL y acceso a la base de datos
- `cache/redis_cache.py`: implementación del cache con Redis
- `schemas/event_schema.py`: esquemas de respuesta con Pydantic

Las abstracciones se proveen mediante protocolos:

- `EventRepositoryProtocol`
- `CacheClientProtocol`

Las dependencias se inyectan mediante `Depends` de FastAPI y constructores de servicios.

## Tests

Ejecutar tests de Django:

docker compose exec django pytest

Ejecutar tests de FastAPI:

docker compose exec fastapi pytest

Desde un entorno local con las dependencias instaladas, también se puede ejecutar:

pytest
