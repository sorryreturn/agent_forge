# Agent Forge 🛠️

Agent Forge is a 100% private, fast, and highly customizable AI Agent Factory built completely in Python. It utilizes meta-programming to generate powerful, multi-purpose automated pipelines. 

While it is lightweight and free, it provides a completely secure ecosystem designed to be open-source so the community can upgrade and optimize it into something even greater.

## 🚀 Key Features & Selling Points
* **100% Fully Private:** Operates entirely locally on your machine with direct Mistral Cloud API interactions. There are absolutely no 3rd-party servers or middlemen logging your data or code.
* **Bring Your Own Key (BYOK):** Safe and highly secure. The Streamlit UI takes your Mistral API key via a masked password text field. Your key is never hardcoded into the scripts—even if someone is looking at your screen, it will only show up as secure dots.
* **Infinite Customization:** Because the factory relies on structural prompts, you can radically alter the entire behavior, coding style, logic, and output parameters of the factory simply by changing the underlying AI prompts and models.
* **Streamlit UI:** Features a clean, accessible graphical interface designed so that even non-programmers can deploy, configure, and use the factory effortlessly.

## 🖥️ Operating System & Environment
* **Default Setup:** Out of the box, the main version of Agent Forge is optimized to build, execute, and test code within a **Windows 11 environment**.
* **Cross-Platform Adaptability:** You are **not** locked into Windows. If you want the factory to generate code for Linux, macOS, or older Windows versions, you can change the target environment instantly just by customizing the system prompts and instructions.

## 📦 Installation & Setup
1. Clone this repository or download the source code files.
2. Install the core factory requirements (built-in libraries like `os`, `sys`, `json`, `re`, and `subprocess` are already included in Python):
   ```bash
   pip install -r requirements.txt
