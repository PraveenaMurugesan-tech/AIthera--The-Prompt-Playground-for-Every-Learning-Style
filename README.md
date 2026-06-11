# AIthera — The Prompt Playground for Every Learning Style

AIthera is a multi-model educational AI platform designed to generate personalized learning prompts through a Multi-Model AI Council. Instead of providing static, one-size-fits-all answers, AIthera constructs adaptive prompts tailored to each learner's preferred cognitive style.

---

## 📖 Table of Contents
1. [Project Overview](#-project-overview)
2. [Architecture](#-architecture)
3. [Environment Variables](#-environment-variables)
4. [Database & Migrations](#-database--migrations)
5. [Backend Setup & Installation](#-backend-setup--installation)
6. [Authentication API Endpoints](#-authentication-api-endpoints)
7. [Prompt Request System](#-prompt-request-system)
8. [Current Project Progress](#-current-project-progress)
9. [Future Roadmap](#-future-roadmap)

---

## 🌟 Project Overview

Traditional AI prompt generation often relies on a single model, which can lead to generic or one-dimensional outputs. AIthera solves this by leveraging an ensemble of top-tier AI providers (GPT, Claude, Gemini, and DeepSeek) acting as a **Multi-Model AI Council**. 

Each council member contributes specialized strengths to craft the final educational prompt:
*   **GPT** (OpenAI) — *Educational Structure Expert* (Layout, Scaffolding, and Organization)
*   **Claude** (Anthropic) — *Deep Reasoning Expert* (Conceptual Depth, Critical Reflection)
*   **Gemini** (Google) — *Visual Learning Expert* (Analogies, Imagery, and Spatial Prompts)
*   **DeepSeek** — *Technical Logic Expert* (Step-by-step progressions, Code/Math validation)

The resulting prompts are synthesized and scored to ensure maximum educational effectiveness, clarity, structure, and style personalization.

---

## 🏗️ Architecture

AIthera follows a modular pipeline from user input to the final generated prompt:

```
User Request
    │
    ▼
Input Processor (Validation & Normalization)
    │
    ▼
Learning Style Engine (Applies rules for: Visual, Conversational, etc.)
    │
    ▼
AI Council Orchestration (Concurrent queries)
    ├── OpenAI Adapter (GPT)
    ├── Anthropic Adapter (Claude)
    ├── Google Adapter (Gemini)
    └── DeepSeek Adapter (DeepSeek)
    │
    ▼
Response Normalizer (Parsing & Semantic Alignment)
    │
    ▼
Consensus Builder (Aggregating strengths & merging drafts)
    │
    ▼
Prompt Scorer (Scoring categories 0-20, overall 0-100)
    │
    ▼
Explanation Generator (Transparent pedagogical rationale)
    │
    ▼
Final persisting & Output (Persisted PromptRequest & ConsensusResult)
```

---

## 🔑 Environment Variables

Create a `.env` file in the root of the project to configure database access, server environments, and JWT authentication:

```env
# Database configuration
DATABASE_URL=mysql+pymysql://root:root@localhost:3306/aithera

# JWT Security
SECRET_KEY=your-highly-secure-jwt-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS Allowed Origins (comma-separated)
FRONTEND_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

---

## 🗄️ Database & Migrations

AIthera utilizes **SQLAlchemy** for ORM and **Alembic** to manage database schema updates.

### Migration Commands

1.  **Run migrations to set up or update your database schema to the latest version:**
    ```bash
    alembic upgrade head
    ```
2.  **Generate a new migration script automatically after modifying models:**
    ```bash
    alembic revision --autogenerate -m "Add new features table"
    ```
3.  **Roll back the last migration step:**
    ```bash
    alembic downgrade -1
    ```
4.  **Roll back all migrations to base status:**
    ```bash
    alembic downgrade base
    ```

---

## 🚀 Backend Setup & Installation

### Prerequisites
*   Python 3.10 or higher
*   MySQL/MariaDB (or a configured SQLite fallback)
*   Redis (optional, for caching)

### Steps

1.  **Clone the Repository & Navigate to Directory:**
    ```bash
    git clone https://github.com/PraveenaMurugesan-tech/AIthera--The-Prompt-Playground-for-Every-Learning-Style.git
    cd AIthera--The-Prompt-Playground-for-Every-Learning-Style
    ```

2.  **Create and Activate a Virtual Environment:**
    ```bash
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    # macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure local `.env`:**
    Rename or create `.env` as detailed in the Environment Variables section.

5.  **Run Database Migrations:**
    ```bash
    alembic upgrade head
    ```

6.  **Start the Local Development Server:**
    ```bash
    python -m uvicorn src.main:app --reload
    ```
    The server will run on `http://127.0.0.1:8000`. You can inspect the interactive OpenAPI documentation at `http://127.0.0.1:8000/docs`.

---

## 🔒 Authentication API Endpoints

All endpoints have a `/auth` prefix. Token authentication follows the OAuth2 Password Bearer specification (bearer JWT tokens).

### 1. Register User
*   **Path:** `POST /auth/register`
*   **Description:** Creates a new user account.
*   **Request Body (`application/json`):**
    ```json
    {
      "email": "student@example.com",
      "password": "securepassword123"
    }
    ```
*   **Response (`201 Created`):**
    ```json
    {
      "id": 1,
      "email": "student@example.com"
    }
    ```

### 2. Login User
*   **Path:** `POST /auth/login`
*   **Description:** Authenticates user credentials and returns a JWT access token.
*   **Request Body (`application/x-www-form-urlencoded`):**
    *   `username`: "student@example.com"
    *   `password`: "securepassword123"
*   **Response (`200 OK`):**
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer"
    }
    ```

### 3. Get Authenticated User Context
*   **Path:** `GET /auth/me`
*   **Description:** Returns details of the currently authenticated user.
*   **Request Headers:**
    *   `Authorization: Bearer <access_token>`
*   **Response (`200 OK`):**
    ```json
    {
      "id": 1,
      "email": "student@example.com"
    }
    ```

---

## 📝 Prompt Request System

The prompt request system allows authenticated users to submit educational topics alongside target learning styles and difficulties. The system routes this configuration to the AI Council, which aggregates, processes, and persists the generated output.

### Learning Style Support
*   `visual` — Uses diagram-oriented cues, conceptual flowcharts, and visual metaphors.
*   `conversational` — Dialogue/Q&A style, storytelling, and reflective checkpoints.
*   `step_by_step` — Clear sequential phases, prerequisites, and milestone tasks.
*   `exam_focused` — High-yield point summaries, definitions, and mock quizzes.
*   `research_oriented` — Inquiry-led reasoning, citations, and critical review prompts.

### Sample Payload for Prompt Creation
*   **Path:** `POST /prompts/` (requires token authorization)
*   **Request Schema:**
    ```json
    {
      "topic": "Photosynthesis",
      "learning_style": "visual",
      "difficulty": "intermediate"
    }
    ```
*   **Persisted Schema (Response):**
    ```json
    {
      "id": 5,
      "user_id": 1,
      "topic": "Photosynthesis",
      "learning_style": "visual",
      "difficulty": "intermediate",
      "generated_prompt": "...",
      "created_at": "2026-06-11T19:30:00Z"
    }
    ```

---

## 📈 Current Project Progress

*   **[Completed]** Database models & Alembic setup.
*   **[Completed]** Authentication (JWT, bcrypt hashing, User Context endpoint).
*   **[Completed]** LearningStyleEngine for rule generation.
*   **[Completed]** Council Response schemas & AI adapters (Gemini, OpenAI, Claude, DeepSeek).
*   **[Completed]** Response Normalizer & Council Executor (concurrent processing).
*   **[Completed]** Consensus Builder (merging logic & provider prioritization).
*   **[Completed]** Prompt Scorer (Phase 17 scoring engine for consensus evaluation).

---

## 🗺️ Future Roadmap

*   **[Phase 18]** **Explanation Generator**: Construct human-readable rationales showing model contributions and learning style adaptations.
*   **[Phase 19]** **API Layer Completion**: Mount prompt request generation endpoints and pipeline execution hooks.
*   **[Phase 20]** **Frontend Dashboard Integration**: Build the playground UI allowing visual interaction with the Multi-Model AI Council.
*   **[Phase 21]** **Telemetry & Feedback Loops**: Implement user rating features to track prompt efficacy and update weights.
