Absolutely! Here’s how you can **integrate Firebase Firestore** into your current Streamlit app to persist chat logs.

---

### ✅ Step 1: Add Firebase Admin SDK

Install it in your environment (locally or via requirements.txt for Streamlit Cloud):

```bash
pip install firebase-admin
```

---

### ✅ Step 2: Add Firebase Credential to `.env`

Add this to your `.env` file:

```env
FIREBASE_CREDENTIAL_JSON=<your-firebase-service-account-json-as-single-line>
```

To get this:

* Go to [Firebase Console](https://console.firebase.google.com/)
* Project > ⚙️ Settings > Service Accounts > Generate New Private Key
* Open the JSON file and convert it to a single-line string or use `json.dumps()` to paste in `.env`.

---

### ✅ Step 3: Firebase Integration Code

Add this at the **top of `app.py`**, **after `load_dotenv()`**:

```python
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase only once
if not firebase_admin._apps:
    firebase_cred_json = os.environ.get("FIREBASE_CREDENTIAL_JSON")
    if not firebase_cred_json:
        raise ValueError("Missing FIREBASE_CREDENTIAL_JSON in .env")

    cred_dict = json.loads(firebase_cred_json)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()
```

---

### ✅ Step 4: Save Chats to Firestore

Define this function (add near top or bottom of `app.py`):

```python
def save_chat_to_firestore(session_id, messages):
    """Store messages in Firebase Firestore under a session document."""
    doc_ref = db.collection("chat_logs").document(session_id)
    doc_ref.set({"messages": messages})
```

---

### ✅ Step 5: Replace Local File Write with Firebase Save

Replace:

```python
# Save chat to local JSON
with open(f"chat_logs/{st.session_state.session_id}.json", "w", encoding="utf-8") as f:
    json.dump(st.session_state.messages, f, ensure_ascii=False, indent=2)
```

With:

```python
# Save chat to Firebase
save_chat_to_firestore(st.session_state.session_id, st.session_state.messages)
```

---

### ✅ Optional: View Logs in Firebase Console

Go to Firestore > `chat_logs` collection and inspect documents.

---

Let me know if you’d like a version that also **retrieves** old chat logs by session ID or **filters by user**, or if you want to use Firebase Authentication.
