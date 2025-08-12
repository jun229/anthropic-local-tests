"""RAG system with contextual retrieval capabilities."""

from .vector_db import VectorDB, ContextualVectorDB
from .rag_operations import (
    retrieve_base, retrieve_contextual, retrieve_combined,
    answer_query_base, answer_query_contextual, answer_query_combined
)
from .data_utils import (
    transform_data_for_vectordb, create_contextual_dataset,
    create_combined_dataset, safe_extract_source_info
)
from . import config
from . import prompts

__version__ = "1.0.0" 