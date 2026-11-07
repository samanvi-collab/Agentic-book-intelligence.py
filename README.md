# Autonomous SRE Incident Response Agent 🛠️🤖

An intelligent Site Reliability Engineering (SRE) assistant designed to ingest real-time server error logs, fetch historical post-mortem runbooks via persistent memory, and output actionable step-by-step resolution commands using Google Gemini 2.5 Flash.

---

## 🌟 Key Features

* **Persistent Vector Memory:** Integrated with **Hindsight Vector Memory** to retain past post-mortem runbooks and system fixes.
* **Context-Aware AI Diagnosis:** Uses **Google Gemini 2.5 Flash** to analyze incoming server errors against recalled historical incidents.
* **Interactive Control Dashboard:** Built with a Python-native **Gradio UI** containing a live memory ON/OFF toggle switch to benchmark stateless vs. memory-augmented AI responses.
* **Runbook Retention Workflow:** Features an "Approve & Retain Fix" module that lets SREs write verified fixes back into Hindsight vector storage directly from the interface.

---

## 🏗️ Architecture

1. **Ingestion Layer:** Raw server log string passed via Gradio frontend UI.
2. **Memory Recall:** Hindsight API queries past vector embeddings stored under the `incident-logs-bank` memory namespace.
3. **LLM Diagnostics:** Google Gemini generates root cause diagnosis and exact CLI remediation steps leveraging recalled runbooks.
4. **Memory Retention:** Newly verified fixes are stored permanently to continuously improve system intelligence.

---

## ⚡ Setup & Execution

### 1. Install Dependencies
```bash
pip install hindsight-client google-genai gradio
