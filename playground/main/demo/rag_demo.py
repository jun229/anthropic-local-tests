#!/usr/bin/env python3
"""
Simple command-line demo of the clean modular RAG system.

Usage:
    python demo.py "What are Uniswap's core values?"
    python demo.py "How much vacation time do employees get?" --approach contextual

Setup:
    1. Activate your virtual environment
    2. Ensure you have the required dependencies installed
    3. Set your API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY)
"""

import sys
import argparse
import textwrap

def wrap_text(text: str, width: int = 90) -> str:
    """Wrap text to specified width while preserving paragraph breaks."""
    if not text:
        return text
    
    # Split by double newlines to preserve paragraph breaks
    paragraphs = text.split('\n\n')
    wrapped_paragraphs = []
    
    for paragraph in paragraphs:
        # Remove single newlines within paragraphs and wrap
        cleaned_paragraph = paragraph.replace('\n', ' ').strip()
        if cleaned_paragraph:
            wrapped = textwrap.fill(cleaned_paragraph, width=width)
            wrapped_paragraphs.append(wrapped)
    
    return '\n\n'.join(wrapped_paragraphs)

def check_requirements():
    """Check if required modules are available."""
    try:
        import anthropic
        import openai
        from dotenv import load_dotenv
        return True
    except ImportError as e:
        print(f"❌ Missing required dependency: {e}")
        print("\n🔧 Setup Instructions:")
        print("1. Activate your virtual environment")
        print("2. Install dependencies: pip install anthropic openai python-dotenv")
        print("3. Set your API keys in environment variables")
        return False

def main():
    if not check_requirements():
        sys.exit(1)
    
    # Import modules after checking requirements
    try:
        from vector_db import VectorDB, ContextualVectorDB
        from rag_operations import answer_query_base, answer_query_contextual
        from data_utils import transform_data_for_vectordb
        import config
        import json
    except ImportError as e:
        print(f"❌ Error importing modules: {e}")
        print("Make sure you're in the correct directory and have the required files.")
        sys.exit(1)

    def setup_databases():
        """Initialize the vector databases."""
        print("🔧 Setting up databases...")
        
        # Basic RAG database
        try:
            with open(config.EMPLOYEE_HANDBOOK_PATH, 'r') as f:
                employee_handbook_raw = json.load(f)
            
            employee_handbook = transform_data_for_vectordb(employee_handbook_raw, "employee_handbook")
            basic_db = VectorDB("employee_handbook")
            basic_db.load_data(employee_handbook)
            print("✅ Basic RAG database loaded")
        except Exception as e:
            print(f"❌ Error loading basic database: {e}")
            basic_db = None
        
        # Contextual RAG database
        try:
            contextual_db = ContextualVectorDB("employee_handbook_contextual")
            contextual_db.load_db()
            print("✅ Contextual RAG database loaded")
        except Exception as e:
            print(f"❌ Error loading contextual database: {e}")
            contextual_db = None
        
        return basic_db, contextual_db

    parser = argparse.ArgumentParser(description="Demo the clean modular RAG system")
    parser.add_argument("query", help="Query to ask the RAG system")
    parser.add_argument("--approach", choices=["basic", "contextual", "both"], 
                       default="both", help="Which RAG approach to use")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Show detailed retrieval information")
    
    args = parser.parse_args()
    
    print("🚀 Clean Modular RAG System Demo")
    print("=" * 50)
    
    # Setup databases
    basic_db, contextual_db = setup_databases()
    
    if not basic_db and not contextual_db:
        print("❌ No databases available. Please check your data files.")
        print("\n💡 Make sure you have:")
        print("- employee_handbook.json in the data directory")
        print("- Pre-computed contextual embeddings (employee_handbook_contextual)")
        sys.exit(1)
    
    print(f"\n🔍 Query: {args.query}")
    print("-" * 50)
    
    # Basic RAG
    if args.approach in ["basic", "both"] and basic_db:
        print("\n📝 BASIC RAG:")
        try:
            answer = answer_query_base(args.query, basic_db)
            print(wrap_text(answer))
            
            if args.verbose:
                results = basic_db.search(args.query, k=3)
                print(f"\n📊 Retrieved {len(results)} chunks with similarities:")
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result['similarity']:.3f}")
        
        except Exception as e:
            print(f"❌ Error with basic RAG: {e}")
    
    # Contextual RAG
    if args.approach in ["contextual", "both"] and contextual_db:
        print("\n🧠 CONTEXTUAL RAG:")
        try:
            answer = answer_query_contextual(args.query, contextual_db)
            print(wrap_text(answer))
            
            if args.verbose:
                results = contextual_db.search(args.query, k=3)
                print(f"\n📊 Retrieved {len(results)} chunks with similarities:")
                for i, result in enumerate(results, 1):
                    metadata = result['metadata']
                    print(f"  {i}. {result['similarity']:.3f} - {metadata.get('heading', 'N/A')}")
        
        except Exception as e:
            print(f"❌ Error with contextual RAG: {e}")
    
    print("\n✅ Demo completed!")


if __name__ == "__main__":
    main() 