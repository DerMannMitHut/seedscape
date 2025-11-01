# 🌱 Seedscape

**Seedscape** ist eine modulare Hexploration-Engine für Pen-and-Paper-Rollenspiele.  
Jede Welt entsteht **aus einem Seed** und wächst während des Spiels, **während die Spielleitung sie entdeckt** – Hex für Hex, Szene für Szene.

Seedscape verbindet klassische Tabletop-Exploration mit prozeduraler Generierung und (optional) KI-Unterstützung.  
Es läuft lokal auf dem Laptop der Spielleitung, während die Spieler nur Würfel, Papier und Neugier benötigen.

---

## ✨ Ziele und Grundideen

- **Unbekannte Welt:** Auch die SL kennt die Karte anfangs nicht.  
- **Deterministische Generierung:** Gleicher Seed → gleiche Welt.  
- **Regelbasierte Logik:** Biome, Features und Begegnungen werden aus konfigurierbaren YAML-Regeln erzeugt.  
- **LLM-Unterstützung (optional):** Für erzählerische Beschreibungen und improvisierte Details.  
- **Kampagnenfähig:** Mehrere unabhängige Welten / Kampagnen pro Benutzer.  
- **Einfachheit zuerst:** File-basierte Datenhaltung, keine externe Datenbank.  
- **Offline-fähig:** Alles läuft lokal – optional später Cloud- oder Server-Integration.

---

## 🧭 Projektstruktur

```
seedscape/
├── backend/              # FastAPI-Server (Hex-API, Kampagnenverwaltung)
│   ├── main.py
│   ├── api/
│   └── core/
│
├── frontend/             # Browser-UI für die Spielleitung
│   ├── index.html
│   ├── main.js
│   └── style.css
│
├── data/                 # Lokale Kampagnen- und Benutzerdaten
│   ├── users/
│   └── campaigns/
│
├── rules/                # Weltregeln (Biome, Encounters, Features)
│
├── scripts/              # CLI-Helfer und Startskripte
│
├── pyproject.toml
├── .env.example
└── README.md
```

---

## 🚀 Installation und Start

### Voraussetzungen
- Python ≥ 3.10  
- `pip` oder `uv` (empfohlen)

### Setup

```bash
git clone https://github.com/youruser/seedscape.git
cd seedscape/backend
pip install -r requirements.txt
```

Oder mit `pyproject.toml`:

```bash
pip install -e .
```

### Starten des Servers

```bash
uvicorn backend.main:app --reload
```

Danach im Browser öffnen:  
👉 [http://localhost:8000](http://localhost:8000)

Seedscape startet mit einer Standardkampagne `default` und generiert neue Hexe bei Bedarf automatisch.

---

## 🌍 API-Beispiele

### Alle Kampagnen anzeigen
```bash
GET /api/campaigns
```

### Neue Kampagne anlegen
```bash
POST /api/campaigns?name=myworld
```

### Hex laden oder generieren
```bash
GET /api/myworld/hex/A5
```

### Beispielausgabe
```json
{
  "id": "A5",
  "biome": "forest",
  "feature": "ruins",
  "encounter": "bandits",
  "discovered": true
}
```

---

## 🧠 Entwicklungsphasen

1. **Backend-Grundstruktur (Python/FastAPI)**  
2. **Browser-Visualisierung (Hex-Map, Kampagnenauswahl)**  
3. **LLM-Anbindung (lokal via Ollama oder API)**  
4. **Migration zu Go oder Rust**  
5. **Erweiterte Weltlogik, KI-Narration, Persistenzoptimierung**

---

## ⚙️ Datenhaltung (KISS-Prinzip)

Seedscape nutzt das Dateisystem als Speicher:
```
data/
└── campaigns/
    ├── default/
    │   ├── meta.json
    │   └── hexes/
    │       ├── A1.json
    │       ├── A2.json
    │       └── ...
```

Jedes Hex wird nur geladen, wenn es benötigt wird — kein Voll-Map-Laden, kein unnötiger Speicherverbrauch.

---

## 🔮 Zukunftsvision

- 🎲 **Spielmechaniken:** Reisekosten, Zufallsereignisse, Wetter, Ressourcen  
- 🧭 **Map-Editor:** Hexe aufdecken, kommentieren, exportieren  
- 🧠 **AI-Modus:** Lokale oder Cloud-LLMs für atmosphärische Texte  
- ☁️ **Mehrspieler- oder Remote-SL-Modus:** Kampagnen gemeinsam verwalten  
- 💾 **Seedscape Engine SDK:** für eigene Module und Regelsets  

---

## 📜 Lizenz

MIT License © 2025 Dom Didom

---

> *“A world doesn’t need to be planned.  
> It only needs to be seeded.”* 🌱
