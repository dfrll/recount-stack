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
    docker compose build --no-cache loader server app
    # Build nginx after app because it uses COPY --from=app_dist
    docker compose build --no-cache nginx

# Prod build: builds images as-is (use committed poetry.lock)
build-prod:
    docker compose build --no-cache loader server app
    docker compose build --no-cache nginx

# Bring stack up (dev uses dev build)
up-dev: build-dev
    docker compose up

# Bring up the full production stack without updating poetry.lock files
up-prod: build-prod
    docker compose up

# Shut down and clean volumes
down:
    docker compose down -v
