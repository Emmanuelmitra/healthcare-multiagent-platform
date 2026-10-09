# Enterprise Multi-Agent AI Platform

A production-grade, extensible Multi-Agent AI system built with clean architectural abstractions following the **Google Agent Development Kit (Google ADK / GenAI)** pattern.

Designed for high-reliability enterprise applications (demonstrated on Healthcare) and engineered for seamless zero-code-change deployment on **Google Cloud Platform (GCP)**, **AWS**, and **Microsoft Azure**.

---

## 🌟 Key Capabilities & Architectural Pillars

1. **Multi-Agent Orchestration**:
   - **Supervisor Agent**: Decomposes user goals, routes tasks, and supervises sub-agents.
   - **Triage Specialist Agent**: Gathers clinical context, symptoms, and severity classification.
   - **Diagnostic & Protocol Agent**: Searches institutional guidelines and verifies drug interactions.
   - **Compliance & Safety Agent**: Audits clinical recommendations, attaches mandatory legal disclaimers, and enforces boundaries.

2. **Enterprise Guardrails**:
   - **HIPAA PHI / PII Scrubber**: Automatically detects and redacts SSNs, MRNs, emails, and phone numbers.
   - **Prompt Injection Defense**: Defends against adversarial jailbreak attempts and system prompt exfiltration.
   - **Clinical Acuity Verification**: Detects emergency red-flag conditions and alerts clinicians.

3. **Multi-Tiered Memory**:
   - **Working / Session Memory**: Ephemeral multi-turn context tracking with Redis / in-memory support.
   - **Semantic / Episodic Memory**: Vector search over institutional guidelines and past encounters.

4. **Human-in-the-Loop (HITL)**:
   - High-risk clinical recommendations trigger approval gates before execution.

5. **Observability & Telemetry**:
   - Structured JSON audit logging, token consumption tracking, and estimated USD cost calculations.

6. **Extensible Domain Model**:
   - Add new agents in under 10 minutes without touching core code using the `@AgentRegistry.register` decorator (see `examples/new_agent_template.py`).

---

## 🚀 Quickstart in VS Code

### 1. Prerequisites
- Python 3.10+
- (Optional) Docker & Docker Compose

### 2. Run the Interactive CLI Demo
```bash
python examples/quickstart.py
```

### 3. Run the Automated Test Suite
```bash
python -m unittest discover -s tests -p "test_*.py"
```

### 4. Run the Production FastAPI Server
```bash
uvicorn src.main:app --reload --port 8000
```
- Open Swagger Documentation at: `http://localhost:8000/docs`
- Health check probe: `http://localhost:8000/health`

---

## ☁️ Multi-Cloud Deployment Guide

### Option A: Local / Virtual Machine Docker Compose
```bash
docker-compose up --build -d
```

### Option B: Google Cloud Platform (GCP)
- **Cloud Run (Serverless)**:
  ```bash
  gcloud run deploy healthcare-agent-platform \
    --source . \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars GEMINI_API_KEY=$GEMINI_API_KEY
  ```
- **GKE (Google Kubernetes Engine)**:
  ```bash
  kubectl apply -f deploy/k8s/
  ```

### Option C: AWS (Amazon Web Services)
- Deploy container image to **Amazon ECR** and run on **AWS ECS Fargate** or **Amazon EKS** using the provided Kubernetes manifests in `deploy/k8s/`.

### Option D: Microsoft Azure
- Deploy container image to **Azure Container Registry (ACR)** and host on **Azure Container Apps** or **AKS (Azure Kubernetes Service)**.
