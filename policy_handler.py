from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_policy_pdf(path: str):
    """
    Loads and splits a PDF document into smaller chunks for processing by language models.

    Args:
        path (str): Path to the PDF file containing HR policy or other documents.

    Returns:
        List[Document]: A list of document chunks, each containing a portion of the original PDF.
    """
    # Initialize the PDF loader using PyMuPDF
    loader = PyMuPDFLoader(path)

    # Load the entire PDF as a list of Document objects
    documents = loader.load()

    # Initialize the text splitter to break content into manageable chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,    # Max number of characters per chunk
        chunk_overlap=200   # Overlap between chunks for context retention
    )

    # Split the loaded documents into smaller chunks
    return splitter.split_documents(documents)
