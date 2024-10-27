from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List

app = FastAPI()

# Enable CORS for all origins (for testing purposes, adjust as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for uploaded PDFs (file names as keys, content as values)
pdf_store = {}

@app.post("/upload_pdf", tags=["PDF"])
async def upload_pdf(files: List[UploadFile] = File(...)):
    """
    Upload one or more PDF files and store them in memory.
    """
    for file in files:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
        pdf_store[file.filename] = await file.read()
    return JSONResponse(
        status_code=200, content={"message": "Files uploaded successfully!"}
    )

@app.post("/ask_question", tags=["PDF"])
async def ask_question(request: Request):
    """
    Receive a question and respond with answers based on uploaded PDFs.
    """
    data = await request.json()
    question = data.get("question")
    if not question:
        raise HTTPException(status_code=400, detail="Question is required.")

    if not pdf_store:
        raise HTTPException(status_code=404, detail="No PDFs uploaded yet.")

    # Simple mock logic (replace with your actual PDF-based Q&A logic)
    answers = [f"Answer based on {name}: {question}" for name in pdf_store.keys()]

    return JSONResponse(status_code=200, content={"answers": answers})
