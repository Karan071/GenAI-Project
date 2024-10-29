"""FastAPI backend for a document chat application with PDF ingestion and LLM-powered responses."""

from fastapi import FastAPI, HTTPException, UploadFile, File
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.llms.openai_like import OpenAILike
from llama_index.core.llms import ChatMessage
from llama_index.core import VectorStoreIndex, Settings
from pydantic import BaseModel
from typing import List
import logging
from llama_index.core import Document
import uuid
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from fastapi.middleware.cors import CORSMiddleware
import fitz

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

embed_model = HuggingFaceEmbedding(model_name="MODEL_NAME")

chat_store = SimpleChatStore()
chat_memory = ChatMemoryBuffer.from_defaults(
    token_limit=3000,
    chat_store=chat_store,
    chat_store_key="u1",
)

llm = OpenAILike(
    model="LLM_MODEL",
    api_base="API_BASE", 
    api_key="API_KEY",
    is_chat_model=True,
    temperature=0
)

Settings.embed_model = embed_model
Settings.llm = llm

class ChatQuery(BaseModel):
    """Model for chat query requests."""
    query: str

class IngestDocs(BaseModel):
    """Model for document ingestion requests."""
    docs: List[Document]

query_engine = None

def extract_text_from_pdf(file: UploadFile) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        file (UploadFile): The uploaded PDF file
        
    Returns:
        str: Extracted text from the PDF
        
    Raises:
        HTTPException: If there's an error reading the PDF file
    """
    try:
        pdf_document = fitz.open(stream=file.file.read(), filetype="pdf")
        text = ""
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
        return text
    except Exception as e:
        logging.error(f"Error reading PDF file: {e}")
        raise HTTPException(status_code=500, detail=f"PDF file reading error: {e}")

@app.post("/ingest")
async def ingest(docs: List[UploadFile] = File(...)):
    """
    Ingest PDF documents and create a searchable index.
    
    Args:
        docs (List[UploadFile]): List of PDF files to ingest
        
    Returns:
        dict: Status message indicating successful ingestion
        
    Raises:
        HTTPException: If there's an error processing files or creating index
    """
    global query_engine
    documents = []

    for doc in docs:
        logging.debug(f"Processing file: {doc.filename}")
        if doc.content_type == "application/pdf":
            try:
                text = extract_text_from_pdf(doc)
                documents.append(Document(text=text, id_=str(uuid.uuid4())))
                logging.debug(f"Extracted text: {text[:500]}")
            except Exception as e:
                logging.error(f"Error reading PDF file {doc.filename}: {e}")
                raise HTTPException(status_code=500, detail=f"Error reading PDF file: {e}")
        else:
            logging.warning(f"Unsupported file type: {doc.content_type}")
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF files.")

    logging.debug("Creating index from documents")
    try:
        index = VectorStoreIndex.from_documents(documents)
        query_engine = index.as_query_engine(response_mode="tree_summarize")
    except Exception as e:
        logging.error(f"Error creating index: {e}")
        raise HTTPException(status_code=500, detail="Index creation error")

    return {"status": "PDF documents ingested and index created"}

@app.post("/chat")
async def chat(chat_query: ChatQuery):
    """
    Process a chat query and return an AI-generated response.
    
    Args:
        chat_query (ChatQuery): The user's chat query
        
    Returns:
        dict: AI-generated response to the query
        
    Raises:
        HTTPException: If no document index exists
    """
    if not query_engine:
        raise HTTPException(status_code=400, detail="Index not found. Please ingest documents first.")

    query = chat_query.query
    chat_memory.put(ChatMessage(role="user", content=f"{query}"))
    get_chat_history = chat_memory.get()
    ret = query_engine.query(query)

    llm_inference_prompt = f"given the chat history : {get_chat_history} and current_query : {query} and current_vector_retrieval : {ret} respond with a suitable answer"
    message = [
        ChatMessage(role="system", content="You are a helpful assistant."),
        ChatMessage(role="user", content=llm_inference_prompt)
    ]

    response = llm.chat(message)
    response_content = str(response).replace("assistant:", "").strip()
    return {"response": str(response)}
