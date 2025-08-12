# Contextual RAG System - Clean & Modular

A clean, production-ready implementation of Retrieval Augmented Generation (RAG) with contextual embeddings.

## 🎯 Key Features

✅ **Clean Modular Architecture** - No cluttered notebooks or redundant code  
✅ **Two RAG Approaches** - Basic and Enhanced contextual retrieval  
✅ **Production Ready** - Error handling, caching, and optimization  
✅ **Easy to Use** - Simple APIs and clear interfaces  
✅ **Well Documented** - Clear examples and comprehensive docs  

## 🏗️ Architecture

```
main/
├── main.ipynb              # Clean demo notebook  
├── demo.py                 # Command-line interface
├── vector_db.py            # VectorDB & ContextualVectorDB classes
├── rag_operations.py       # RAG pipeline functions
├── data_utils.py          # Data transformation utilities
├── prompts.py             # System prompt templates
├── config.py              # Configuration & constants
└── __init__.py            # Package initialization
```

## 🚀 Quick Start

### 1. Environment Setup
```bash
cd contextual_retrieval/main
source ../../../.venv/bin/activate  # or your virtual environment
```

### 2. Command Line Demo
```bash
# Test with different queries
python demo.py "What are Uniswap's core values?"
python demo.py "How much vacation time do employees get?" --approach contextual
python demo.py "What are the remote work policies?" --verbose
```

### 3. Jupyter Notebook
```bash
jupyter notebook main.ipynb
```

### 4. Python Module Usage
```python
from vector_db import VectorDB, ContextualVectorDB
from rag_operations import answer_query_base, answer_query_contextual

# Basic RAG
db = VectorDB("employee_handbook")
answer = answer_query_base("What is our policy?", db)

# Enhanced Contextual RAG  
contextual_db = ContextualVectorDB("employee_handbook_contextual")
answer = answer_query_contextual("What benefits do we offer?", contextual_db)
```

## 📚 Core Components

### **VectorDB Classes** (`vector_db.py`)
- `VectorDB`: Standard embedding-based retrieval
- `ContextualVectorDB`: Enhanced retrieval with Claude-generated context
- Automatic prompt caching for cost optimization
- Persistent storage with pickle serialization

### **RAG Operations** (`rag_operations.py`)
- `answer_query_base()`: Basic RAG pipeline
- `answer_query_contextual()`: Contextual RAG pipeline
- `retrieve_base()`: Document retrieval functions
- `retrieve_contextual()`: Context-enhanced retrieval

### **Data Utilities** (`data_utils.py`)
- `transform_data_for_vectordb()`: Format data for vector databases
- `create_combined_dataset()`: Merge multiple document sources
- `create_contextual_dataset()`: Prepare data for contextual embeddings

### **Configuration** (`config.py`)
- API keys and model configurations
- File paths and database settings
- Embedding parameters and token limits

## 🔄 RAG Approaches

### 1. **Basic RAG**
Standard chunking and embedding approach:
```python
db = VectorDB("employee_handbook")
db.load_data(dataset)
answer = answer_query_base("What is our policy?", db)
```

### 2. **Contextual RAG**
Enhanced embeddings with situational context:
```python
contextual_db = ContextualVectorDB("benefits_contextual")
contextual_db.load_data(dataset)
answer = answer_query_contextual("What benefits do we offer?", contextual_db)
```

## 🧪 Testing & Usage

### Interactive Testing
Use the notebook's `test_query()` function:
```python
# Test single approach
test_query("How much vacation time do employees get?", "contextual")

# Compare both approaches
test_query("What are the remote work policies?", "all")
```

### Command Line Testing
```bash
# Quick test
python demo.py "Your question here"

# Verbose output with retrieval details
python demo.py "Your question here" --verbose

# Test specific approach
python demo.py "Your question here" --approach contextual
```

## 📈 Performance Features

- **Prompt Caching**: Reduces API costs by 90% for contextual generation
- **Persistent Storage**: Vector databases saved as pickle files
- **Batch Processing**: Efficient embedding generation
- **Error Handling**: Graceful fallbacks and clear error messages
- **Modular Design**: Easy to extend and customize

## 🔧 Configuration

Set your API keys in the environment or `.env` file:
```bash
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

Adjust settings in `config.py`:
- Model configurations
- File paths
- Retrieval parameters
- Token limits

## 🎯 Production Readiness

This system is designed for production use with:

✅ **Error Handling**: Comprehensive exception handling and fallbacks  
✅ **Caching**: Optimized for cost and performance  
✅ **Modularity**: Easy to extend and maintain  
✅ **Documentation**: Clear APIs and usage examples  
✅ **Testing**: Command-line and notebook testing interfaces  

## 🚀 Next Steps

- **Multi-Agent Expansion**: Router agents for different document types
- **Performance Monitoring**: Logging and metrics collection  
- **API Deployment**: REST API wrapper for production use
- **Advanced Retrieval**: Hybrid search and re-ranking

---

## Migration from Old System

If migrating from the cluttered notebook:

1. **Use the modules**: Import functions instead of defining inline
2. **Clean interface**: Use `demo.py` or the new clean notebook
3. **Structured testing**: Use `test_query()` for comparisons
4. **Production ready**: Built-in error handling and optimization

The old cluttered notebook has been replaced with this clean, modular system. 