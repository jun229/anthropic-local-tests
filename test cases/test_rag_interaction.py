#!/usr/bin/env python3
"""
Simple script to interact with your RAG database using Claude
Run this to ask questions about Anthropic documentation
"""

import os
import sys
import pickle
import json
import numpy as np
from openai import OpenAI
import anthropic

# Add the RAG directory to the path
sys.path.append('skills/retrieval_augmented_generation')

# Set up your API keys (make sure these are set in your environment)
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class SimpleRAG:
    def __init__(self, db_path="skills/retrieval_augmented_generation/data/anthropic_docs/vector_db.pkl"):
        self.db_path = db_path
        self.load_db()
    
    def load_db(self):
        """Load the existing vector database"""
        try:
            with open(self.db_path, "rb") as file:
                data = pickle.load(file)
            self.embeddings = data["embeddings"]
            self.metadata = data["metadata"]
            self.query_cache = json.loads(data.get("query_cache", "{}"))
            print(f"✅ Loaded database with {len(self.embeddings)} documents")
        except FileNotFoundError:
            print(f"❌ Database not found at {self.db_path}")
            print("Run the RAG guide notebook first to create the database")
            sys.exit(1)
    
    def search(self, query, k=3):
        """Search for relevant documents"""
        # Get query embedding
        if query in self.query_cache:
            query_embedding = self.query_cache[query]
        else:
            response = openai_client.embeddings.create(
                input=[query],
                model="text-embedding-3-small"
            )
            query_embedding = response.data[0].embedding
        
        # Calculate similarities
        similarities = np.dot(self.embeddings, query_embedding)
        top_indices = np.argsort(similarities)[::-1][:k]
        
        results = []
        for idx in top_indices:
            results.append({
                "text": self.metadata[idx]["text"],
                "url": self.metadata[idx].get("url", "Unknown"),
                "similarity": similarities[idx]
            })
        
        return results
    
    def ask_question(self, question):
        """Ask a question and get an answer from Claude"""
        print(f"\n🔍 Searching for: {question}")
        
        # Retrieve relevant documents
        results = self.search(question, k=3)
        
        # Build context
        context = ""
        print("\n📄 Found relevant documents:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. Similarity: {result['similarity']:.3f}")
            print(f"     URL: {result['url']}")
            context += f"\n--- Document {i} ---\n{result['text']}\n"
        
        # Ask Claude
        prompt = f"""Based on the following documentation, please answer this question: {question}

Documentation:
{context}

Please provide a clear, helpful answer based on the documentation provided. If the documentation doesn't contain enough information to answer the question, please say so."""

        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Extract text from response
        if response.content and len(response.content) > 0:
            content_block = response.content[0]
            if hasattr(content_block, 'text'):
                return content_block.text
            else:
                return str(content_block)
        else:
            return "No response received from Claude"

def main():
    print("🤖 Claude RAG Testing Tool")
    print("Ask questions about Anthropic documentation!")
    print("Type 'quit' to exit\n")
    
    rag = SimpleRAG()
    
    while True:
        question = input("\n❓ Your question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not question:
            continue
            
        try:
            answer = rag.ask_question(question)
            print(f"\n🤖 Claude's Answer:\n{answer}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 