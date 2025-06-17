import os
from langchain_groq import ChatGroq
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from policy_handler import load_policy_pdf

# Constants for file paths
INDEX_DIR = "faiss_index"  # Directory to store/load FAISS index
PDF_PATH = "data/POLICIES 2.3- Code of Conduct, Work Hour Policy & Leave Policy 2025.pdf"

def get_or_create_qa_chain():
    """
    Creates or loads a RetrievalQA chain for querying HR policy documents.

    This function initializes a text embedding model, builds (or loads) a FAISS vector index 
    from the policy PDF, and sets up a RetrievalQA chain with a Groq-powered LLM (LLaMA 3 model).

    Returns:
        RetrievalQA: A ready-to-use question-answering chain.
    """
    # Initialize HuggingFace sentence transformer for creating embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Load FAISS index from disk if it exists, otherwise create it from the policy PDF
    if os.path.exists(INDEX_DIR):
        vectorstore = FAISS.load_local(INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
    else:
        # Load and split the PDF content into documents
        docs = load_policy_pdf(PDF_PATH)

        # Create FAISS vector store from documents
        vectorstore = FAISS.from_documents(docs, embeddings)

        # Save the vector store locally for future reuse
        vectorstore.save_local(INDEX_DIR)

    # Set up a retriever from the vector store for semantic search
    retriever = vectorstore.as_retriever()

    # Initialize LLM from Groq (using LLaMA-3 70B)
    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile",
        temperature=0.2
    )

    # Define a prompt template for contextual QA
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
You are an assistant for answering questions about HR policy documents.
Use the following context to answer the question clearly and simply.

Context:
{context}

Question:
{question}

Answer:
"""
    )

    # Create the RetrievalQA chain using the LLM and retriever
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",  # Simple method for combining context
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=False  # Do not return source docs with answer
    )

    return qa_chain
