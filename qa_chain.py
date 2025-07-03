import os
from langchain_groq import ChatGroq
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import StuffDocumentsChain, LLMChain
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate

from policy_handler import load_policy_pdf

# Constants for file paths
INDEX_DIR = "faiss_index"
PDF_PATH = "data/POLICIES 2.3- Code of Conduct, Work Hour Policy & Leave Policy 2025.pdf"

def get_or_create_qa_chain():
    """
    Creates or loads a ConversationalRetrievalChain for querying HR policy documents.

    - Loads or builds a FAISS vector store from the provided PDF.
    - Initializes an LLM from Groq (LLaMA-3).
    - Defines custom prompts for answering and question generation.
    - Returns a conversational chain with retrieval and memory.

    Returns:
        ConversationalRetrievalChain: Multi-turn QA chain with vector retrieval.
    """
    # Step 1: Initialize the embeddings model
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Step 2: Load or create FAISS vector index
    if os.path.exists(INDEX_DIR):
        vectorstore = FAISS.load_local(INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
    else:
        docs = load_policy_pdf(PDF_PATH)
        vectorstore = FAISS.from_documents(docs, embeddings)
        vectorstore.save_local(INDEX_DIR)

    retriever = vectorstore.as_retriever()

    # Step 3: Initialize the language model (Groq LLaMA-3)
    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile",
        temperature=0.1
    )

    # Step 4: Prompt for answering HR policy questions
    qa_prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
        You are an assistant helping employees understand HR policies at Prakash Software Solutions Pvt. Ltd.

        Use the following extracted document content to answer the question.
        Be concise, professional, and easy to understand.
        If available, mention the policy page number for reference.
        If the page number is available, mention it like: "For more information, refer to page X."
        If it's not available, do not mention any page number—just answer the question.


        Context:
        {context}

        Question:
        {question}

        Answer:
        """
    )

    # Step 5: Prompt for rephrasing follow-up questions
    question_prompt = PromptTemplate(
        input_variables=["chat_history", "question"],
        template="""
        Given the following conversation and a follow-up question, rephrase the follow-up question to be a standalone question.

        Chat History:
        {chat_history}
        Follow-Up Input:
        {question}

        Standalone question:
        """
    )

    # Step 6: Build chains
    qa_llm_chain = LLMChain(llm=llm, prompt=qa_prompt)
    question_generator_chain = LLMChain(llm=llm, prompt=question_prompt)

    # Step 7: Combine documents into a StuffDocumentsChain
    stuff_chain = StuffDocumentsChain(
        llm_chain=qa_llm_chain,
        document_variable_name="context"
    )

    # Step 8: Add memory to track chat history
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="result"
    )

    # Step 9: Build the final conversational chain
    qa_chain = ConversationalRetrievalChain(
        retriever=retriever,
        combine_docs_chain=stuff_chain,
        question_generator=question_generator_chain,
        memory=memory,
        return_source_documents=True,
        output_key="result"
    )

    return qa_chain
