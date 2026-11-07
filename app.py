import gradio as gr
from hindsight_client import Hindsight
from google import genai

# Setup Clients
HINDSIGHT_API_KEY = "hsk_a0f29fd7808a64542cf1dec59f70aab1_9b3f87fec8505c17"
HINDSIGHT_ENDPOINT = "https://api.hindsight.vectorize.io"
GEMINI_API_KEY = "AQ.Ab8RN6IXMyfNuX1LDejSxSjs5alio0Tk08hG5jkGikqHVC_t2A"

hindsight_client = Hindsight(base_url=HINDSIGHT_ENDPOINT, api_key=HINDSIGHT_API_KEY)
gemini_client = genai.Client(api_key=GEMINI_API_KEY.strip())
BANK_ID = "incident-logs-bank"

# Seed Data (Error logs & Runbooks)
INCIDENT_RUNBOOKS = [
    {"error": "FATAL: remaining connection slots are reserved for non-replication superuser connections", "fix": "ALTER SYSTEM SET max_connections = 200; SELECT pg_reload_conf();"},
    {"error": "OOM command not allowed when used memory > 'maxmemory'", "fix": "redis-cli CONFIG SET maxmemory-policy volatile-lru"},
    {"error": "504 Gateway Time-out nginx/1.18.0", "fix": "Increase proxy_read_timeout to 300s in /etc/nginx/nginx.conf and reload nginx."}
]

def seed_memory():
    for item in INCIDENT_RUNBOOKS:
        entry = f"Error: {item['error']} | Fix: {item['fix']}"
        try:
            hindsight_client.retain(bank_id=BANK_ID, documents=[entry])
        except Exception:
            try:
                hindsight_client.retain(bank_id=BANK_ID, content=entry)
            except Exception:
                pass

def diagnose_error(error_log, use_memory):
    if not error_log.strip():
        return "Please enter an error log."
    
    recalled_context = ""
    if use_memory:
        try:
            recall_res = hindsight_client.recall(bank_id=BANK_ID, query=error_log)
            memories = []
            if hasattr(recall_res, 'results'):
                for m in recall_res.results:
                    memories.append(getattr(m, 'text', str(m)))
            recalled_context = "\n".join(memories) if memories else "No relevant historical runbooks found."
        except Exception as e:
            recalled_context = f"Memory recall error: {str(e)}"
    else:
        recalled_context = "MEMORY DISABLED (Stateless Mode)"

    prompt = f"""
    You are an Autonomous SRE Incident Response AI Agent.
    Current Server Error: {error_log}
    Historical Memory Context: {recalled_context}

    Diagnose the root cause and provide exact step-by-step resolution commands.
    """
    
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

def retain_new_fix(error_log, custom_fix):
    if not error_log or not custom_fix:
        return "Error log and fix resolution are required."
    entry = f"Error: {error_log} | Fix: {custom_fix}"
    try:
        hindsight_client.retain(bank_id=BANK_ID, documents=[entry])
    except Exception:
        hindsight_client.retain(bank_id=BANK_ID, content=entry)
    return "Fix successfully approved and retained in Hindsight memory!"

# Gradio UI Interface
with gr.Blocks(title="Autonomous SRE Incident Response Agent") as demo:
    gr.Markdown("# 🛠️ Autonomous SRE Incident Response Agent")
    gr.Markdown("Powered by **FastAPI**, **Google Gemini**, and **Hindsight Persistent Vector Memory**.")
    
    with gr.Row():
        with gr.Column():
            error_input = gr.Textbox(lines=4, label="Paste Server Error Log", placeholder="e.g. FATAL: remaining connection slots are reserved...")
            memory_toggle = gr.Checkbox(label="Enable Hindsight Memory", value=True)
            diagnose_btn = gr.Button("Diagnose Incident", variant="primary")
        
        with gr.Column():
            diagnosis_output = gr.Textbox(lines=10, label="AI SRE Diagnosis & Resolution Plan")
    
    diagnose_btn.click(fn=diagnose_error, inputs=[error_input, memory_toggle], outputs=diagnosis_output)
    
    gr.Markdown("---")
    gr.Markdown("### 📥 Approve & Retain Resolved Runbook")
    with gr.Row():
        fix_input = gr.Textbox(lines=2, label="Verified Fix Command / Runbook", placeholder="e.g. ALTER SYSTEM SET max_connections = 200;")
        retain_btn = gr.Button("Approve & Retain Fix")
    retain_status = gr.Textbox(label="Status")
    
    retain_btn.click(fn=retain_new_fix, inputs=[error_input, fix_input], outputs=retain_status)

if __name__ == "__main__":
    seed_memory()
    demo.launch(share=True)
  
