# 📦 Autonomous Conversational AI Inventory Management System (StockBot)

An enterprise-grade, conversational inventory management platform that bridges natural language human commands with an ACID-compliant relational SQL ledger via autonomous LLM tool calling. 

Engineered with a decoupled architecture (**Separation of Concerns**), the system provides deterministic stock accounting, multi-page data analytics, customizable theme palettes, multi-tenant client isolation, and zero-knowledge per-query billing telemetry.

---

## 🌟 Key Highlights

- **Deterministic Tool Calling:** Uses native function calling (`add_stock`, `reduce_stock`, `query_stock`) rather than raw text or vulnerable SQL generation. Prevents hallucinations and SQL injection risks.
- **Ultra-Low Latency Inference:** Powered by Groq LPUs (`openai/gpt-oss-20b`) delivering responses in under 400ms with high uptime.
- **Auditable Ledger Engine:** Every stock movement records an immutable entry in an activity ledger with timestamps, delta shifts, and classification categories (`RESTOCK` vs. `SALE`).
- **Interactive Multi-Page Frontend:** Built on Streamlit's multi-page architecture with separate views for high-level warehouse metrics, real-time conversational agents, dynamic theming, and an administrative billing portal.
- **Dynamic Theming Engine:** Instant theme switching across four high-contrast palettes (*Cyberpunk Neon*, *Terminal Amber*, *Nordic Glacier*, *Royal Amethyst*) via dynamic session-state CSS injection.
- **Zero-Knowledge Multi-Tenancy:** Complete separation between the **Data Plane** (confidential client inventory stored locally) and the **Control Plane** (pure numerical billing telemetry logging tokens and costs with zero business data leakage).

---

## 🏗️ System Architecture & Workflow

```
                             +---------------------------------+
                             |    Streamlit Web Interface      |
                             |  (Dashboard / Chatbot / Admin)  |
                             +---------------+-----------------+
                                             |
                                   User Natural Prompt
                                             |
                                             v
                             +---------------------------------+
                             |        AI Service Layer         |
                             |    (Groq LPU Engine: GPT-OSS)   |
                             +---------------+-----------------+
                                             |
                       Evaluates & Emits Structured Tool Call
                                             |
                                             v
                             +---------------------------------+
                             |       Business Logic Layer      |
                             |  (services.py / Tool Registry)  |
                             +---------------+-----------------+
                                             |
                     Executes Parameterized & Isolated SQL Transactions
                                             |
                                             v
                             +---------------------------------+
                             |         Database Layer          |
                             |     (SQLite: inventory.db)      |
                             |  * products      * transactions |
                             |  * clients       * telemetry    |
                             +---------------------------------+
```

---

## 📁 Repository Structure

```text
stockbot/
├── .env                              # Environment variables (API keys, ports)
├── requirements.txt                  # Python dependencies
├── database.py                       # SQLite schema, data models & telemetry helpers
├── services.py                       # Business logic tools (add_stock, reduce_stock, query_stock)
├── ai_service.py                     # Groq LLM tool calling orchestration & meter tracking
├── theme_manager.py                  # Dynamic CSS injection & theme definitions
├── test_groq.py                      # Diagnostic script for API & model connectivity
├── app.py                            # Main application entry point & portal router
└── pages/
    ├── 1_📊_Dashboard.py             # Live inventory tables, KPIs & audit logs
    ├── 2_💬_AI_Assistant.py          # Conversational chatbot interface with loading status
    ├── 3_⚙️_Settings.py              # Visual theme selector & configuration
    └── 4_💳_Admin_Billing.py         # Multi-client telemetry, rate manager & usage audit
```

---

## ⚙️ Tech Stack & Prerequisites

- **Language:** Python 3.10 or higher
- **Frontend Framework:** Streamlit (Multi-Page Architecture)
- **AI Orchestration & LLM:** Groq Cloud SDK (`openai/gpt-oss-20b`)
- **Database & Persistence:** SQLite3 (Embedded ACID Relational Engine)
- **Data Manipulation:** Pandas
- **Configuration & Environment:** `python-dotenv`

