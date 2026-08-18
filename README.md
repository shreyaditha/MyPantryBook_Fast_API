# 🍲 My Pantry Book

> **A warm, hand-illustrated, cookbook-style recipe & pantry manager for South Indian home cooking.**

Keep track of your pantry ingredients, browse traditional South Indian recipes, and instantly discover *"What can I cook right now?"* based on what's on your kitchen shelf.

---

## ✨ Features

- 📖 **Editorial Cookbook Aesthetic**: Designed to feel like flipping through a homely handwritten recipe notebook — featuring warm terracotta and cream paper tones, Fraunces serif display typography, and Caveat handwritten accents.
- 🫙 **Pantry Shelf Manager**: Log ingredient quantities and track expiry dates with visual freshness indicators (*Fresh*, *Soon*, *Urgent*).
- 🍛 **South Indian Recipe Collection**: Pre-loaded with 26 authentic recipes (Masala Dosa, Plain Idli, Sambar, Rasam, Medu Vada, Appam, Avial, Bisi Bele Bath, etc.).
- 💡 **"What Can I Cook?" Matcher**: Automatically cross-references your pantry against every recipe to rank what you can make tonight with match percentage progress bars.
- 🔔 **Smart Expiry Alerts**: Receive automatic reminders for ingredients nearing their expiry date.
- 🚀 **Serverless-Ready Deployment**: Configured out of the box for instant Vercel deployment with automatic `/tmp` database failover and auto-seeding.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.14+, [FastAPI](https://fastapi.tiangolo.com/)
- **Database & ORM**: SQLite, [SQLAlchemy 2.0 (Asyncio)](https://www.sqlalchemy.org/), `aiosqlite`
- **Frontend / Templating**: Jinja2 HTML Templates, Vanilla CSS Design System (Custom Variables, Google Fonts `Fraunces`, `Lora`, `Caveat`)
- **Deployment**: Vercel Serverless Python Runtime (`@vercel/python`)

---

## 🚀 Quick Start (Local Development)

### 1. Clone & Setup Environment

```bash
git clone https://github.com/shreyaditha/MyPantryBook_Fast_API.git
cd MyPantryBook_Fast_API
```

### 2. Create Virtual Environment & Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Seed Database

To seed the database with 26 traditional South Indian recipes and ingredients:

```bash
python -m seeds.seed_full
```

### 4. Run Development Server

```bash
python -m uvicorn app.main:app --reload --port 8000
```

Open your browser and navigate to:
- **Application**: [http://localhost:8000](http://localhost:8000)
- **Interactive API Documentation (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📂 Project Structure

```
fast_api_pantry/
├── api/
│   └── index.py             # Vercel Serverless entry point
├── app/
│   ├── api/                 # FastAPI REST API & HTML View Routers
│   │   ├── ingredients.py   # Ingredient CRUD endpoints
│   │   ├── notifications.py # Notification endpoints
│   │   ├── pantry.py        # Pantry item CRUD endpoints
│   │   ├── recipes.py       # Recipe CRUD & suggestion logic
│   │   └── views.py         # Jinja2 Page Rendering views
│   ├── core/                # Core Config & Database Sessions
│   │   ├── config.py        # Pydantic Settings & Serverless detection
│   │   └── database.py      # Async SQLAlchemy Engine & Auto-seeding
│   ├── models/              # SQLAlchemy Database Models
│   ├── schemas/             # Pydantic Request/Response Schemas
│   ├── static/              # CSS Stylesheets & Static Uploads
│   │   └── css/styles.css   # Homely Cookbook CSS Design System
│   ├── templates/           # Jinja2 HTML Templates
│   │   ├── base.html        # Main Layout & Navigation
│   │   ├── index.html       # Cookbook Title Landing Page
│   │   ├── pantry.html      # Ledger Pantry Shelf Page
│   │   ├── recipes.html     # Recipe Index Cards Page
│   │   ├── recipe_detail.html# Open-Book Recipe View Page
│   │   └── suggestions.html # "What Can I Cook?" Matcher Page
│   └── main.py              # FastAPI Application Factory & Lifespan
├── seeds/                   # Recipe Seed Data & Importer
│   ├── seed_full.py
│   └── south_indian_recipes_seed.json
├── requirements.txt         # Python Package Dependencies
├── vercel.json              # Vercel Deployment Configuration
└── README.md
```

---

## 🌐 API Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Homely Cookbook Title Page |
| `GET` | `/pantry` | Pantry Shelf Ledger Page |
| `GET` | `/recipes` | Recipe Index Page (with filters) |
| `GET` | `/recipes/{id}` | Open-Book Recipe Detail View |
| `GET` | `/suggestions` | Pantry Recipe Matcher Page |
| `GET` | `/api/recipes/suggestions` | JSON API for recipe pantry match ranking |
| `GET` | `/api/pantry` | JSON API for user pantry items |
| `POST` | `/api/recipes` | Create a new recipe |
| `POST` | `/api/pantry` | Add ingredient to pantry shelf |

---

## ☁️ Deployment (Vercel)

This repository includes a pre-configured `vercel.json` and Python entrypoint (`api/index.py`).

1. Push your code to GitHub.
2. Import the repository into [Vercel](https://vercel.com).
3. Vercel will automatically detect `api/index.py` and deploy using `@vercel/python`.
4. Database tables and 26 South Indian recipes will automatically seed on first invocation.

---

## 📄 License

Distributed under the MIT License. Built with ❤️ for home cooking.
