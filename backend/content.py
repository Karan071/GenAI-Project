import os
import tempfile
import uuid
from typing import Dict, List

from fastapi import BackgroundTasks, UploadFile, FastAPI, HTTPException, Query
from langchain.text_splitter import CharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings
from langchain_milvus import Milvus
from langchain_openai import ChatOpenAI
from PyPDF2 import PdfReader

app = FastAPI()

class MilvusDBManager:
    """Handles connection to Milvus and manages embedding storage and retrieval."""
    
    def _init_(self, logger, collection_name="specs_embeddings"):
        self.logger = logger
        self.collection_name = collection_name
        self.config = self.read_milvus_config()
        self.embeddings = HuggingFaceEndpointEmbeddings(
            model=self.config["EMBEDDING_ENDPOINT"]
        )
        self.initialize_milvus_connection()

    def read_milvus_config(self):
        """Read and return Milvus configuration with default values."""
        default_configs = {
            "MILVUS_HOST": "milvus",
            "MILVUS_PORT": "19530",
            "EMBEDDING_ENDPOINT": "http://embedding-service:80",
        }
        return read_config_vars(default_configs, ["MILVUS_HOST", "MILVUS_PORT"], self.logger)

    def initialize_milvus_connection(self):
        """Initialize the connection to Milvus."""
        try:
            milvus_uri = f"http://{self.config['MILVUS_HOST']}:{self.config['MILVUS_PORT']}"
            self.milvus = Milvus(
                embedding_function=self.embeddings,
                connection_args={"uri": milvus_uri},
                collection_name=self.collection_name,
                auto_id=False,
                drop_old=True,
            )
            self.logger.info("Connected to Milvus.")
        except Exception as error:
            err_msg = f"Milvus connection failed: {str(error)}"
            self.logger.error(err_msg)
            raise RuntimeError(err_msg) from error

    def store_embeddings(self, texts: List[str], file_id: str):
        """Store embeddings in the Milvus collection, associated with a file ID."""
        try:
            if texts:
                documents = [Document(page_content=text) for text in texts]
                self.milvus.add_documents(documents=documents, ids=[file_id])
                self.logger.info(f"Stored embeddings for file ID: {file_id}")
            else:
                self.logger.warning("No texts for embedding storage.")
        except Exception as error:
            err_msg = f"Embedding storage error: {str(error)}"
            self.logger.error(err_msg)
            raise RuntimeError(err_msg) from error

    def retrieve_relevant_embeddings(self, query: str, top_k: int = 5) -> List[str]:
        """Retrieve relevant embeddings based on query text."""
        try:
            retriever = self.milvus.as_retriever(search_type="similarity", search_kwargs={"k": top_k})
            results = retriever.get_relevant_documents(query)
            return [res.page_content for res in results]
        except Exception as error:
            err_msg = f"Retrieval error: {str(error)}"
            self.logger.error(err_msg)
            raise RuntimeError(err_msg) from error


class ProdLaunch:
    """Orchestrates the product launch workflow."""

    def _init_(self, logger):
        self.logger = logger
        self.config = self.read_prod_launch_config()
        self.llm = ChatOpenAI(
            base_url=self.config["VLLM_ENDPOINT"],
            model=self.config["LLM_MODEL"],
            api_key=self.config["VLLM_KEY"],
            temperature=0,
        )
        self.db_manager = MilvusDBManager(self.logger)

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from all pages of a PDF."""
        try:
            text = ""
            with open(pdf_path, "rb") as file:
                reader = PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() or ""
            return text
        except Exception as error:
            raise RuntimeError(f"PDF extraction error: {str(error)}") from error

    def embed_pdf(self, file_path: str, file_id: str):
        """Embeds the content of a PDF into the database."""
        pdf_text = self.extract_text_from_pdf(file_path)
        splitter = CharacterTextSplitter(separator="\n", chunk_size=200, chunk_overlap=50)
        texts = splitter.split_text(pdf_text)
        self.db_manager.store_embeddings(texts, file_id)

    def answer_question(self, query: str) -> str:
        """Answer a question based on relevant content from Milvus."""
        relevant_content = self.db_manager.retrieve_relevant_embeddings(query)
        context = "\n".join(relevant_content)
        prompt = ChatPromptTemplate.from_messages([{"role": "system", "content": context}, 
                                                   {"role": "user", "content": query}])
        response = self.llm(prompt=prompt.render())
        return response["choices"][0]["message"]["content"]


@app.post("/upload/")
async def upload_pdf(
    files: List[UploadFile], background_tasks: BackgroundTasks, prod_launch: ProdLaunch
):
    """Upload PDFs and start the embedding process."""
    try:
        for file in files:
            file_id = f"file_{uuid.uuid4()}"
            file_extension = file.filename.split(".")[-1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as tmp:
                contents = await file.read()
                tmp.write(contents)
                background_tasks.add_task(prod_launch.embed_pdf, tmp.name, file_id)
        return {"message": "Files uploaded successfully. Embedding in progress."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")


@app.get("/ask/")
async def ask_question(
    query: str = Query(..., description="Question about the PDF content"),
    prod_launch: ProdLaunch = None,
):
    """Answer a question based on the uploaded PDF content."""
    try:
        answer = prod_launch.answer_question(query)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question answering error: {str(e)}")