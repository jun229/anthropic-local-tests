"""Vector database classes for RAG system."""

import os
import pickle
import json
import numpy as np
import threading
import time
from openai import OpenAI
import anthropic
from typing import List, Dict, Any, Tuple
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import (
    OPENAI_API_KEY, ANTHROPIC_API_KEY, EMBEDDING_MODEL, CONTEXT_MODEL,
    EMBEDDING_BATCH_SIZE, MAX_CHUNK_TOKENS, OVERLAP_TOKENS, MAX_TOKENS_CONTEXT
)
from prompts import DOCUMENT_CONTEXT_PROMPT, CONTEXTUAL_CHUNK_PROMPT


class VectorDB:
    """In-memory vector database for document embeddings."""
    
    # Initialize necessary variables, and create the correspoding pkl file which represents the embeddings
    def __init__(self, name: str, api_key: str = None):
        if api_key is None:
            api_key = OPENAI_API_KEY
        self.client = OpenAI(api_key=api_key)
        self.name = name
        self.embeddings = []
        self.metadata = []
        self.query_cache = {}
        self.db_path = f"./data/{name}/vector_db.pkl"

    # Load data into the local vector database
    def load_data(self, dataset: List[Dict[str, Any]]):
        """Load and embed documents into the vector database."""
        if self.embeddings and self.metadata:
            print("Vector database is already loaded. Skipping data loading.")
            return
        if os.path.exists(self.db_path):
            print("Loading vector database from disk.")
            self.load_db()
            return

        texts_to_embed = []
        metadata = []
        total_chunks = sum(len(doc['chunks']) for doc in dataset)
        
        # Showcase the progress of the data loading process
        with tqdm(total=total_chunks, desc="Processing chunks") as pbar:
            for doc in dataset:
                for chunk in doc['chunks']:
                    texts_to_embed.append(chunk['content'])
                    # Start with all chunk fields to preserve custom metadata
                    chunk_metadata = chunk.copy()
                    # Add document-level fields
                    chunk_metadata.update({
                        'doc_id': doc['doc_id'],
                        'original_uuid': doc['original_uuid']
                    })
                    metadata.append(chunk_metadata)
                    pbar.update(1)

        self._embed_and_store(texts_to_embed, metadata)
        self.save_db()
        print(f"Vector database loaded and saved. Total chunks processed: {len(texts_to_embed)}")

    # Split text into overlapping chunks that fit within token limits
    def _chunk_text(self, text: str, max_tokens: int = MAX_CHUNK_TOKENS, overlap_tokens: int = OVERLAP_TOKENS) -> List[str]:
        """Split text into overlapping chunks that fit within token limits."""
        max_chars = max_tokens * 4
        overlap_chars = overlap_tokens * 4
        
        if len(text) <= max_chars:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + max_chars
            
            if end < len(text):
                break_point = text.rfind('.', end - 500, end)
                if break_point == -1:
                    break_point = text.rfind('\n', end - 500, end)
                if break_point != -1:
                    end = break_point + 1
            
            chunk = text[start:end]
            chunks.append(chunk)
            
            if end >= len(text):
                break
            start = end - overlap_chars
            
        return chunks

    def _embed_and_store(self, texts: List[str], data: List[Dict[str, Any]]):
        """Create embeddings for texts and store them."""
        batch_size = EMBEDDING_BATCH_SIZE
        with tqdm(total=len(texts), desc="Embedding chunks") as pbar:
            result = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]
                response = self.client.embeddings.create(
                    input=batch,
                    model=EMBEDDING_MODEL
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                result.extend(batch_embeddings)
                pbar.update(len(batch))
        
        self.embeddings = result
        self.metadata = data

    def search(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """Search for similar documents using cosine similarity."""
        if query in self.query_cache:
            query_embedding = self.query_cache[query]
        else:
            query_embedding = self.client.embeddings.create(
                input=[query], 
                model=EMBEDDING_MODEL
            ).data[0].embedding
            self.query_cache[query] = query_embedding

        if not self.embeddings:
            raise ValueError("No data loaded in the vector database.")

        similarities = np.dot(self.embeddings, query_embedding)
        top_indices = np.argsort(similarities)[::-1][:k]
        
        top_results = []
        for idx in top_indices:
            result = {
                "metadata": self.metadata[idx],
                "similarity": float(similarities[idx]),
            }
            top_results.append(result)
        
        return top_results

    def save_db(self):
        """Save database to disk."""
        data = {
            "embeddings": self.embeddings,
            "metadata": self.metadata,
            "query_cache": json.dumps(self.query_cache),
        }
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, "wb") as file:
            pickle.dump(data, file)

    def load_db(self):
        """Load database from disk."""
        if not os.path.exists(self.db_path):
            raise ValueError("Vector database file not found. Use load_data to create a new database.")
        with open(self.db_path, "rb") as file:
            data = pickle.load(file)
        self.embeddings = data["embeddings"]
        self.metadata = data["metadata"]
        self.query_cache = json.loads(data["query_cache"])


"""
============================================================================================
Contextual Vector Database
============================================================================================
"""
class ContextualVectorDB:
    """Vector database with contextual embeddings for improved retrieval."""
    
    def __init__(self, name: str, anthropic_api_key: str = None, openai_api_key: str = None):
        if anthropic_api_key is None:
            anthropic_api_key = ANTHROPIC_API_KEY
        if openai_api_key is None:
            openai_api_key = OPENAI_API_KEY
        
        self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.name = name
        self.embeddings = []
        self.metadata = []
        self.query_cache = {}
        self.db_path = f"./data/{name}/contextual_vector_db.pkl"

        self.token_counts = {
            'input': 0,
            'output': 0,
            'cache_read': 0,
            'cache_creation': 0
        }
        self.token_lock = threading.Lock()

    def situate_context(self, doc: str, chunk: str) -> Tuple[str, Any]:
        """Generate contextual information for a chunk within its document."""
        response = self.anthropic_client.messages.create(
            model=CONTEXT_MODEL,
            max_tokens=MAX_TOKENS_CONTEXT,
            temperature=0.0,
            messages=[
                {
                    "role": "user", 
                    "content": [
                        {
                            "type": "text",
                            "text": DOCUMENT_CONTEXT_PROMPT.format(doc_content=doc),
                            "cache_control": {"type": "ephemeral"}
                        },
                        {
                            "type": "text",
                            "text": CONTEXTUAL_CHUNK_PROMPT.format(chunk_content=chunk),
                        },
                    ]
                },
            ],
            extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"}
        )
        
        try:
            response_text = response.content[0].text
        except AttributeError:
            response_text = str(response.content[0])
        return response_text, response.usage

    def load_data(self, dataset: List[Dict[str, Any]], parallel_threads: int = 1):
        """Load data and create contextual embeddings."""
        if self.embeddings and self.metadata:
            print("Vector database is already loaded. Skipping data loading.")
            return
        if os.path.exists(self.db_path):
            print("Loading vector database from disk.")
            self.load_db()
            return

        texts_to_embed = []
        metadata = []
        total_chunks = sum(len(doc['chunks']) for doc in dataset)

        def process_chunk(doc, chunk):
            contextualized_text, usage = self.situate_context(doc['content'], chunk['content'])
            with self.token_lock:
                self.token_counts['input'] += usage.input_tokens
                self.token_counts['output'] += usage.output_tokens
                self.token_counts['cache_read'] += usage.cache_read_input_tokens
                self.token_counts['cache_creation'] += usage.cache_creation_input_tokens
            
            return {
                'text_to_embed': f"{chunk['content']}\n\n{contextualized_text}",
                'metadata': {
                    'doc_id': doc['doc_id'],
                    'original_uuid': doc['original_uuid'],
                    'chunk_id': chunk['chunk_id'],
                    'original_index': chunk['original_index'],
                    'original_content': chunk['content'],
                    'contextualized_content': contextualized_text
                }
            }

        print(f"Processing {total_chunks} chunks with {parallel_threads} threads")
        with ThreadPoolExecutor(max_workers=parallel_threads) as executor:
            futures = []
            for doc in dataset:
                for chunk in doc['chunks']:
                    futures.append(executor.submit(process_chunk, doc, chunk))
            
            for future in tqdm(as_completed(futures), total=total_chunks, desc="Processing chunks"):
                result = future.result()
                texts_to_embed.append(result['text_to_embed'])
                metadata.append(result['metadata'])

        self._embed_and_store(texts_to_embed, metadata)
        self.save_db()

        print(f"Contextual Vector database loaded and saved. Total chunks processed: {len(texts_to_embed)}")
        self._print_token_usage()

    def _embed_and_store(self, texts: List[str], data: List[Dict[str, Any]]):
        """Create embeddings for contextualized texts."""
        batch_size = EMBEDDING_BATCH_SIZE
        result = []
        with tqdm(total=len(texts), desc="Embedding chunks") as pbar:
            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]
                response = self.openai_client.embeddings.create(
                    input=batch,
                    model=EMBEDDING_MODEL
                )
                batch_embeddings = [item.embedding for item in response.data]
                result.extend(batch_embeddings)
                pbar.update(len(batch))

        self.embeddings = result
        self.metadata = data

    def search(self, query: str, k: int = 20) -> List[Dict[str, Any]]:
        """Search for similar contextualized documents."""
        if query in self.query_cache:
            query_embedding = self.query_cache[query]
        else:
            response = self.openai_client.embeddings.create(
                input=[query],
                model=EMBEDDING_MODEL
            )
            query_embedding = response.data[0].embedding
            self.query_cache[query] = query_embedding

        if not self.embeddings:
            raise ValueError("No data loaded in the vector database.")

        similarities = np.dot(self.embeddings, query_embedding)
        top_indices = np.argsort(similarities)[::-1][:k]
        
        top_results = []
        for idx in top_indices:
            result = {
                "metadata": self.metadata[idx],
                "similarity": float(similarities[idx]),
            }
            top_results.append(result)
        return top_results

    def save_db(self):
        """Save contextual database to disk."""
        data = {
            "embeddings": self.embeddings,
            "metadata": self.metadata,
            "query_cache": json.dumps(self.query_cache),
        }
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, "wb") as file:
            pickle.dump(data, file)

    def load_db(self):
        """Load contextual database from disk."""
        if not os.path.exists(self.db_path):
            raise ValueError("Vector database file not found. Use load_data to create a new database.")
        with open(self.db_path, "rb") as file:
            data = pickle.load(file)
        self.embeddings = data["embeddings"]
        self.metadata = data["metadata"]
        self.query_cache = json.loads(data["query_cache"])

    def _print_token_usage(self):
        """Print token usage statistics."""
        print(f"Total input tokens without caching: {self.token_counts['input']}")
        print(f"Total output tokens: {self.token_counts['output']}")
        print(f"Total input tokens written to cache: {self.token_counts['cache_creation']}")
        print(f"Total input tokens read from cache: {self.token_counts['cache_read']}")
        
        total_tokens = self.token_counts['input'] + self.token_counts['cache_read'] + self.token_counts['cache_creation']
        savings_percentage = (self.token_counts['cache_read'] / total_tokens) * 100 if total_tokens > 0 else 0
        print(f"Total input token savings from prompt caching: {savings_percentage:.2f}%") 