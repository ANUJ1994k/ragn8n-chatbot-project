# ragn8n-chatbot-project
Retrieval-Augmented Generation (RAG)-powered FAQ chatbot using n8n
# RAG-Powered FAQ Chatbot with n8n

## Project Overview

This project implements a Retrieval-Augmented Generation (RAG) powered FAQ chatbot using n8n as the primary workflow orchestration tool. The system processes user queries, retrieves relevant context from documents, and generates accurate responses using Large Language Models.

## Architecture

The system follows a modular RAG architecture:
1. **Document Processing**: Ingests PDFs, text, and markdown files
2. **Embedding Generation**: Creates vector representations using OpenAI embeddings
3. **Vector Storage**: Stores embeddings in Pinecone for efficient retrieval
4. **Query Processing**: Handles user input through n8n webhooks
5. **Retrieval**: Performs semantic search to find relevant document chunks
6. **Generation**: Uses OpenAI GPT to generate contextual responses
7. **Response Delivery**: Returns formatted answers with source attribution

## Prerequisites

### Required Services
- **n8n**: Workflow automation platform
- **OpenAI API**: For embeddings and text generation
- **Pinecone**: Vector database for document storage
- **Node.js**: Runtime environment (v16+)

### Environment Variables
Create a `.env` file with:
```
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX_NAME=rag-chatbot-index
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=your_password
```

## Installation & Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd rag-chatbot-project
```

### 2. Install Dependencies
```bash
npm install
pip install -r requirements.txt
```

### 3. Setup Vector Database
```bash
python scripts/setup_pinecone.py
```

### 4. Process Documents
```bash
python scripts/process_documents.py --input data/sample-documents/
```

### 5. Start n8n
```bash
npx n8n start
```

### 6. Import Workflow
1. Open n8n interface (http://localhost:5678)
2. Go to Workflows → Import from File
3. Select `workflows/rag-chatbot-workflow.json`
4. Activate the workflow

## Usage

### API Endpoint
Send POST requests to the webhook URL:
```bash
curl -X POST http://localhost:5678/webhook/rag-chatbot \
  -H "Content-Type: application/json" \
  -d '{"query": "What is your return policy?"}'
```

### Web Form
Access the web form at: `http://localhost:5678/form/rag-chatbot`

## Configuration

### Document Chunking
- **Chunk Size**: 500-1000 tokens
- **Overlap**: 100 tokens
- **Strategy**: Semantic chunking with sentence boundaries

### Retrieval Settings
- **Top-k**: 5 relevant chunks
- **Similarity Threshold**: 0.7
- **Reranking**: Enabled for improved relevance

### LLM Configuration
- **Model**: GPT-4 (fallback to GPT-3.5-turbo)
- **Temperature**: 0.3 for consistent responses
- **Max Tokens**: 500

## Testing

### Run Test Suite
```bash
npm test
```

### Sample Queries
Test with provided sample queries:
```bash
node tests/run_sample_queries.js
```

## Performance Considerations

- **Caching**: Implemented response caching for frequently asked questions
- **Rate Limiting**: Built-in rate limiting to prevent API abuse
- **Error Handling**: Graceful fallbacks for service failures
- **Monitoring**: Query logging and performance metrics

## Security Features

- **Input Validation**: Sanitizes user queries
- **API Key Management**: Secure credential handling
- **Rate Limiting**: Prevents abuse
- **Error Sanitization**: No sensitive data in error messages

## Scalability Improvements

1. **Horizontal Scaling**: Multiple n8n instances with load balancing
2. **Database Optimization**: Implement vector database sharding
3. **Caching Layer**: Redis for response caching
4. **CDN Integration**: Static asset delivery optimization
5. **Monitoring**: Comprehensive logging and alerting

## Troubleshooting

### Common Issues

1. **Vector Search Failing**
   - Check Pinecone API credentials
   - Verify index exists and has data

2. **LLM Responses Poor Quality**
   - Review prompt engineering
   - Adjust retrieval parameters

3. **Workflow Not Triggering**
   - Check webhook URL configuration
   - Verify n8n is running and accessible

### Debug Mode
Enable debug logging:
```bash
N8N_LOG_LEVEL=debug npx n8n start
```

## Contributing

1. Follow code style guidelines
2. Add tests for new features
3. Update documentation
4. Ensure security best practices

## License

MIT License - see LICENSE file for details

## Support

For technical support, please create an issue in the repository or contact the development team.