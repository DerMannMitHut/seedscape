# SeedScape 🌱

**SeedScape** is a modular backend project that unifies experimental tools, scripts, and data sources under one framework.  
It uses **Poetry** for dependency management and a **Makefile** to standardize all common tasks.

---

## 🚀 Quick Start

### 1. Installation

```bash
make install
```

Sets up an isolated virtual environment and installs all dependencies via Poetry.  
If Poetry is not yet installed, it will be installed automatically.

### 2. Start Development Mode

```bash
make dev
```

Runs the development server with automatic reload.  
Logs, hot reload, and local data are kept outside version control by default.

### 3. Normal Server Run

```bash
make run
```

Starts the server without debug or hot-reload features (e.g., for tests or container builds).

### 4. Tests & Code Checks

```bash
make test
```

Runs unit tests, static type checks, and linters.  
Details (e.g., pytest, mypy, ruff) are defined in the Makefile.

### 5. Clean / Reset

```bash
make clean
```

Removes local artifacts such as `.venv`, temporary files, or build folders.  
Useful when resetting or rebuilding the environment from scratch.

---

## ⚙️ Configuration

Local settings (e.g., ports, API keys, or paths) are stored in a `.env` file.

Copy the example configuration:

```bash
cp .env.example .env
```

Then adjust the values in `.env` to fit your environment.

---

## 🧩 Project Philosophy

- **Stable interfaces:** Internal implementation changes should not require README updates.  
- **Automated workflows:** All major actions are encapsulated via `make`.  
- **Consistent environment:** Poetry manages dependencies; no global installs are needed.  
- **Separation of code & data:** User data (e.g., saves, logs, temporary files) should never be version-controlled.

---

## 📁 Directories (for orientation only)

The exact structure depends on the implementation.  
Typically, the project includes areas such as:

- **src/** – Source code  
- **rules/** – Configuration or gameplay data  
- **scripts/** – Utility scripts  
- **data/** – Runtime data (ignored by Git)

---

## 🧪 Development & Contributions

Pull requests, issues, and ideas are welcome.  
Please follow the existing code style (validated through `make test`).

---

## 🤖 CI & Automation

- GitHub Actions runs lint, type-checks, and tests on pushes/PRs.  
- The workflow pre-creates Poetry config (`~/.config/pypoetry/config.toml`) to use in-project virtualenvs.  
- Single entrypoint: `make install` installs Python deps (Poetry) and frontend tooling (npm).  
- Node is set up (v20) and npm caches are reused; Python venv is cached by lockfile.  
- CI commands mirror local use: `make install`, then `make test`.

---

## 🌾 Campaign Biomes (data-driven)

- Each campaign defines its own biomes and styles in `data/campaigns/<name>/`.
- Required in `meta.json`:
  - `biomes`: list of biome keys (strings)
  - `biomes_css`: relative CSS file (e.g., `biomes.css`)
- CSS is served at `/api/campaigns/<name>/assets/biomes.css` and loaded by the frontend.
- Example: see `data/campaigns/example/meta.json` and `data/campaigns/example/biomes.css`.


## 📜 License

This project is licensed under the **MIT License**.  
© 2025 Der Mann mit Hut

---

> *“A world doesn’t need to be planned.  
> It only needs to be seeded.”* 🌱
