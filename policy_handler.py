from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List
from langchain.schema import Document

def load_policy_pdf(path: str) -> List[Document]:
    """
    Loads and splits a PDF document into smaller chunks for retrieval-based QA systems.

    This function:
    - Loads the PDF using PyMuPDF.
    - Splits the text into overlapping chunks to preserve context.
    - Retains metadata like page numbers to enable traceable responses.

    Args:
        path (str): Path to the PDF file containing HR policy or similar documents.

    Returns:
        List[Document]: A list of document chunks with metadata.
    """
    # Load the PDF document using PyMuPDF (returns a list of Document objects)
    loader = PyMuPDFLoader(path)
    documents = loader.load()  # Each document contains metadata including 'page'

    # Initialize the text splitter to break content into manageable chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,    # Max characters per chunk
        chunk_overlap=200   # Overlap between chunks for better context flow
    )

    # Split the loaded documents into smaller chunks (preserving metadata)
    split_docs = splitter.split_documents(documents)

    return split_docs
