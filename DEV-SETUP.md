# Dev Setup

## Repo layout

All three repos should be cloned as siblings:

```
etlas/
├── vms-ac-server/     Spring Boot backend (Java 11, port 8082)
├── vms-ac-ui-next/    Next.js frontend (port 3000)
└── vms-ac-pi/         Raspberry Pi services (Python, port 5000)
                       Also contains Makefile and this file
```

## First-time setup

From the `vms-ac-pi` directory:

```bash
make setup
```

This installs frontend and Pi dependencies, then reminds you to copy the config templates.

### Copy config templates

**Frontend:**
```bash
cp ../vms-ac-ui-next/.env.development.example ../vms-ac-ui-next/.env.development.local
```

**Pi code:**
```bash
cp src/var.example.py src/var.py
```

Both default to `http://localhost:8082` (backend on same machine). Edit if your backend is elsewhere.

## Running for development

Run all `make` commands from the `vms-ac-pi` directory.

### Quick start (one terminal)

```bash
make dev
```

This runs both the backend and frontend in a single terminal. Ctrl+C stops both.

### Separate terminals (cleaner logs)

If you prefer separate output for each:

**Terminal 1 — Backend:**
```bash
make backend-dev
```
Starts Spring Boot on `http://localhost:8082` with H2 in-memory database.

**Terminal 2 — Frontend:**
```bash
make frontend-dev
```
Starts Next.js on `http://localhost:3000`.

---

Open `http://localhost:3000` in your browser.

## Frontend without backend

If you only need the UI and don't want to run the backend:

1. Edit `../vms-ac-ui-next/.env.development.local`:
   ```
   NEXT_PUBLIC_USE_API=false
   ```
2. Run `make frontend-dev`

The frontend will use the fake data defined in `src/api/api-config.js`.

## Common make targets

| Command | What it does |
|---------|-------------|
| `make backend-dev` | Run backend with H2 (in-memory DB) |
| `make backend-dev-pg` | Run backend with local PostgreSQL |
| `make backend-build` | Build backend JAR (skip tests) |
| `make backend-test` | Run backend tests |
| `make frontend-install` | Install frontend npm packages |
| `make frontend-dev` | Run frontend dev server |
| `make frontend-build` | Build frontend for production |
| `make frontend-lint` | Lint frontend code |
| `make pi-install` | Install Pi Python dependencies |
| `make dev` | Run backend + frontend together (Ctrl+C kills both) |
| `make setup` | First-time dependency install |

## Using local PostgreSQL instead of H2

The default `dev` profile uses H2 (in-memory, resets on restart). To use PostgreSQL locally:

1. Start a PostgreSQL instance (e.g. via Docker):
   ```bash
   docker run -d --name etlas-pg \
     -e POSTGRES_DB=testdb \
     -e POSTGRES_USER=postgres \
     -e POSTGRES_PASSWORD=postgres \
     -p 5432:5432 \
     postgres:13
   ```

2. Run the backend with the `devpostgres` profile:
   ```bash
   make backend-dev-pg
   ```

   This connects to `localhost:5432/testdb` (configured in `application-devpostgres.properties`).

## Notes

- **Pi code on Mac/PC:** The Pi code (`vms-ac-pi`) depends on `pigpio` and `RPi.GPIO` which only work on a Raspberry Pi. You can still edit and review the code, but running `api.py` locally will fail on GPIO calls.
- **H2 console:** When running with `dev` profile, the H2 database console is available at `http://localhost:8082/h2-console` (JDBC URL: `jdbc:h2:mem:testdb`, username: `Admin`, password: `123456`).
- **Swagger:** API docs are at `http://localhost:8082/swagger-ui-custom.html`.