---

## 🚀 Getting Started

### 1. Clone the Repository & Navigate

```bash
git clone https://github.com/<your-username>/stockbot.git
cd stockbot
```

### 2. Configure Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Ensure your `requirements.txt` contains:

```text
streamlit>=1.35.0
groq>=0.9.0
python-dotenv>=1.0.1
pandas>=2.2.0
requests>=2.31.0
```

Install packages:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
```

---

## 🧪 Testing & Diagnostics

### Run API & Model Connectivity Test
Verify that your Groq API key is valid and inspect available models on your account:

```bash
python test_groq.py
```

### Initialize Database Schema
Pre-populate the SQLite tables (`products`, `transactions`, `clients`, `api_usage_logs`) with baseline demo data:

```bash
python -c "from database import init_db; init_db()"
```

### Launch the Application
Run the Streamlit application:

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

## 💡 Conversational Demo Test Suite

Test the application workflow by passing these structured prompts on the **💬 AI Assistant** page:

| Test Case | Sample Prompt | Expected Action |
| :--- | :--- | :--- |
| **Catalog Query** | `Show me the complete inventory list.` | Calls `query_stock`, returns formatted list of current items and prices. |
| **Restock / Insert** | `We received 50 Mechanical Keyboards at $45 each.` | Calls `add_stock`, updates stock or registers new SKU, logs `RESTOCK` in ledger. |
| **Record Sale** | `Sold 5 Mechanical Keyboards to an office.` | Calls `reduce_stock`, decrements stock by 5, logs `SALE` in ledger. |
| **Safety Guardrail** | `Sell 500 Mechanical Keyboards right now.` | Rejects operation due to insufficient inventory without modifying the database. |
| **Catalog Query** | `Do we have any Gaming Monitors?` | Handles missing SKU checks and informs user politely. |

---

## 🔒 Commercial Architecture: Multi-Tenancy & Zero-Knowledge Billing

For enterprise deployment, this project demonstrates **Zero-Knowledge Multi-Tenancy**:

1. **Client Isolation:**
   Every inventory transaction is strictly scoped with a tenant constraint (`WHERE client_id = ?`). Clients only interact with their own catalog.
2. **Zero-Knowledge Telemetry:**
   The admin portal records **only numerical usage metadata**:
   - `client_id`
   - `model_used`
   - `prompt_tokens` & `completion_tokens`
   - `cost_charged` (e.g., $0.05 per query)
   - `timestamp`
3. **Data Sovereignty:**
   Shopkeepers' actual products, pricing margins, inventory volumes, and prompt text remain isolated in their data layer and are **never** logged to the administrative billing telemetry table.

---

## 🎓 Viva Voce Defense Guide (Key Questions & Answers)

- **Q: Which database did you use to store data, and why?**  
  *A:* We use **SQLite**, an embedded, serverless, relational SQL database management system. All data is persisted in an ACID-compliant file (`inventory.db`) with normalized tables (`products`, `transactions`, `clients`, `api_usage_logs`). Relational integrity guarantees that stock level updates and ledger entries commit atomically.

- **Q: Why use Function Calling instead of Text-to-SQL?**  
  *A:* Direct SQL generation poses critical security risks (SQL injection) and calculation errors (hallucinated schemas). Using **Function Calling** binds the LLM to strict, pre-validated Python functions (`add_stock`, `reduce_stock`, `query_stock`) with parameterized queries, guaranteeing deterministic database integrity.

- **Q: How does the system handle multi-client deployments without seeing private shopkeeper data?**  
  *A:* We enforce a strict separation between the **Data Plane** and the **Telemetry Plane**. The shopkeeper's inventory and transactions reside in their isolated local database. The administrative backend only receives non-sensitive numeric telemetry (`client_id`, `tokens_consumed`, `cost_charged`), ensuring zero business data leakage.

- **Q: How do you handle inference latency and API errors?**  
  *A:* We route requests through Groq LPUs (`openai/gpt-oss-20b`) for sub-second function calling, and protect frontend states with Streamlit session management and error wrappers that prevent unhandled crashes during network interruptions.
