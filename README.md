# TelecomPlus Customer Support Chatbot

A sophisticated multi-agent customer support chatbot for TelecomPlus, built with advanced RAG (Retrieval-Augmented Generation) and data querying capabilities. The system achieves 100% evaluation accuracy and handles both general FAQ questions and personal customer data queries.

## 🚀 Features

### Core Capabilities
- **Intelligent Question Classification**: Automatically routes questions between FAQ and personal data agents
- **Enhanced RAG System**: Context-aware retrieval with question-type specific searches (pricing, roaming, battery specs, etc.)
- **Personal Data Queries**: Secure access to customer-specific information (plans, usage, billing)
- **Real-time Responses**: Powered by Google Gemini 2.5-flash LLM
- **Web Interface**: Clean Streamlit-based chat interface with conversation history

### Technical Highlights
- **100% Evaluation Accuracy**: Achieved perfect scores on 25 evaluation questions
- **Multi-Agent Architecture**: Orchestrator pattern with specialized agents for different query types
- **Local Vector Store**: ChromaDB with sentence-transformers embeddings for efficient FAQ retrieval
- **Comprehensive Data Integration**: Processes PDF documents and Excel databases
- **Monitoring & Observability**: Langfuse integration for LLM call tracking and performance monitoring

## 🏗️ Architecture

### System Components

#### Orchestrator Agent (`src/agents/`)
- **Question Classification**: Routes questions to appropriate agents based on content analysis
- **Fallback Logic**: Handles misclassified questions with intelligent recovery
- **Response Coordination**: Manages multi-step query processing

#### FAQ Agent
- **Vector Retrieval**: Searches TelecomPlus FAQ documents using semantic similarity
- **Context Enhancement**: Adapts search strategy based on question type (pricing tables, roaming policies, etc.)
- **Answer Generation**: Combines retrieved context with LLM reasoning

#### Data Agent
- **Excel Database Queries**: Accesses customer data across multiple tables:
  - Clients (customer information)
  - Forfaits (service plans)
  - Abonnements (subscriptions)
  - Consommation (usage data)
  - Factures (billing)
  - Tickets (support cases)
- **Secure Filtering**: Client-specific data access with proper authentication

#### Vector Store (`src/vectorstore/`)
- **PDF Processing**: Loads and chunks TelecomPlus documentation
- **Embedding Generation**: Uses sentence-transformers for semantic indexing
- **Efficient Retrieval**: ChromaDB for fast similarity searches

### Data Flow
```
User Query → Orchestrator → Classification → [FAQ Agent | Data Agent]
                                      ↓
Retrieval (Vector/PDF) ←→ LLM Generation → Response
                                      ↓
Data Query (Excel) ←→ Result Filtering → Response
```

## 📋 Prerequisites

- Python 3.8+
- Google Gemini API key
- Langfuse API key (optional, for monitoring)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd dauphine-project-iasd-2025
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   Create a `.env` file in the root directory:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key
   LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
   LANGFUSE_SECRET_KEY=your_langfuse_secret_key
   LANGFUSE_HOST=your_langfuse_host
   ```

4. **Prepare data files**:
   Place your data files in the following structure:
   ```
   data/
   ├── pdfs/          # TelecomPlus FAQ documents
   └── xlsx/          # Customer data Excel files
       ├── clients.xlsx
       ├── forfaits.xlsx
       ├── abonnements.xlsx
       ├── consommation.xlsx
       ├── factures.xlsx
       └── tickets.xlsx
   ```

## ⚡ Quick Start

Follow these steps to get the TelecomPlus chatbot running quickly:

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Set Up Environment Variables
Create a `.env` file in the project root:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key_here  # Optional
LANGFUSE_SECRET_KEY=your_langfuse_secret_key_here  # Optional
LANGFUSE_HOST=your_langfuse_host_here              # Optional
```

