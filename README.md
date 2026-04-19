# CivicLens — AI-Powered Political Manifesto Analyzer

CivicLens is an AI tool that brings transparency to political discourse. Upload any political manifesto as a PDF and a team of AI agents — an Economist, a Sociologist, and a Skeptic — will analyse it and return an unbiased summary, economic feasibility score, trust score, and historical context check.

**AI backbone:** Groq (LLaMA 3.3 70B) via LangChain + LangGraph  
**Search:** DuckDuckGo (for live fact-checking)  
**Backend:** Python · FastAPI  
**Frontend:** React · TypeScript · Vite · Tailwind CSS

---

## Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.9 or higher |
| Node.js + npm | 18 or higher |
| Groq API Key | Free at [console.groq.com](https://console.groq.com) |

---

## Setup

### 1 — Clone / unzip the repo

```
CivicLens-main/
├── backend/
│   ├── civic_brain.py   ← AI agent pipeline
│   ├── main.py          ← FastAPI server
│   ├── test.py          ← API key sanity check
│   ├── requirements.txt
│   └── .env             ← you create this (see step 3)
└── frontend/
    ├── src/
    ├── package.json
    └── vite.config.ts
```

### 2 — Backend setup

Open a terminal and navigate to the backend folder:

```bash
cd CivicLens-main/backend
```

Create and activate a virtual environment:

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3 — Configure your API key

In a file called `.env` inside the `backend/` folder, place your groq API key :

```env
GROQ_API_KEY=your_actual_groq_key_here
```

Get a free key at [console.groq.com](https://console.groq.com) → API Keys → Create Key.

> **Tip:** Run `python test.py` to verify your key works before starting the server.

### 4 — Start the backend

```bash
python main.py
```

You should see:

```
--- [SYSTEM] Groq Scoring Engine Initialized ---
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Keep this terminal open.** The backend must stay running while you use the app.

### 5 — Frontend setup

Open a **new** terminal and navigate to the frontend folder:

```bash
cd CivicLens-main/frontend
```

Install dependencies (first time only):

```bash
npm install
```

Start the dev server:

```bash
npm run dev
```

Open your browser at **http://localhost:5174**

---

## How to Use

### Manifesto Decoder
1. Click **Manifesto Decoder** in the sidebar.
2. Upload a PDF of a political manifesto or policy document.
3. Wait ~30–60 seconds for the three AI agents to complete their analysis.
4. Review the Feasibility Score, Trust Score, and the full Markdown report.

> The app only accepts genuine political manifestos. Resumes, novels, or unrelated PDFs will be rejected with an explanation.

### Alignment Compass
1. Click **Alignment Compass** in the sidebar.
2. Answer the quiz questions about your political views.
3. See which political quadrant and party your views align with.

---

## Troubleshooting

**`GROQ_API_KEY not found` error on startup**  
→ Make sure your `.env` file is inside the `backend/` folder (not the root), and contains `GROQ_API_KEY=...` with no quotes around the key.

**Port 5173 already in use / wrong app opens in browser**  
→ Another project is using port 5173. Kill it first:
```bash
# Windows — find the PID and kill it
netstat -ano | findstr :5173
taskkill /PID <PID_NUMBER> /F

# Mac / Linux
lsof -ti:5173 | xargs kill -9
```
Or pin CivicLens to a different port by adding this to `frontend/vite.config.ts`:
```ts
server: { port: 5174, strictPort: true }
```

**Analysis returns irrelevant or nonsensical content**  
→ This can happen if the PDF text extraction fails (scanned/image-only PDFs are not supported). Make sure your PDF has selectable text.

**`429 ResourceExhausted` errors**  
→ Groq free tier has daily limits. Wait a few minutes and retry, or create a new Groq API key.

**`ModuleNotFoundError` in Python**  
→ Your virtual environment is not activated. Run `.\venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux) before starting the server.

**Frontend can't reach backend**  
→ Make sure both servers are running. The frontend expects the backend at `http://localhost:8000`. If your backend port differs, update `API_BASE_URL` in `frontend/src/App.tsx`.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Groq · LLaMA 3.3 70B Versatile |
| Agent framework | LangChain · LangGraph |
| Web search | DuckDuckGo Search |
| Backend | Python · FastAPI · Uvicorn |
| PDF parsing | pypdf |
| Frontend | React 19 · TypeScript · Vite 7 |
| Styling | Tailwind CSS · Framer Motion · Lucide Icons |