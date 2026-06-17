import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader

load_dotenv()

class VolatileChromaClient:
    """
    In-memory Chroma store for testing.
    A new empty database is created on every startup; load_documents() must
    repopulate it from data/docs each run. Nothing persists after the program exits.
    """

    def __init__(self):
        self.documents_directory = Path("data/docs")
        self.client = chromadb.EphemeralClient()
        self.collection = self.client.get_or_create_collection("job_descriptions")
        self.load_documents()

    def load_documents(self):
        """
        Read the job description PDF, embed it, and add it to the collection.
        """
        pdf_path = self.documents_directory / "Python Developer Job Description.pdf"
        text = self._read_pdf_text(pdf_path)
        if not text:
            return
        embedding = self._create_embedding(text)
        self.collection.add(
            ids=["python-developer-job-description"],
            documents=[text],
            embeddings=[embedding],
        )

    def _read_pdf_text(self, pdf_path):
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            page_text = (page.extract_text() or "").strip()
            if page_text:
                text += page_text + "\n\n"
        text = text.strip()
        if not text:
            return ""
        return text

    def _create_embedding(self, text):
        if not text:
            return None

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        return response.data[0].embedding

    def search(self, query):
        query_embedding = self._create_embedding(query)
        if query_embedding is None:
            return "No job description information is loaded yet."

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=1,
        )
        documents = results.get("documents", [[]])[0]
        if not documents:
            return "No job description information is loaded yet."
        return "\n\n".join(documents)
