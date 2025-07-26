# Show available commands
default:
    @just --list

# Update poetry.lock for loader
[working-directory: 'services/loader']
update-lock-loader:
    poetry update

# Update poetry.lock for server
[working-directory: 'services/server']
update-lock-server:
    poetry update

# Update all poetry.lock files
update-locks: update-lock-loader update-lock-server

# Dev build: updates locks before building
build-dev: update-locks
    docker compose build --no-cache

# Prod build: builds images as-is (use committed poetry.lock)
build-prod:
    docker compose build --no-cache

# Bring stack up (dev uses dev build)
up-dev: build-dev
    docker compose up

# Bring up the full production stack without updating poetry.lock files
up-prod: build-prod
    docker compose up

# Shut down and clean volumes
down:
    docker compose down -v
