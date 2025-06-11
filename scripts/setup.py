#!/usr/bin/env python3
"""
Document Processing Script for RAG Chatbot
Processes PDF, text, and markdown files and stores embeddings in Pinecone
"""

import os
import argparse
import logging
from typing import List, Dict, Any
import json
from pathlib import Path
import hashlib
import uuid

# Required libraries
import PyPDF2
import markdown
import openai
import vector
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import tiktoken

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Handles document processing and embedding generation for RAG system"""
    
    def __init__(self):
        """Initialize the document processor with API keys and configurations"""
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.pinecone_api_key = os.getenv('VECTOR_API_KEY')
        self.pinecone_environment = os.getenv('VECTOR_ENVIRONMENT')
        self.pinecone_index_name = os.getenv('VECTOR_INDEX_NAME', 'rag-chatbot-index')
        
        if not all([self.openai_api_key, self.vector_api_key, self.pinecone_environment]):
            raise ValueError("Missing required environment variables")
        
        # Initialize OpenAI
        openai.api_key = self.openai_api_key
        
        # Initialize Pinecone
        pinecone.init(
            api_key=self.vector_api_key,
            environment=self.vector_environment
        )
        
        # Setup text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,  # Target 500-1000 tokens
            chunk_overlap=100,
            length_function=self._count_tokens,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        
        # Initialize tokenizer for token counting
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        logger.info("Document processor initialized successfully")
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken"""
        return len(self.tokenizer.encode(text))
    
    def read_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {e}")
            return ""
    
    def read_text_file(self, file_path: str) -> str:
        """Read plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {e}")
            return ""
    
    def read_markdown(self, file_path: str) -> str:
        """Read and convert markdown to plain text"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                md_content = file.read()
                # Convert markdown to HTML then strip HTML tags for plain text
                html = markdown.markdown(md_content)
                # Simple HTML tag removal (for more robust solution, use BeautifulSoup)
                import re
                text = re.sub(r'<[^>]+>', '', html)
                return text.strip()
        except Exception as e:
            logger.error(f"Error reading markdown file {file_path}: {e}")
            return ""
    
    def process_document(self, file_path: str) -> List[Document]:
        """Process a single document and return chunks"""
        file_path = Path(file_path)
        file_extension = file_path.suffix.lower()
        
        logger.info(f"Processing document: {file_path}")
        
        # Read document based on file type
        if file_extension == '.pdf':
            content = self.read_pdf(str(file_path))
        elif file_extension == '.md':
            content = self.read_markdown(str(file_path))
        elif file_extension in ['.txt', '.text']:
            content = self.read_text_file(str(file_path))
        else:
            logger.warning(f"Unsupported file type: {file_extension}")
            return []
        
        if not content:
            logger.warning(f"No content extracted from {file_path}")
            return []
        
        # Create document object
        document = Document(
            page_content=content,
            metadata={
                "source": str(file_path.name),
                "file_path": str(file_path),
                "file_type": file_extension,
                "file_size": file_path.stat().st_size,
                "processed_at": str(pd.Timestamp.now())
            }
        )
        
        # Split document into chunks
        chunks = self.text_splitter.split_documents([document])
        
        logger.info(f"Created {len(chunks)} chunks from {file_path}")
        return chunks
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        try:
            response = openai.Embedding.create(
                model="text-embedding-ada-002",
                input=texts
            )
            return [item['embedding'] for item in response['data']]
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return []
    
    def create_pinecone_index(self):
        """Create Pinecone index if it doesn't exist"""
        try:
            # Check if index exists
            if self.pinecone_index_name not in pinecone.list_indexes():
                logger.info(f"Creating Pinecone index: {self.pinecone_index_name}")
                pinecone.create_index(
                    name=self.pinecone_index_name,
                    dimension=1536,  # OpenAI embedding dimension
                    metric="cosine",
                    pods=1,
                    replicas=1,
                    pod_type="p1.x1"
                )
                logger.info("Index created successfully")
            else:
                logger.info("Index already exists")
        except Exception as e:
            logger.error(f"Error creating index: {e}")
            raise
    
    def store_embeddings(self, chunks: List[Document]):
        """Store document embeddings in Pinecone"""
        if not chunks:
            logger.warning("No chunks to store")
            return
        
        # Get or create index
        index = pinecone.Index(self.pinecone_index_name)
        
        # Process chunks in batches
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i + batch_size]
            
            # Prepare texts and metadata
            texts = [chunk.page_content for chunk in batch_chunks]
            
            # Generate embeddings
            embeddings = self.generate_embeddings(texts)
            
            if not embeddings:
                logger.error("Failed to generate embeddings for batch")
                continue
            
            # Prepare vectors for Pinecone
            vectors = []
            for j, (chunk, embedding) in enumerate(zip(batch_