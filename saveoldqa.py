import os
from langchain_groq import ChatGroq
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from policy_handler import load_policy_pdf

# Constants for file paths
INDEX_DIR = "faiss_index"  # Directory where FAISS index is stored/loaded
PDF_PATH = "data/POLICIES 2.3- Code of Conduct, Work Hour Policy & Leave Policy 2025.pdf"

def get_or_create_qa_chain():
    """
    Creates or loads a RetrievalQA chain for querying HR policy documents.

    - If the FAISS vector index is already present, it will be loaded.
    - Otherwise, the policy PDF will be read, embedded, and indexed.
    - A RetrievalQA chain is returned that can answer questions using Groq LLaMA-3 model.

    Returns:
        RetrievalQA: A ready-to-use question-answering chain.
    """
    # Initialize HuggingFace embedding model (MiniLM)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Check if FAISS index exists; load if yes, create if not
    if os.path.exists(INDEX_DIR):
        # Load the FAISS vector store from disk (allowing deserialization)
        vectorstore = FAISS.load_local(INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
    else:
        # Load and split policy PDF into documents
        docs = load_policy_pdf(PDF_PATH)

        # Create FAISS vector store from the loaded documents
        vectorstore = FAISS.from_documents(docs, embeddings)

        # Save vector index locally to reuse later
        vectorstore.save_local(INDEX_DIR)

    # Set up retriever for searching relevant document chunks
    retriever = vectorstore.as_retriever()

    # Initialize LLM from Groq (LLaMA-3 70B model)
    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile",
        temperature=0.1
    )

    # Define the prompt used to instruct the LLM
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
You are an assistant helping employees understand HR policies at Prakash Software Solutions Pvt. Ltd.

Use the following extracted document content to answer the question.
Be concise, professional, and easy to understand.
If available, mention the policy page number for reference.
and when there is page number to share you can state as for more information refer to page no.
if not able to find the reference page not talk about it just answer to user query.

Context:
{context}

Question:
{question}

Answer:
"""
    )

    # Construct a RetrievalQA chain using the retriever and LLM
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",  # Simply concatenate context chunks
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True  # Set to True if you want raw source docs
    )

    return qa_chain