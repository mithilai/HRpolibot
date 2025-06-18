# PSSPL Assist – HR Policy Bot

PSSPL Assist is an internal HR policy chatbot developed for Prakash Software Solutions Pvt. Ltd. (PSSPL). It allows employees to ask questions about HR policies using natural language and receive accurate answers derived directly from a company-provided PDF document.

## Features

* Automatically loads HR policy PDF from code (no user upload needed)
* Uses LangChain and Groq (LLaMA 3) for natural language understanding
* Supports contextual question-answering
* Stores and reuses FAISS index for faster performance
* Saves chat conversations as timestamped JSON files
* Simple and professional user interface using Streamlit

## Technology Stack

* LangChain for chaining logic and QA system
* Groq (LLaMA 3) for LLM-based responses
* FAISS for document vector indexing and retrieval
* HuggingFace Embeddings for converting text into vectors
* PyMuPDF for extracting text from PDFs
* Streamlit for the chat-based UI

## Project Structure

```
.
├── app.py                  # Main Streamlit application
├── qa_chain.py            # QA chain setup using LangChain and Groq
├── policy_handler.py      # PDF loader and text splitter
├── data/
│   └── hr_policy.pdf      # Pre-loaded HR policy PDF
├── faiss_index/           # Stores vector index to avoid reloading every time
├── chat_logs/             # Stores all chat sessions as JSON
├── requirements.txt
└── README.md
```

## How It Works

1. **Loading PDF**: On first run, the app reads the HR policy PDF from the `data/` directory and splits it into smaller chunks for processing.
2. **Indexing**: These chunks are embedded and stored using FAISS for semantic search.
3. **Caching**: On subsequent runs, if the FAISS index already exists, it is reused to avoid reprocessing the PDF.
4. **Question Answering**: User queries are matched to relevant chunks, passed to the LLaMA 3 model via Groq, and the most relevant answer is returned.
5. **Chat Logging**: All user and assistant messages are saved in a JSON file named using the current date and time.

## How to Run

1. Install the dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Create a `.env` file and add your Groq API key:

   ```
   GROQ_API_KEY=your_groq_api_key_here

   ```

3. Run the application:

   ```
   streamlit run app.py
   ```

## Notes

* Make sure the HR policy document is located in the `data/` folder.
* To reload or update the document, delete the existing `faiss_index/` folder and restart the app.
* Each chat session will be saved under `chat_logs/` automatically.
