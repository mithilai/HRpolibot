"""
Main Streamlit app to run PSSPL Polibot with ip address
"""
import os
import json
import requests
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

import firebase_admin
from firebase_admin import credentials, firestore

from qa_chain import get_or_create_qa_chain

# ---------- Load Environment Variables ----------
load_dotenv()

# ---------- Firebase Initialization ----------
if not firebase_admin._apps:
    cred = credentials.Certificate(json.loads(os.getenv("FIREBASE_CREDENTIAL_JSON")))
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ---------- Helper: Get User IP ----------
def get_user_ip():
    try:
        return requests.get("https://api.ipify.org").text
    except:
        return "unknown"

# ---------- Helper: Save Chat to Firebase ----------
def save_chat_to_firestore(user_id, session_id, messages):
    db.collection("chat_logs").document(f"{user_id}_{session_id}").set({
        "user_id": user_id,
        "session_id": session_id,
        "messages": messages,
        "timestamp": firestore.SERVER_TIMESTAMP
    })

# ---------- Streamlit Page Setup ----------
st.set_page_config(page_title="PSSPL Polibot", page_icon="images/logo.png", layout="wide")

# ---------- Custom CSS Styling ----------
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
    }

    div.stChatMessage.user {
        display: flex !important;
        justify-content: flex-end !important;
    }

    div.stChatMessage.assistant {
        display: flex !important;
        justify-content: flex-start !important;
    }

    .stChatMessage.user {
        background-color: #dbeafe !important;
        border-radius: 20px;
        padding: 12px;
        margin-bottom: 10px;
        color: #1e3a8a;
        text-align: right;
        max-width: 75%;
    }

    .stChatMessage.assistant {
        background-color: #f0fdf4 !important;
        border-radius: 20px;
        padding: 12px;
        margin-bottom: 10px;
        color: #166534;
        text-align: left;
        max-width: 75%;
    }

    .block-container {
        padding-top: 2rem;
    }

    .app-title-container {
        padding-top: 1.5rem;
        padding-bottom: 1rem;
    }

    .app-title {
        font-size: 20px;
        font-weight: 600;
        margin: 0;
    }

    @media (prefers-color-scheme: dark) {
        .app-title {
            color: #e1e1e1;
        }
    }

    @media (prefers-color-scheme: light) {
        .app-title {
            color: #333333;
        }
    }
    </style>

    <div class="app-title-container">
        <h3 class="app-title">PSSPL Polibot</h3>
    </div>
""", unsafe_allow_html=True)

# ---------- Session Initialization ----------
if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = get_or_create_qa_chain()

if "user_id" not in st.session_state:
    st.session_state.user_id = get_user_ip()

if "session_id" not in st.session_state:
    st.session_state.session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- Display Previous Messages ----------
for msg in st.session_state.messages:
    avatar = "👨‍💼" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ---------- User Input ----------
user_input = st.chat_input("Ask anything about HR policies...")

if user_input:
    with st.chat_message("user", avatar="👨‍💼"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("Thinking..."):
        response = st.session_state.qa_chain.invoke({"question": user_input})
        answer = response["result"]
        # answer = response["answer"]


    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})

    save_chat_to_firestore(
        st.session_state.user_id,
        st.session_state.session_id,
        st.session_state.messages
    )
