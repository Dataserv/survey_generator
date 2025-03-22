# Survey Generator

## 📌 Overview
Survey Generator is a **Streamlit-based** application that enables users to create customized surveys with the help of **AI models** such as **OpenAI (ChatGPT), Claude (Anthropic), and Ollama (local)**. The app provides an interactive UI for configuring, generating, editing, and finalizing surveys before exporting them in various formats.

This tool is ideal for:
- Market research
- Customer feedback surveys
- Academic research
- Employee satisfaction surveys
- Any custom survey needs

---

## 🚀 Installation Guide
### 📋 Prerequisites
Ensure your system meets the following requirements:
- **Python 3.8+** installed
- `pip` package manager updated:
  ```sh
  pip install --upgrade pip
  ```

### 📦 Install Dependencies
Run the following command to install all necessary packages:
```sh
pip install -r requirements.txt
```
This will install:
- **Streamlit** (for the UI)
- **Pandas** (data processing)
- **Ollama** (local AI integration)
- **OpenAI & Anthropic** (for external AI services)
- **Openpyxl** (Excel export support)

---

## 🎯 How to Use
### 🔹 Launch the Application
Start the app with:
```sh
streamlit run app.py
```
This will open the application in your default web browser.

### 🔹 Configuration Steps
#### **1️⃣ Select Language & AI Service**
- Supported languages:
  - 🇫🇷 French
  - 🇬🇧 English
  - 🇪🇸 Spanish
  - 🇸🇦 Arabic
- Choose an AI Service:
  - **Ollama (Local)** (requires a running Ollama instance)
  - **OpenAI (ChatGPT)** (requires API key)
  - **Claude (Anthropic)** (requires API key)
- If using OpenAI or Claude, **enter your API key** in the sidebar.

#### **2️⃣ Survey Setup**
- Enter **Survey Details**:
  - Entity Name (e.g., Company, Organization, Institution)
  - Survey Title
  - Objectives
  - Target Audience (Individuals, Businesses, Employees, etc.)
- Define **Survey Structure**:
  - Number of Sections
  - Question Types (Single Choice, Multiple Choice, Open-ended, etc.)
  - Detail Level (Basic, Detailed, Very Detailed)
  - Estimated Duration
- Select **International Standards** (ISO 20252, AAPOR, etc.).

#### **3️⃣ Generate Questions**
- AI generates an **editable list of questions**.
- Modify, delete, or add new questions as needed.
- Save your updated question list.

#### **4️⃣ Finalize & Export**
- Generate a **structured and validated survey**.
- Review any inconsistencies (e.g., conditional logic errors).
- Choose an export format:
  - **JSON** (structured format for developers)
  - **CSV** (easy spreadsheet integration)
  - **Excel** (formatted for professional use)

---

## 📦 Export Formats
- **JSON** - Structured format for integration with other systems.
- **CSV** - Can be opened in Excel, Google Sheets, etc.
- **Excel (.xlsx)** - Best for professional reporting.

---

## 🔧 Advanced Features
### 🔹 **Ollama Integration (Local AI Model)**
- Uses `llama3:instruct` for generating questions.
- Requires a running **Ollama** instance:
  ```sh
  ollama serve
  ```
- Extracts and validates JSON responses from the model.

### 🔹 **Multi-Language Support**
- Surveys can be generated in **French, English, Spanish, and Arabic**.
- UI adapts based on selected language.

### 🔹 **International Standards Compliance**
- Supports **ISO 20252**, **AAPOR**, **ESS**, **OCDE**, and **ESOMAR** standards for professional survey design.

---

## 🛠 Troubleshooting Guide
### ❌ Common Issues & Fixes
| Issue | Possible Causes | Solution |
|--------|----------------|-----------|
| Application won’t start | Missing dependencies | Run `pip install -r requirements.txt` |
| No questions generated | API key missing or invalid | Check AI service settings & enter a valid API key |
| JSON format error | AI response not structured properly | Try regenerating the survey |
| Ollama not responding | Server not running | Run `ollama serve` in a separate terminal |

---

## 📜 License
This project is licensed under the **Apache 2.0 License**. Feel free to use and modify it.

---

## 🤝 Contributing
Contributions are welcome! To contribute:
1. **Fork the repository**.
2. **Create a feature branch** (`git checkout -b new-feature`).
3. **Commit changes** (`git commit -m "Added new feature"`).
4. **Push to GitHub** (`git push origin new-feature`).
5. **Submit a Pull Request**.

---

## 📞 Contact & Support
For issues, feature requests, or questions, please open an issue on **GitHub**.

🚀 **Happy Surveying!** 🎯
