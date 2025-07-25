# recount-stack

A full-stack web application for visualizing and querying the [recount3](https://rna.recount.bio/) RNA-seq dataset.

This project includes:
- **PostgreSQL** database to store public exon, junction, and annotation data
- **Flask server** REST API with server-side pagination and filtering
- **Vue 3 + ag-Grid frontend** for interactive data exploration
- **Nginx reverse proxy** for serving the frontend and API routing

## Getting Started

Make sure you have [Docker](https://docs.docker.com/get-docker/) and [Just](https://just.systems/) installed.

### Development

To update dependencies, build, and start all services:

```bash
just up-dev
```

This will:
- Update Python dependencies (`poetry update`)
- Build the application stack
- Start all services via Docker Compose
- Initialize the dataset metadata with [pyrecount](https://github.com/dfrll/pyrecount)

### Tear Down

To stop services and remove volumes (e.g. PostgreSQL data):

```bash
just down
```

## Services & Architecture

| Service | Purpose                                                               | Technology       |
| ------- | --------------------------------------------------------------------- | ---------------- |
| db      | PostgreSQL 15 database initialized from `infra/postgres/init.sql`     | PostgreSQL 15    |
| loader  | Python service that populates project metadata (runs once at startup) | Python 3.11+      |
| server  | Flask API server using Gunicorn for production deployment             | Flask + Gunicorn |
| app     | Vue 3 frontend compiled into static assets and served by NGINX        | Vue 3 + Vite     |
| nginx   | Public reverse proxy that serves frontend and forwards API requests   | Nginx            |

## Ports & Networking

| Service (Container)           | Host → Container Port   | Purpose                          |
|-------------------------------|------------------------|----------------------------------|
| nginx (`recount-stack-nginx-1`)  | 80 → 80                | Public frontend + API            |
| server (`recount-stack-server-1`)| (internal only) → 8080 | Flask API (Gunicorn)             |
| db (`recount-stack-db-1`)        | (internal only) → 5432 | PostgreSQL (internal in prod)    |

## Volumes

- pgdata: Persists PostgreSQL data between runs
- init.sql: Initializes the recount3 schema on first boot

## Environment Secrets

Docker secrets are used for managing credentials (to be replaced with [Vault](https://www.hashicorp.com/en/products/vault)):

Secrets are mounted at runtime inside each container at `/run/secrets/`.

Docker Compose does not encrypt secrets, they are just mounted from files and not committed to version control.

### Required Secrets

Create these files in your `secrets/` directory:
```
secrets/
├── db.txt           # PostgreSQL password
├── loader.env       # Loader secrets/env
└── server.env       # Server secrets/env
```
