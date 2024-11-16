# PDF Chat Application

A full-stack application that allows users to chat with their PDF documents using AI. Built with React, FastAPI and Weaviate vector database.

## How It Works

1. Users upload a PDF file through the drag-and-drop interface
2. The backend processes the PDF, chunks it, and creates embeddings
3. Embeddings are stored in Weaviate vector database
4. When users ask questions, relevant context is retrieved using hybrid search
5. The LLM generates responses based on the retrieved context

## Features

- 📁 Drag-and-drop PDF upload interface
- 📄 Side-by-side PDF viewer and chat interface
- 💬 AI-powered chat functionality using Llama model
- 🔍 Vector search using sentence embeddings
- 🚀 Real-time PDF processing and vector storage

## Tech Stack

### Models used

- LLM: `Llama-3.2-1B-Instruct` 4bit quantized
- Embeddings: `all-mpnet-base-v2`

### Frontend

- React.js with React Router
- Tailwind CSS for styling
- Axios for API communication
- React Markdown for message rendering

### Backend

- FastAPI
- PyMuPDF for PDF parsing
- Sentence Transformers for embeddings
- Unsloth's FastLanguageModel for LLM
- Weaviate vector database

## Prerequisites

- Python 3.8+
- Node.js and npm
- CUDA-compatible GPU
- Weaviate Cloud account

<!-- ## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd pdf-chat-app
```

2. Set up the backend:
```bash
cd backend
pip install -r requirements.txt
```

3. Create a `.env` file in the backend directory with your Weaviate credentials:
```
WEAVIATE_URL=your-weaviate-cluster-url
WEAVIATE_API_KEY=your-weaviate-api-key
```

4. Set up the frontend:
```bash
cd ../frontend
npm install
```

## Running the Application

1. Start the backend server:
```bash
cd backend
fastapi run main.py
```

2. Start the frontend development server:
```bash
cd frontend
npm run start
```

3. Open your browser and navigate to `http://localhost:3000` -->

## Project Structure

```
├── backend/
│   ├── models/
│   │   └── model.py          # LLM model loading
│   ├── utils/
│   │   ├── chat.py          # Chat functionality
│   │   ├── embeddings.py    # Document embedding
│   │   ├── pdf_parser.py    # PDF processing
│   │   └── vectordb.py      # Weaviate operations
│   └── main.py              # FastAPI application
└── frontend/
    ├── src/
    │   ├── App.js
    │   ├── FileUpload.jsx   # Upload component
    │   ├── PDFViewer.jsx    # PDF viewer & chat
    │   └── index.js
    └── tailwind.config.js
```

## License

[MIT License](LICENSE)
