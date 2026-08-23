"""
Recursive Document Chunker for RAG Indexing.

Splits markdown/text documents by headers and paragraphs while preserving
section context and metadata.
"""

import re
from typing import Dict, Any, List


class DocumentChunker:
    """Recursive markdown/text chunker with configurable max tokens/chars and overlap."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Splits raw documents into chunk objects enriched with section titles."""
        chunks = []

        for doc in documents:
            content = doc["content"]
            sections = self._split_by_headers(content)

            chunk_seq = 0
            for sec_title, sec_text in sections:
                if not sec_text.strip():
                    continue

                words = sec_text.split()
                if len(words) <= self.chunk_size:
                    chunks.append(self._create_chunk(doc, sec_title, sec_text, chunk_seq))
                    chunk_seq += 1
                else:
                    # Recursive character / word splitting with overlap
                    start = 0
                    while start < len(words):
                        end = start + self.chunk_size
                        chunk_words = words[start:end]
                        chunk_text = " ".join(chunk_words)

                        chunks.append(self._create_chunk(doc, sec_title, chunk_text, chunk_seq))
                        chunk_seq += 1
                        start += (self.chunk_size - self.chunk_overlap)

        return chunks

    def _split_by_headers(self, content: str) -> List[tuple]:
        """Parses markdown headers (# or ## or ###) to track section titles."""
        lines = content.split("\n")
        sections = []
        current_header = "General"
        current_lines = []

        for line in lines:
            if line.startswith("#"):
                if current_lines:
                    sections.append((current_header, "\n".join(current_lines)))
                    current_lines = []
                current_header = line.lstrip("#").strip()
            else:
                current_lines.append(line)

        if current_lines:
            sections.append((current_header, "\n".join(current_lines)))

        return sections

    def _create_chunk(self, doc: Dict[str, Any], section: str, text: str, seq: int) -> Dict[str, Any]:
        chunk_id = f"{doc['source']}#chunk-{seq}"
        return {
            "chunk_id": chunk_id,
            "source": doc["source"],
            "title": doc["title"],
            "section": section,
            "document_type": doc["document_type"],
            "content": text.strip(),
            "ingestion_timestamp": doc["ingestion_timestamp"]
        }
