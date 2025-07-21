# app.py

import streamlit as st
import boto3
import uuid
import streamlit_authenticator as stauth
from typing import Tuple

# === Auth Setup ===
# NOTE: Replace 'hashed_pw' with an actual hashed password using stauth.Hasher
credentials = {
    'user1@example.com': {
        'name': 'User One',
        'password': '$2b$12$KIX3rZ0UFP8z5T8Ww6oKZeP.k2pGzQ9acpyLyrIm0BOuTq5uUNixC'  # Example hash
    }
}

authenticator = stauth.Authenticate(
    credentials,
    'ocyonbio_cookie',
    'ocyonbio_signature_key',
    cookie_expiry_days=1
)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status is False:
    st.error('❌ Username or password is incorrect')

if authentication_status is None:
    st.warning('🔐 Please enter your credentials')

if authentication_status:
    # === Show Logout Button and Welcome Message
    authenticator.logout('Logout', 'sidebar')
    st.sidebar.success(f"Logged in as: {name}")
    
    # === AWS Bedrock Client Init
    client = boto3.client(
        "bedrock-agent-runtime",
        region_name=st.secrets["AWS_DEFAULT_REGION"],
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"]
    )

    AGENT_ID = st.secrets["AGENT_ID"]
    AGENT_ALIAS_ID = st.secrets["AGENT_ALIAS_ID"]

    # === Streamlit Page Setup
    st.set_page_config(page_title="OcyonBio Smart Search", layout="centered")
    st.title("🔍 OcyonBio Internal Smart Search")
    st.caption("Search SOPs, QA documents, protocols, audits, and internal memos.")

    # === Session State Setup
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "bedrock_session_id" not in st.session_state:
        st.session_state.bedrock_session_id = str(uuid.uuid4())

    # === Helper Function to Split Main Answer + Sources
    def render_response_with_sources(text: str):
        split_token = "#### Sources:"
        if split_token in text:
            answer, sources = text.split(split_token, 1)
            st.markdown(answer.strip())
            st.markdown("---")
            st.markdown(f"#### 📁 Sources:\n{sources.strip()}")
        else:
            st.markdown(text)

    # === Chat Input
    query = st.chat_input("Ask a question about internal documents...")

    if query:
        st.session_state.chat_history.append(("user", query))

        with st.spinner("Retrieving response..."):
            try:
                response_stream = client.invoke_agent(
                    agentId=AGENT_ID,
                    agentAliasId=AGENT_ALIAS_ID,
                    sessionId=st.session_state.bedrock_session_id,
                    inputText=query
                )

                reply_chunks = []
                for event in response_stream["completion"]:
                    if "chunk" in event and "bytes" in event["chunk"]:
                        reply_chunks.append(event["chunk"]["bytes"].decode("utf-8"))

                reply = "".join(reply_chunks) if reply_chunks else "⚠️ No response from agent."
            except Exception as e:
                reply = f"❌ Error: {str(e)}"

            st.session_state.chat_history.append(("agent", reply))

    # === Display Chat History
    for role, message in st.session_state.chat_history:
        if role == "user":
            st.chat_message("user").write(message)
        else:
            st.chat_message("assistant").markdown("📄 **Agent Response:**")
            render_response_with_sources(message)
