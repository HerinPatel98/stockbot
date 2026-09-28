# 📦 Autonomous Conversational AI Inventory Management System (StockBot)

An enterprise-grade, conversational multi-tenant inventory management platform that bridges natural language human commands with an ACID-compliant relational SQL ledger via autonomous LLM tool calling. 

Engineered with a decoupled architecture (**Separation of Concerns**), the system provides deterministic stock accounting, dynamic fuzzy SKU matching, overselling prevention, session-persisted role-based access control (RBAC), multi-tenant isolation, and zero-knowledge per-query billing telemetry with prepaid dummy-dollar wallets.

---

## 🌟 Key Highlights & Engineering Features

- **Autonomous Deterministic Tool Calling:** Uses native function calling (`add_stock`, `reduce_stock`, `query_stock`, `delete_stock`) rather than raw text generation or vulnerable Text-to-SQL.
- **Fuzzy Entity Resolution & Suffix Normalization:** Built-in canonical matcher using `difflib` and plural/suffix stemming (`"usb-c docks"` $\rightarrow$ `"USB-C Dock"`). Completely eliminates accidental SKU duplication caused by typos or natural pluralization.
- **Dual-Mode Warehouse UI:**
  - **Guided Operations Bar:** Dropdown selection of active catalog items with hard inventory-clamped limits (`max_value = available_stock`) preventing human overselling and disabling out-of-stock sales.
  - **Conversational Chatbot:** Freeform conversational assistant with real-time status spinners, token telemetry tags, and intent-aware routing.
- **Auditable Lifecycle & SKU Decommissioning:** Every stock movement is logged to an immutable transaction ledger (`RESTOCK`, `SALE`). Destructive catalog deletions require explicit confirmation, calculate written-off asset valuations, and record permanent `DECOMMISSION` audit events.
- **Ultra-Low Latency Inference:** Powered by Groq LPUs (`openai/gpt-oss-20b`) delivering function calls and contextual summaries in under 400ms.
- **Zero-Knowledge Multi-Tenancy & Prepaid Wallets:**
  - **Data Plane (Isolated):** Confidential warehouse catalogs, unit margins, and inventory volumes remain strictly isolated to the tenant (`client_id`).
  - **Control Plane (Zero-Knowledge):** Platform administrators inspect only numerical metering logs (tokens, deducted cost, remaining balance, execution timestamp) with zero leakage of client prompts or product data.
  - **Self-Service Top-Ups:** Integrated sandbox recharge portal for clients to deposit dummy USD into their prepaid balance.
- **Multi-Port Enterprise Deployment:**
  - **Client Application (`app.py` on Port `8501`):** Warehouse dashboard, conversational assistant, theme customizer, and personal usage billing.
  - **Platform Admin Center (`admin_app.py` on Port `8502`):** Central fleet telemetry, macro revenue analytics, rate adjustment, and tenant provisioning.
- **Session-Persisted RBAC (`auth.py`):** Secure SHA-256 credential hashing backed by URL-query-parameter session continuity, preventing unexpected logouts on browser reloads or form reruns.
- **Dynamic Theming Engine:** High-contrast palettes (*Cyberpunk Neon*, *Terminal Amber*, *Deep Arctic Glacier*, *Royal Amethyst*) with WCAG-compliant card elevation and neon border accents.

---

## 🏗️ System Architecture & Workflow

```
                             +--------------------------------------------------+
                             |              Client Web Portal                   |
                             |         (Streamlit App - Port 8501)              |
                             |    Dashboard / Guided UI / Chat / Billing        |
                             +------------------------+-------------------------+
                                                      |
                                            Natural User Command
                                                      |
                                                      v
                             +--------------------------------------------------+
                             |           AI Orchestration Layer                 |
                             |         (Groq LPU Engine: GPT-OSS)               |
                             |   Tool Schema Validation & Anti-Hallucination    |
                             +------------------------+-------------------------+
                                                      |
                                       Emits Structured Tool Call
                                                      |
                                                      v
                             +--------------------------------------------------+
                             |             Business Logic Layer                 |
                             |         (services.py / Tool Registry)            |
                             |     * Fuzzy SKU Normalizer (difflib/stemming)    |
                             |     * Oversell Guardrails & Decommissioning      |
                             +------------------------+-------------------------+
                                                      |
                             Atomic ACID Parameterized Relational Transactions
                                                      |
                                                      v
                             +--------------------------------------------------+
                             |               Database Layer                     |
                             |           (SQLite: inventory.db)                 |
                             |   * clients             * products (scoped)      |
                             |   * users (RBAC)        * transactions (ledger)  |
                             |   * wallet_topups       * api_billing_telemetry  |
                             +------------------------+-------------------------+
                                                      ^
                                                      |
                                       Reads Only Numeric Telemetry
                                                      |
                             +------------------------+-------------------------+
                             |       Platform Administration Portal             |
                             |       (Streamlit Admin App - Port 8502)          |
                             |    Macro Revenue / Fleet Wallets / Provisioning  |
                             +--------------------------------------------------+
```

---

## 📁 Repository Structure

