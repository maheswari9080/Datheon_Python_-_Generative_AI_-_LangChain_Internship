# AI Research Workbench: GitHub & Cloud Hosting Guide

This guide details how all four applications and the central portal are hosted directly on GitHub and public cloud environments.

---

## 1. GitHub Pages Hosting (Central Research Portal)

The central research workbench portal ([`index.html`](../index.html)) is configured for automated deployment via GitHub Pages using the included GitHub Actions workflow.

### Automated Workflow
The repository includes `.github/workflows/pages.yml`. Whenever changes are pushed to `main`, GitHub Actions automatically packages and deploys the root directory to GitHub Pages.

### Live URL Format:
```text
https://maheswari9080.github.io/Python-Generative-AI-LangChain-Internship/
```

### Enabling GitHub Pages in Repository Settings:
1. Navigate to the GitHub repository: `https://github.com/maheswari9080/Python-Generative-AI-LangChain-Internship`
2. Go to **Settings** -> **Pages** (under the "Code and automation" section).
3. Under **Build and deployment** -> **Source**, select **GitHub Actions**.
4. The workflow will trigger and publish the live portal.

---

## 2. Streamlit Community Cloud Hosting (Interactive Multi-Task Suite)

Streamlit Community Cloud provides 100% free, 24/7 cloud hosting for Streamlit applications directly linked to GitHub repositories.

The repository includes a root [`streamlit_app.py`](../streamlit_app.py) and [`requirements.txt`](../requirements.txt) specifically engineered for one-click Streamlit Cloud deployment.

### How to Deploy in 2 Minutes:
1. Visit **[share.streamlit.io](https://share.streamlit.io/)** and sign in with GitHub account `maheswari9080`.
2. Click **New app**.
3. Fill in the deployment form:
   - **Repository**: `maheswari9080/Python-Generative-AI-LangChain-Internship`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
4. *(Optional)* Click **Advanced settings** to add your secret keys under Secrets:
   ```toml
   GEMINI_API_KEY = "your-api-key-here"
   OPENAI_API_KEY = "your-api-key-here"
   ```
5. Click **Deploy!**

### What Evaluators Can Access on the Live URL:
- 🏠 **Suite Overview**: Executive architecture summary and test audit ledger.
- 📑 **Task 1: Structured Extractor**: Full interactive parsing of invoices and resumes with schema validation and JSON export.
- 📚 **Task 2: Grounded Document RAG**: Pre-indexed technical whitepapers with semantic retrieval and inline citation cards.
- 🤖 **Task 3: Autonomous AI Agent**: Interactive multi-step ReAct agent runner with live action-observation audit tables.
- 💬 **Task 4: Conversation Studio**: Multi-turn chat with streaming output, session isolation, and tri-mode dispatch.

---

## 3. GitHub Actions CI/CD Automated Test Pipeline

The repository includes `.github/workflows/ci.yml` which runs automatically on every push and pull request.

- Tests across Python `3.11` and `3.12`.
- Installs all dependencies via `requirements.txt`.
- Runs all 39 unit and integration tests via `pytest`.
- Emits green verification status check on GitHub commits.

---

## 4. Docker & Container Cloud Hosting

The repository includes a production `Dockerfile` and `docker-compose.yml`.

### Local Container Run:
```bash
docker compose up --build
```
Access at `http://localhost:8501`.

### Deploying to Hugging Face Spaces:
1. Create a new Space on [Hugging Face](https://huggingface.co/new-space).
2. Select **Streamlit** (or **Docker**) as the SDK.
3. Link your GitHub repository or push the repository code to Hugging Face.
