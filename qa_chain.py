import os
from langchain_groq import ChatGroq
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import StuffDocumentsChain, LLMChain
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate

from policy_handler import load_policy_pdf

INDEX_DIR = "faiss_index"
PDF_PATH = "data/POLICIES 2.3- Code of Conduct, Work Hour Policy & Leave Policy 2025.pdf"

def get_or_create_qa_chain():
    # Step 1: Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Step 2: Load or create FAISS index
    if os.path.exists(INDEX_DIR):
        vectorstore = FAISS.load_local(INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
    else:
        docs = load_policy_pdf(PDF_PATH)
        vectorstore = FAISS.from_documents(docs, embeddings)
        vectorstore.save_local(INDEX_DIR)

    # Step 3: Setup retriever with higher recall
    retriever = vectorstore.as_retriever(search_kwargs={"k": 6})

    # Step 4: Initialize LLM
    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile",
        temperature=0.1
    )

    # Step 5: Define prompts (cleaned and minimal)
    qa_prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""You are an assistant helping employees understand HR policies at Prakash Software Solutions Pvt. Ltd.

Use the following extracted document content to answer the question.
Be concise, professional, and easy to understand.
If available, mention the policy page number like: "For more information, refer to page X."
If it's not available, do not mention page numbers.

Context:
{context}

Question:
{question}

Answer:"""
    )

    question_prompt = PromptTemplate(
        input_variables=["chat_history", "question"],
        template="""Given the following conversation and a follow-up question, rephrase the follow-up to be a standalone question.

Chat History:
{chat_history}

Follow-Up Input:
{question}

Standalone question:"""
    )

    # Step 6: QA and question generator chains
    qa_llm_chain = LLMChain(llm=llm, prompt=qa_prompt)
    question_generator_chain = LLMChain(llm=llm, prompt=question_prompt)

    # Step 7: Combine context chunks
    stuff_chain = StuffDocumentsChain(
        llm_chain=qa_llm_chain,
        document_variable_name="context"
    )

    # Step 8: Add memory
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="result"
    )

    # Step 9: Final conversational chain
    qa_chain = ConversationalRetrievalChain(
        retriever=retriever,
        combine_docs_chain=stuff_chain,
        question_generator=question_generator_chain,
        memory=memory,
        return_source_documents=True,
        output_key="result"
    )

    return qa_chain