```text
stockbot/
├── .env                              # Groq API key configuration
├── requirements.txt                  # Python package dependencies
├── database.py                       # SQLite schema, multi-tenant models, & billing telemetry
├── auth.py                           # Session gatekeeper, SHA-256 auth, & URL query persistence
├── services.py                       # Business logic (fuzzy resolution, add/reduce/delete stock)
├── ai_service.py                     # Groq LLM tool orchestration & anti-hallucination caller
├── theme_manager.py                  # Dynamic CSS injection & contrast palettes
├── app.py                            # Client application entry point (Port 8501)
├── admin_app.py                      # Platform Admin Control Center (Port 8502)
└── pages/
    ├── 1_📊_Dashboard.py             # Tenant inventory KPIs, stock table, & SKU decommissioner
    ├── 2_💬_AI_Assistant.py          # Chatbot agent + Guided Stock Operations query builder
    ├── 3_⚙️_Settings.py              # Visual color palette selector
    └── 4_💳_Usage_and_Billing.py     # Prepaid dummy dollar wallet, top-up sandbox, & query logs
```

---

## ⚙️ Tech Stack & Prerequisites

- **Language:** Python 3.10+
- **Application Framework:** Streamlit (Multi-Page Architecture)
- **AI Inference Engine:** Groq Cloud SDK (`openai/gpt-oss-20b`)
- **Database Engine:** SQLite3 (Embedded ACID Relational Engine with Foreign Key Enforcement)
- **Data Analysis & Processing:** Pandas
- **String Distance & Matching:** Python Standard Library (`difflib`, `re`)
- **Environment Management:** `python-dotenv`

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

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=gsk_your_groq_api_key_here
```

### 5. Initialize the Multi-Tenant Database

```bash
python -c "import database; database.init_db(); print('Database schema initialized!')"
```

---

## 🖥️ Running the Applications (Concurrent Multi-Port)

To simulate a real enterprise production deployment, run the **Client Portal** and the **Platform Administration Center** simultaneously in two separate terminals:

### Terminal 1: Client Application (Port 8501)
```bash
streamlit run app.py
```
- **Access URL:** `http://localhost:8501`

### Terminal 2: Administration Portal (Port 8502)
```bash
streamlit run admin_app.py --server.port 8502
```
- **Access URL:** `http://localhost:8502`

*(Tip: Open the Admin portal in an Incognito window to maintain concurrent, isolated browser sessions.)*

---

## 🔑 Demo Access Credentials

| Organization / Role | Username | Password | Default Wallet | Access Port |
| :--- | :--- | :--- | :--- | :--- |
| **Acme Corp (Client Admin)** | `acme_admin` | `pass123` | `$25.00` Dummy USD | `http://localhost:8501` |
| **Stark Logistics (Client Admin)** | `stark_admin` | `pass123` | `$50.00` Dummy USD | `http://localhost:8501` |
| **Super Admin (Platform Owner)** | `admin` | `admin123` | N/A (Fleet Master) | `http://localhost:8502` |

---

## 💡 Operational Test Suite & Guardrail Verification

Test the application against these scenarios to demonstrate system robustness:

| Category | Action / Prompt | Expected System Behavior |
| :--- | :--- | :--- |
| **Fuzzy Resolution** | `Add 5 usb-c docks` | Resolves plural/case mismatch to existing `'USB-C Dock'`, updates stock without creating a duplicate SKU, and reports resolution trace. |
| **New SKU Protection** | `Add 10 Gaming Mice` | Halts insertion with a prompt guide because `'Gaming Mice'` does not exist in the catalog and no creation intent was declared. |
| **Explicit SKU Registration** | `Add new SKU 'Gaming Mouse' with 15 units at $35 each` | Detects `is_new_sku` authorization, registers the new catalog entry, and logs `RESTOCK`. |
| **Overselling Guardrail** | Guided Operations $\rightarrow$ `Record Sale (-)` | Dynamic selector clamps quantity to the exact available stock and prevents selecting $> available$. Out-of-stock items disable the execution button. |
| **Safe Decommissioning** | Dashboard $\rightarrow$ Decommission SKU | Displays valuation loss write-off warning (`Units × Unit Price`) and disables deletion until an explicit confirmation checkbox is toggled. |
| **Zero-Knowledge Billing** | Any Assistant Query | Deducts tenant query rate (e.g. `$0.05`), updates wallet balance, and writes numerical telemetry (`tokens`, `cost`, `timestamp`) to the audit ledger without logging prompt or catalog text. |
| **Prepaid Top-Up** | `4_💳_Usage_and_Billing` | Client selects sandbox recharge tier (e.g. `+$25.00`), clicks deposit, and updates their wallet balance. |

---

## 🔒 Security Architecture: Zero-Knowledge Multi-Tenancy

```
+------------------------------------+       +------------------------------------+
|         TENANT DATA PLANE          |       |        ADMIN CONTROL PLANE         |
|      (Client-Isolated Storage)     |       |      (Zero-Knowledge Telemetry)    |
+------------------------------------+       +------------------------------------+
| [products]                         |       | [api_billing_telemetry]            |
|  - id, client_id, name, stock,     |       |  - id, client_id, user_id          |
|    price                           |       |  - model_used                      |
|                                    |       |  - prompt_tokens, completion_tokens|
| [transactions]                     |       |  - cost_deducted, balance_after    |
|  - id, client_id, product_name,    |       |  - timestamp                       |
|    quantity_change, action_type    |       |                                    |
+------------------------------------+       +------------------------------------+
                |                                              |
                +----------------------+-----------------------+
                                       |
                   🛡️ ZERO BUSINESS LEAKAGE GUARANTEE:
        Platform admins can audit revenue, usage spikes, and model
        token throughput without accessing confidential inventory catalogs,
        product names, margins, or proprietary conversational prompts.
```

---
