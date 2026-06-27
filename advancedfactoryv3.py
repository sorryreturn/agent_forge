import os
import json
import re
import subprocess
import sys
import pandas as pd
import streamlit as st
from mistralai.client import Mistral
from typing import Dict, Any

# --- Streamlit Page Configurations ---
st.set_page_config(
    page_title="Enterprise Agent Factory Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Global Reviewer Class ---
class GlobalReviewer:
    def __init__(self, api_key: str):
        self.client = Mistral(api_key=api_key)

    def review_code(self, code: str) -> str:
        messages = [
            {"role": "system", "content": (
                "You are a ruthless Senior Auditor. Inspect code for bugs, security, and logic. "
                "If flawless, output exactly 'PASSED'. If not, output 'FAILED' followed by directives."
            )},
            {"role": "user", "content": code}
        ]
        response = self.client.chat.complete(model="mistral-large-latest", messages=messages)
        return response.choices[0].message.content

# --- Styling & Setup ---
st.markdown("""<style>.main { background-color: #0f172a; color: #f8fafc; }</style>""", unsafe_allow_html=True)
MISTRAL_MODEL = "codestral-latest"
SANDBOX_TEST_FILE = "factory_sandbox_run"
MEMORY_DIR = "factory_agent_memory"
os.makedirs(MEMORY_DIR, exist_ok=True)

# --- (Memory/Sandbox functions remain unchanged, starting from read_all_memory()...) ---
def read_all_memory():
    lessons = []
    if not os.path.exists(MEMORY_DIR): return ""
    for filename in os.listdir(MEMORY_DIR):
        if filename.endswith(".json"):
            try:
                with open(os.path.join(MEMORY_DIR, filename), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    lessons.append(f"Known Bug: {data.get('error')}\nFixing Action: {data.get('solution')}")
            except Exception: pass
    return "\n--- HISTORIC LEARNED LESSONS ---\n" + "\n\n".join(lessons) if lessons else ""

def save_new_memory(error_msg, fix_instruction):
    safe_name = re.sub(r'[^a-zA-Z0-9]', '_', error_msg[:30]).lower()
    with open(os.path.join(MEMORY_DIR, f"lesson_{safe_name}.json"), "w", encoding="utf-8") as f:
        json.dump({"error": error_msg, "solution": fix_instruction}, f, indent=4)

def run_safe_sandbox_test(code_content, file_extension):
    # [Sandbox logic same as your original...]
    return {"status": "SUCCESS", "error": None, "stdout": "Sandbox result placeholder"}

# --- Sidebar UI ---
st.sidebar.title("🛠️ Factory Settings")
api_key_input = st.sidebar.text_input("Enter Mistral API Key", type="password", value=os.environ.get("MISTRAL_API_KEY", ""))
sandbox_toggle = st.sidebar.checkbox("Enable Live Sandbox Runtime Execution", value=True)
use_final_reviewer = st.sidebar.checkbox("✅ Enable Final Global Audit", value=True)
# User-provided high-level objective for the factory
user_goal = st.sidebar.text_input("Enter your development objective (user_goal)", value="")

# ... (Insert your original manager_instructions, worker_instructions, etc., here) ...
manager_instructions = """
    "You are the Lead System Architect. Take a complex development objective and break it down into an engineering plan.\n"
    "Output strictly a JSON object containing exactly two keys:\n"
    "1. 'blueprint': A global map outlining module packages, function signatures, variable naming scopes, and data type rules.\n"
    "2. 'tasks': A sequential array of step-by-step specific tasks to be assigned to cooperative workers.\n"
    "Ensure all code constraints are optimized for Windows 11 environment pipelines.\n"
    "Output format: {\"blueprint\": \"...\", \"tasks\": [\"task 1\", \"task 2\"]}"
    "whenever i ask you to make a ai agent for me, always use mistral cloud api as the ai agent in the code"""
worker_instructions=""""You are a Collaborative Software Engineer working in a sequential relay pipeline.\n"
    "You will receive the project goal, the master system blueprint, and the codebase built by your peers so far.\n"
    "Your job is to append or refactor code to solve your assigned task without breaking existing logical features.\n"
    "CRITICAL RULES:\n"
    "1. Always match variable and function names to the blueprint and code already provided.\n"
    "2. Deduplicate all import statements, positioning them cleanly at the top.\n"
    "3. Return the entire codebase including your new additions inside a single markdown code block."
"""
worker_reviewer_instructions = """
    "You are a notoriously strict, adversarial Senior Code Auditor reviewing code written by an intern.\n"
    "Your job is to catch lazily written loops, security flaws, or bad logic before it hits assembly pipelines.\n"
    "CRITICAL CRASH TRIGGERS:\n"
    "1. Check for 'input()' statements. If you see 'input()', write FAILED instantly. Scripts must never wait for command-line inputs.\n"
    "2. Check for '__file__'. If used without safety fallbacks, write FAILED because sandbox environments will crash on it.\n"
    "3. Look for unsafe slice modifications like 'df[cols] = ...' that cause SettingWithCopyWarnings.\n\n"
    "OUTPUT FORMAT:\n"
    "- If the structure is logically bulletproof, reply exactly: PASSED\n"
    "- If structurally broken or triggering a rule, reply exactly: FAILED followed by precise refactoring directives."
    "make sure the code uses mistral cloud api as the ai agent in the code"
    "make sure the work follows the manager blueprint"
    "Use the correct URL: https://api.mistral.ai/v1/chat/completions (Never anything else)."

    "Use the messages array: Always wrap code in a user message and instructions in a system message."

    "Model parameter: Ensure it uses model="mistral-large-latest" or the model you prefer."

    "Security First: The Factory should never hardcode keys. It should generate the file with a placeholder like api_key = os.getenv("MISTRAL_API_KEY") so you aren't pasting keys into files that might get saved or shared." 
"""
global_reviewer_instructions = """"
    "You are a notoriously strict, adversarial Senior Code Auditor reviewing code written by an intern.\n"
    "Your job is to catch lazily written loops, security flaws, or bad logic before it hits assembly pipelines.\n"
    "CRITICAL CRASH TRIGGERS:\n"
    "1. Check for 'input()' statements. If you see 'input()', write FAILED instantly. Scripts must never wait for command-line inputs.\n"
    "2. Check for '__file__'. If used without safety fallbacks, write FAILED because sandbox environments will crash on it.\n"
    "3. Look for unsafe slice modifications like 'df[cols] = ...' that cause SettingWithCopyWarnings.\n\n"
    "OUTPUT FORMAT:\n"
    "- If the structure is logically bulletproof, reply exactly: PASSED\n"
    "- If structurally broken or triggering a rule, reply exactly: FAILED followed by precise refactoring directives."
    "make sure the code uses mistral cloud api as the ai agent in the code"
    "make sure the work follows the manager blueprint"
    "Use the correct URL: https://api.mistral.ai/v1/chat/completions (Never anything else)."

    "Use the messages array: Always wrap code in a user message and instructions in a system message."

    "Model parameter: Ensure it uses model="mistral-large-latest" or the model you prefer."

    "Security First: The Factory should never hardcode keys. It should generate the file with a placeholder like api_key = os.getenv("MISTRAL_API_KEY") so you aren't pasting keys into files that might get saved or shared." 
"""

# --- Main Production Workflow ---
if st.button("🚀 Run Assembly Line"):
    mistral_client = Mistral(api_key=api_key_input)
    def call_agent(system_prompt, user_prompt, temperature=0.7):
        return mistral_client.chat.complete(model=MISTRAL_MODEL, temperature=temperature, 
               messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]).choices[0].message.content

    prog_bar = st.progress(0)
    status_text = st.empty()
    log_expander = st.expander("📘 Assembly Log", expanded=True)
    
    # ... (Stage 1 and 2 logic remains identical) ...
    with log_expander:
            # STAGE 1: PLAN AND ARCHITECTURE DESIGN
            status_text.text("🧠 [Stage 1/4] Constructing architectural blueprint layout...")
            prog_bar.progress(15)
            
            historic_lessons = read_all_memory()
            manager_raw = call_agent(manager_instructions, f"Objective: {user_goal}\n{historic_lessons}", temperature=0.5)
            
            try:
                json_match = re.search(r"(\{.*\})", manager_raw, re.DOTALL)
                arch_data = json.loads(json_match.group(1))
                global_blueprint = arch_data.get("blueprint", "")
                subtasks = arch_data.get("tasks", [])
            except Exception:
                global_blueprint = "Maintain clean standard modular execution paths and consistent parameters."
                subtasks = [line.strip() for line in manager_raw.split('\n') if line.strip()][:4]

            st.markdown("### 📋 System Design Blueprint Established")
            st.info(global_blueprint)
            st.json(subtasks)
            st.markdown("---")

            # STAGE 2: SEQUENTIAL COOPERATIVE WORKER REACTION LOOP
            status_text.text("🤝 [Stage 2/4] Triggering collaborative peer relay execution...")
            prog_bar.progress(40)
            
            accumulated_codebase = ""
            
            for idx, subtask in enumerate(subtasks, 1):
                status_text.text(f"⚡ Peer Worker {idx}/{len(subtasks)} executing integration: {subtask}")
                
                worker_prompt = (
                    f"Master Objective: {user_goal}\n"
                    f"Global Blueprint: {global_blueprint}\n\n"
                    f"--- ACCUMULATED CODEBASE FROM PREVIOUS PEERS ---\n"
                    f"{accumulated_codebase if accumulated_codebase else '# Core initialization complete.'}\n\n"
                    f"YOUR TASK STEP: {subtask}\n\n"
                    f"Integrate code modifications and return the whole code sequence inside standard code blocks."
                )
                
                # Creative Generation Mode
                worker_raw = call_agent(worker_instructions, worker_prompt, temperature=0.7)
                code_match = re.search(r"```[a-zA-Z0-9+#-]*\n(.*?)```", worker_raw, re.DOTALL)
                current_worker_code = code_match.group(1).strip() if code_match else worker_raw.strip()
                
                # Rigid Auditing Mode (Temperature = 0.0)
                audit_prompt = f"Target task assignment: {subtask}\nIntegrated output proposal:\n{current_worker_code}"
                review_verdict = call_agent(worker_reviewer_instructions, audit_prompt, temperature=0.0)
                
                if review_verdict.strip().upper().startswith("FAILED"):
                    feedback = review_verdict.replace("FAILED", "").strip()
                    repair_prompt = f"Peer audit flagged an issue: {feedback}\nRegenerate the complete integrated codebase with fixes applied."
                    worker_raw = call_agent(worker_instructions, repair_prompt, temperature=0.4)
                    code_match = re.search(r"```[a-zA-Z0-9+#-]*\n(.*?)```", worker_raw, re.DOTALL)
                    current_worker_code = code_match.group(1).strip() if code_match else worker_raw.strip()
                
                accumulated_codebase = current_worker_code
                st.write(f"✅ *Worker {idx} Complete:* {subtask}")
            
            st.markdown("---")
    # After Stage 2, enter the logic below:

    # Ensure accumulated_codebase exists (fallback to empty string if earlier stages didn't set it)
    if 'accumulated_codebase' not in locals():
        accumulated_codebase = ""
    clean_code = accumulated_codebase
    if use_final_reviewer:
        status_text.text("🧐 Running Global Final Audit...")
        reviewer = GlobalReviewer(api_key=api_key_input)
        audit_verdict = reviewer.review_code(clean_code)
        
        if audit_verdict.strip().upper().startswith("PASSED"):
            st.success("🎉 Global Audit Passed!")
        else:
            st.warning("⚠️ Global Audit Failed. Refactoring...")
            refactor_prompt = f"Fix these issues: {audit_verdict}. Deliver ONLY the corrected code."
            refactor_raw = call_agent(worker_instructions, refactor_prompt, temperature=0.3)
            code_match = re.search(r"```[a-zA-Z0-9+#-]*\n(.*?)```", refactor_raw, re.DOTALL)
            clean_code = code_match.group(1).strip() if code_match else refactor_raw.strip()

    st.markdown("## 🏁 Output Workspace")
    st.code(clean_code, language="python")

    output_file_name = "factory_production_output.py"
    with open(output_file_name, "w", encoding="utf-8") as f:
        f.write(clean_code)

    st.download_button(
        label="📥 Download Production Asset File",
        data=clean_code,
        file_name=output_file_name,
        mime="text/plain"
    )