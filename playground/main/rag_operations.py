"""RAG operations for retrieval and answer generation."""

from typing import List, Dict, Any, Tuple
import anthropic

from config import ANTHROPIC_API_KEY, ANSWER_MODEL, MAX_TOKENS_ANSWER, TEMPERATURE, DEFAULT_TOP_K
from prompts import BASE_RAG_SYSTEM_PROMPT, COMBINED_RAG_SYSTEM_PROMPT
from data_utils import safe_extract_source_info


def retrieve_base(query: str, db, k: int = DEFAULT_TOP_K) -> Tuple[List[Dict[str, Any]], str]:
    """Retrieve relevant documents and format context."""
    results = db.search(query, k=k)
    context = ""
    for result in results:
        chunk = result['metadata']
        context += f"\n{chunk['content']}\n"
    return results, context


def retrieve_contextual(query: str, contextual_db, k: int = 3) -> Tuple[List[Dict[str, Any]], str]:
    """Retrieve relevant documents and format context from contextual database."""
    results = contextual_db.search(query, k=k)
    context = ""
    for result in results:
        chunk = result['metadata']
        # Use the original content for context (the contextualized content was used for better retrieval)
        context += f"\n{chunk['original_content']}\n"
    return results, context


def retrieve_combined(query: str, combined_db, k: int = DEFAULT_TOP_K) -> Tuple[List[Dict[str, Any]], str, List[Dict[str, Any]]]:
    """Retrieve relevant documents from combined database with source information."""
    results = combined_db.search(query, k=k)
    context = ""
    sources = []
    
    for result in results:
        chunk = result['metadata']
        source_doc, heading = safe_extract_source_info(chunk)
        
        # Include source information in context
        source_info = f"[Source: {source_doc} - {heading}]"
        context += f"\n{source_info}\n{chunk.get('content', '')}\n"
        sources.append({
            'source_doc': source_doc,
            'heading': heading,
            'similarity': result['similarity']
        })
    
    return results, context, sources


def answer_query_base(query: str, db) -> str:
    """Answer a query using the basic RAG pipeline."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    documents, context = retrieve_base(query, db)
    prompt = BASE_RAG_SYSTEM_PROMPT.format(query=query, context=context)
    
    response = client.messages.create(
        model=ANSWER_MODEL,
        max_tokens=MAX_TOKENS_ANSWER,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=TEMPERATURE
    )
    
    try:
        return response.content[0].text
    except AttributeError:
        return str(response.content[0])


def answer_query_contextual(query: str, contextual_db) -> str:
    """Answer a query using the Contextual RAG pipeline."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    documents, context = retrieve_contextual(query, contextual_db)
    prompt = BASE_RAG_SYSTEM_PROMPT.format(query=query, context=context)
    
    response = client.messages.create(
        model=ANSWER_MODEL,
        max_tokens=MAX_TOKENS_ANSWER,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=TEMPERATURE
    )
    
    try:
        if hasattr(response.content[0], 'text'):
            return response.content[0].text
        else:
            return str(response.content[0])
    except (AttributeError, IndexError):
        return str(response.content)


def answer_query_combined(query: str, combined_db) -> Tuple[str, str]:
    """Answer a query using the Combined RAG pipeline."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    documents, context, sources = retrieve_combined(query, combined_db)
    
    # Create source summary
    source_summary = "Sources consulted:\n"
    for source in sources:
        source_summary += f"• {source['source_doc']}: {source['heading']} (similarity: {source['similarity']:.3f})\n"
    
    prompt = COMBINED_RAG_SYSTEM_PROMPT.format(query=query, context=context)
    
    response = client.messages.create(
        model=ANSWER_MODEL,
        max_tokens=500,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=TEMPERATURE
    )
    
    try:
        answer = response.content[0].text
    except AttributeError:
        answer = str(response.content[0])
    
    return answer, source_summary 