# gLLM — Local LLM Platform with RAG & Fine-Tuning

A full-stack platform for deploying a local Large Language Model with Retrieval-Augmented Generation (RAG) and LoRA fine-tuning capabilities. Built as a senior design project.

## Architecture

```
                         +-------------------+
                         |   React Frontend  |
                         |   (Vite + TS)     |
                         +--------+----------+
                                  |
                         +--------v----------+
                         |   FastAPI Server   |
                         |   (port 8001)      |
                         +--+-----+-----+----+
                            |     |     |
              +-------------+  +--+--+  +-------------+
              |                |     |                 |
     +--------v--------+  +---v---+ +-------v-------+ |
     | Chainlit Chat UI |  | Auth  | | Admin / Docs  | |
     | (/gllm)          |  | JWT   | | Fine-Tune API | |
     +--------+---------+  +-------+ +---------------+ |
              |                                         |
     +--------v---------+    +----------+    +----------v---------+
     | vLLM Inference   |    |PostgreSQL|    |   ChromaDB         |
     | (port 8000)      |    | (5432)   |    |   (port 8003)      |
     | Qwen3-VL-8B      |    +----------+    | Vector embeddings  |
     | + LoRA adapters   |                   +--------------------+
     +-------------------+
```

## Features

### Chat with Local LLM
- Streaming chat via Chainlit UI mounted at `/gllm`
- Vision support (image upload + analysis) with multimodal models
- Conversation history and session management

### RAG Pipeline
- Upload PDF, text, code, and markdown files during chat
- Automatic chunking with language-aware splitting (Python, Markdown, etc.)
- ChromaDB vector storage with per-user document isolation
- Top-5 semantic retrieval with source attribution
- Document management API (`GET /docs/`, `DELETE /docs/{file_id}`)
- Duplicate detection and 50MB file size limit

### LoRA Fine-Tuning
- Unsloth + QLoRA training script with YAML configuration
- Docker-based training runner (`run_finetune.sh`)
- vLLM hot-swapping: load/unload LoRA adapters at runtime without restart
- API endpoints for adapter management (`/finetune/adapters`)
- Optional HuggingFace Hub push for trained adapters

### Authentication & Access Control
- JWT-based authentication (signup/login/token refresh)
- Four roles: `admin`, `fine_tuner`, `normal`, `unauthorized`
- New users start as `unauthorized` — admin approves via dashboard
- Role-based route protection on both frontend and backend
- Admin console for user management (approve, deny, role assignment)

### Admin Dashboard
- React 19 + TypeScript + Tailwind CSS + Shadcn/UI
- Stats overview (total users, active users, pending approvals)
- User approval workflow with one-click approve/deny
- Dark/light theme toggle
- Responsive sidebar navigation

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM Inference | vLLM (OpenAI-compatible API) |
| Chat UI | Chainlit 2.9.6 |
| Backend | FastAPI + Uvicorn |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS |
| Database | PostgreSQL 16 (SQLAlchemy + Alembic) |
| Vector DB | ChromaDB |
| Fine-Tuning | Unsloth + PEFT (QLoRA) |
| Auth | PyJWT + Argon2 password hashing |
| Package Manager | uv (Python), npm (Node) |
| Containerization | Docker Compose |
| CI/CD | GitHub Actions |

## Project Structure

