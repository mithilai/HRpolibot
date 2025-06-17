"""
Old code working but app2 is the latest file
"""
import os
import json
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from qa_chain import get_or_create_qa_chain

# ---------- Load Environment ----------
load_dotenv()

# ---------- Streamlit UI Setup ----------
st.set_page_config(page_title="HR Policy Bot", page_icon="📄", layout="centered")

st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
    }
    .stChatMessage.user {
        background-color: #cce5ff !important;
        border-radius: 20px;
        padding: 12px;
        color: #2c2c2c;
        margin-bottom: 8px;
    }
    .stChatMessage.assistant {
        background-color: #e2f0d9 !important;
        border-radius: 20px;
        padding: 12px;
        color: #2c2c2c;
        margin-bottom: 8px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📄 HR Policy Chatbot")

# ---------- Session State Initialization ----------
if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = get_or_create_qa_chain()

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os.makedirs("chat_logs", exist_ok=True)

# ---------- Display Chat History ----------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------- Chat Input ----------
user_input = st.chat_input("Ask something about your HR policies...")

if user_input:
    # User message
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Bot response
    with st.spinner("Thinking..."):
        response = st.session_state.qa_chain.invoke({"query": user_input})
        answer = response["result"]

    with st.chat_message("assistant"):
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})

    # Save conversation to JSON
    with open(f"chat_logs/{st.session_state.session_id}.json", "w", encoding="utf-8") as f:
        json.dump(st.session_state.messages, f, ensure_ascii=False, indent=2)

# # ---------- Custom Styling ----------
# st.markdown("""
#     <style>
#     html, body, [class*="css"] {
#         font-family: 'Segoe UI', sans-serif;
#     }
#     .stChatMessage.user {
#         background-color: #dbeafe !important;
#         border-radius: 20px;
#         padding: 12px;
#         margin-bottom: 10px;
#         color: #1e3a8a;
#         text-align: right;
#         align-self: flex-end;
#     }
#     .stChatMessage.assistant {
#         background-color: #f0fdf4 !important;
#         border-radius: 20px;
#         padding: 12px;
#         margin-bottom: 10px;
#         color: #166534;
#         text-align: left;
#         align-self: flex-start;
#     }

#     .block-container {
#         padding-top: 2rem;
#     }

#     .app-title-container {
#         padding-top: 1.5rem;
#         padding-bottom: 1rem;
#     }

#     .app-title {
#         font-size: 22px;
#         font-weight: 600;
#         margin: 0;
#     }

#     @media (prefers-color-scheme: dark) {
#         .app-title {
#             color: #e1e1e1;
#         }
#     }

#     @media (prefers-color-scheme: light) {
#         .app-title {
#             color: #333333;
#         }
#     }
#     </style>

#     <div class="app-title-container">
#         <h3 class="app-title">PSSPL Polibot</h3>
#     </div>
# """, unsafe_allow_html=True)