"""
Document Loader for Enterprise RAG Knowledge Base.

Loads Markdown, Text, and PDF files from local directory structure and attaches
rich metadata (source, title, section, document_type, ingestion_timestamp).
"""

import os
import glob
from datetime import datetime, timezone
from typing import Dict, Any, List


class DocumentLoader:
    """Loads enterprise knowledge documents from disk with metadata enrichment."""

    def __init__(self, knowledge_base_dir: str = None):
        self.knowledge_base_dir = knowledge_base_dir or os.path.join(os.getcwd(), "ai", "knowledge_base")

    def load_documents(self) -> List[Dict[str, Any]]:
        """Scans knowledge base directory and loads all .md, .txt, and project documentation."""
        documents = []

        if not os.path.exists(self.knowledge_base_dir):
            return documents

        file_paths = glob.glob(os.path.join(self.knowledge_base_dir, "*.md")) + \
                     glob.glob(os.path.join(self.knowledge_base_dir, "*.txt"))

        readme_path = os.path.join(os.getcwd(), "README.md")
        if os.path.exists(readme_path) and readme_path not in file_paths:
            file_paths.append(readme_path)

        for path in file_paths:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()

                filename = os.path.basename(path)
                doc_title = filename.replace(".md", "").replace(".txt", "").replace("_", " ").title()
                
                domain = "general"
                if "fraud" in filename or "credit" in filename:
                    domain = "credit_cards"
                elif "bank" in filename:
                    domain = "banking"
                elif "health" in filename:
                    domain = "healthcare"
                elif "insurance" in filename:
                    domain = "insurance"
                elif "retail" in filename:
                    domain = "retail"
                elif "architecture" in filename or "platform" in filename:
                    domain = "platform_architecture"

                documents.append({
                    "source": filename,
                    "filepath": path,
                    "title": doc_title,
                    "document_type": domain,
                    "content": content,
                    "ingestion_timestamp": datetime.now(timezone.utc).isoformat()
                })
            except Exception as e:
                print(f"[DocumentLoader] Error reading {path}: {e}")

        return documents