### Step 3: Prepare Data Files
Ensure your data directory structure is:
```
data/
├── pdfs/          # Place TelecomPlus FAQ PDF documents here
└── xlsx/          # Place Excel data files here
    ├── clients.xlsx
    ├── forfaits.xlsx
    ├── abonnements.xlsx
    ├── consommation.xlsx
    ├── factures.xlsx
    └── tickets.xlsx
```

### Step 4: Run the Evaluation (Optional)
Test the system performance:
```bash
python evaluate.py
```

### Step 5: Start the Chatbot
Launch the web interface:
```bash
streamlit run app.py
```

### Step 6: Access the Application
Open your browser and navigate to: `http://localhost:8501`

### Step 7: Test the Chatbot
Try asking questions like:
- "What are the family plan options?"
- "How much does international roaming cost in Canada?"
- "What is my current plan?" (for personal data queries)

## 🚀 Usage

### Running the Chatbot

1. **Start the web interface**:
   ```bash
   streamlit run app.py
   ```

2. **Access the application**:
   Open your browser to `http://localhost:8501`

### Example Queries

#### FAQ Questions
- "What are the family plan options?"
- "How much does international roaming cost in Canada?"
- "What is the battery life of your smartphones?"
- "How do I cancel my subscription?"

#### Personal Data Queries
- "What is my current plan?"
- "How much data have I used this month?"
- "Show me my last bill amount"
- "What is the status of my support ticket?"

### Evaluation

Run the evaluation script to test system performance:
```bash
python evaluate.py
```

The system achieves 100% accuracy on the evaluation question set.

## 📊 Data Analysis

The project includes comprehensive data exploration utilities:

```bash
python -m src.utils.data_exploration
```

This analyzes all Excel tables and PDF documents, providing:
- Data quality metrics
- Statistical summaries
- Usage patterns
- Customer insights

## 🗂️ Project Structure

```
dauphine-project-iasd-2025/
├── app.py                      # Streamlit web interface
├── evaluate.py                 # Evaluation script (100% accuracy)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── data/
│   ├── pdfs/                   # FAQ documents
│   └── xlsx/                   # Customer data files
├── src/
│   ├── __init__.py
│   ├── config.py               # Configuration management
│   ├── main.py                 # Entry point
│   ├── agents/
│   │   ├── __init__.py         # Core agent logic & orchestration
│   │   └── evaluation/         # Evaluation utilities
│   ├── prompts/                # LLM prompt templates
│   ├── tools/
│   │   └── __init__.py         # Data querying tools
│   ├── utils/
│   │   └── data_exploration.py # Data analysis utilities
│   └── vectorstore/
│       └── __init__.py         # Vector database setup
└── __pycache__/                # Python cache files
```

## 🔧 Key Components

### Configuration (`src/config.py`)
Centralized configuration for API keys, file paths, and model parameters.

### Main Entry Point (`src/main.py`)
Simple wrapper that calls the orchestrator agent.

### Agent System (`src/agents/__init__.py`)
- `orchestrate()`: Main routing function
- `answer_faq()`: FAQ retrieval and generation
- `answer_data_query()`: Database query processing
- `evaluate_response()`: LLM-as-judge evaluation

### Data Tools (`src/tools/__init__.py`)
DataTools class with methods for querying each Excel table:
- `find_client_by_name()`
- `query_forfaits()`
- `get_consumption_data()`
- `get_billing_info()`

### Vector Store (`src/vectorstore/__init__.py`)
- PDF document loading and chunking
- ChromaDB vectorstore creation
- Embedding generation with sentence-transformers

## 📈 Evaluation Results

The system has been thoroughly evaluated with:
- **25 evaluation questions**
- **100% accuracy achieved**
- **LLM-as-judge methodology** with lenient scoring criteria
- **Comprehensive test coverage** including edge cases

### Recent Improvements
- Fixed question classification for roaming queries
- Enhanced retriever for type-specific searches
- Improved fallback logic for misclassified questions
- Achieved perfect evaluation scores

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run evaluation tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for the IASD 2025 course project
- Powered by Google Gemini 2.5-flash
- LangChain framework for RAG implementation
- Streamlit for the web interface
- ChromaDB for vector storage