```
gLLM/
├── src/
│   ├── server.py                # FastAPI app entry point
│   ├── chainlit-app.py          # Chat logic, RAG integration, auth
│   ├── Dockerfile               # Multi-stage build (frontend + backend)
│   ├── routers/
│   │   ├── authrouter.py        # POST /auth/signup, /login, GET /auth/me
│   │   ├── adminrouter.py       # CRUD /admin/users (admin-only)
│   │   ├── docsrouter.py        # GET/DELETE /docs (user documents)
│   │   └── finetuningrouter.py  # GET/POST /finetune/adapters
│   ├── services/
│   │   ├── authservice.py       # JWT, password hashing, RBAC
│   │   ├── adminservice.py      # User management queries
│   │   ├── promptservice.py     # System prompt configuration
│   │   └── ragutils/
│   │       ├── ingestion.py     # File validation, chunking, storage
│   │       ├── retrieval.py     # Semantic search, context formatting
│   │       └── vector_db.py     # ChromaDB abstraction layer
│   ├── schema/
│   │   ├── models.py            # SQLAlchemy ORM (User, Thread, Step, etc.)
│   │   └── alembic/             # Database migrations
│   ├── core/
│   │   └── config.py            # Pydantic Settings (env vars)
│   └── pyproject.toml           # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── pages/               # Login, Signup, MainMenu, AdminPanel
│   │   ├── contexts/            # AuthContext, ThemeContext
│   │   ├── services/api.ts      # API client with JWT management
│   │   └── models/User.ts       # Role enum aligned with backend
│   └── package.json
├── finetune/
│   ├── finetune.py              # Unsloth training script
│   ├── config.yaml              # Training hyperparameters
│   └── run_finetune.sh          # Docker runner for training
├── vllmconfig/
│   ├── vllminit.sh              # Start vLLM (base model)
│   └── vllminit_lora.sh         # Start vLLM with LoRA support
├── tests/                       # Unit and integration tests
├── docker-compose.yaml          # PostgreSQL + ChromaDB
└── .github/workflows/ci.yaml    # CI pipeline
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- NVIDIA GPU with drivers installed
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Node.js 20+
- HuggingFace account with access token

### 1. Clone and configure

```bash
git clone https://github.com/gongjiawei105/gLLM.git
cd gLLM
cp src/.env.example src/.env
# Edit src/.env with your credentials
```

### 2. Start databases

```bash
docker compose up -d
```

### 3. Install dependencies and apply migrations

```bash
cd src
uv sync
source .venv/bin/activate
cd schema && alembic upgrade head && cd ..
```

### 4. Build frontend

```bash
cd ../frontend
npm install
npm run build
cd ..
```

### 5. Start vLLM inference server

```bash
# Set HF_TOKEN and MODEL in src/.env first
cd vllmconfig
./vllminit.sh          # Base model only
# OR
./vllminit_lora.sh     # With LoRA adapter support
```

### 6. Start the application

```bash
cd src
fastapi dev server.py --port 8001
```

Visit `http://localhost:8001` for the dashboard, or `http://localhost:8001/gllm` for direct chat.

### Fine-Tuning (optional)

```bash
# Edit finetune/config.yaml with your dataset and model settings
cd finetune
./run_finetune.sh config.yaml
```

Then load the adapter via the API or dashboard.

## Environment Variables

See [src/.env.example](src/.env.example) for all options:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `AUTH_SECRET` | JWT signing secret (32+ chars) |
| `CHAINLIT_AUTH_SECRET` | Chainlit session secret |
| `VLLM_BASE_URL` | vLLM server URL (default: `http://localhost:8000`) |
| `CORS_ORIGINS` | Allowed origins, comma-separated |
| `BUCKET_NAME` | AWS S3 bucket for file storage |
| `HF_TOKEN` | HuggingFace access token |
| `MODEL` | Model name (default: `Qwen/Qwen3-VL-8B-Instruct`) |

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/signup` | No | Create account |
| POST | `/auth/login` | No | Get JWT token |
| GET | `/auth/me` | Bearer | Current user profile |
| GET | `/admin/users/` | Admin | List all users |
| PUT | `/admin/users/{id}` | Admin | Update user role |
| DELETE | `/admin/users/{id}` | Admin | Delete user |
| GET | `/docs/` | Bearer | List user's documents |
| DELETE | `/docs/{file_id}` | Bearer | Delete document |
| GET | `/finetune/adapters` | Fine-tuner+ | List LoRA adapters |
| POST | `/finetune/adapters/load` | Fine-tuner+ | Load adapter into vLLM |
| POST | `/finetune/adapters/unload` | Fine-tuner+ | Unload adapter |
| GET | `/health` | No | Health check |

## Contributing

See [DEV_GUIDE.md](DEV_GUIDE.md) for setup instructions.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes and add tests
4. Submit a Pull Request

## License

This project is part of a senior design course. See repository for license details.
