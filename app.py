import streamlit as st
import anthropic
import chromadb
import os

# ── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🤖",
    layout="wide"
)

# ── Load vector DB (cached — runs only once) ──────────────
@st.cache_resource
def load_db():
    client = chromadb.Client()
    db = client.create_collection("knowledge_base")

    # Sample documents — replace these with your own content!
    sample_docs = [
        "Employees are entitled to 20 days of annual leave per year. Leave must be approved by your manager at least 2 weeks in advance.",
        "Sick leave is separate from annual leave. A medical certificate is required for absences longer than 3 consecutive days.",
        "Work from home is allowed up to 3 days per week. You must be available on Slack and attend all scheduled meetings.",
        "Parental leave is 12 weeks for primary caregivers and 4 weeks for secondary caregivers. It is fully paid.",
        "The performance review cycle runs twice a year — in June and December. Goals are set at the start of each half-year.",
        "New employees have a 3-month probation period. During this time, either party can terminate with 1 week notice.",
        "The company provides a $500 annual learning budget for courses, books, and conferences. Submit receipts to HR.",
        "Office hours are 9am to 6pm Monday to Friday. Flexible start times between 8am and 10am are allowed.",
    ]

    ids = [f"doc{i}" for i in range(len(sample_docs))]
    db.add(documents=sample_docs, ids=ids)
    return db


# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Settings")

    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        placeholder="sk-ant-...",
        help="Get your key from console.anthropic.com"
    )

    n_chunks = st.slider("Chunks to retrieve", min_value=1, max_value=5, value=2,
                         help="How many document chunks to send to Claude")

    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.3, step=0.1,
                            help="Higher = more creative, Lower = more factual")

    st.divider()
    st.markdown("### 📚 Knowledge Base")
    st.info("8 HR policy documents loaded.\nReplace `sample_docs` in the code with your own content.")

    if st.button("🗑️ Clear chat history"):
        st.session_state.messages = []
        st.rerun()


# ── Main UI ───────────────────────────────────────────────
st.title("🤖 RAG Chatbot")
st.caption("Ask questions — answers come from your knowledge base, not just AI memory.")

# Metric row
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Documents indexed", "8")
with col2:
    msg_count = len([m for m in st.session_state.get("messages", []) if m["role"] == "user"])
    st.metric("Questions asked", msg_count)
with col3:
    st.metric("Chunks per query", n_chunks)

st.divider()

# ── Chat history ──────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show all past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        # Show retrieved context for assistant messages
        if msg["role"] == "assistant" and "context" in msg:
            with st.expander("📄 Retrieved context"):
                for i, chunk in enumerate(msg["context"], 1):
                    st.markdown(f"**Chunk {i}:** {chunk}")


# ── Chat input ────────────────────────────────────────────
if question := st.chat_input("Ask something about the HR policies..."):

    # Validate API key
    if not api_key:
        st.error("Please enter your Anthropic API key in the sidebar.")
        st.stop()

    # Show user message
    with st.chat_message("user"):
        st.write(question)
    st.session_state.messages.append({"role": "user", "content": question})

    # RAG: Retrieve relevant chunks
    db = load_db()
    results = db.query(query_texts=[question], n_results=n_chunks)
    retrieved_chunks = results["documents"][0]

    # Build the prompt
    context = "\n\n".join([f"[Doc {i+1}]: {c}" for i, c in enumerate(retrieved_chunks)])
    prompt = f"""You are a helpful HR assistant. Answer the question using ONLY the context below.
If the answer is not in the context, say "I don't have that information in my knowledge base."
Be concise and friendly.

Context:
{context}

Question: {question}"""

    # Call Claude
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                ai = anthropic.Anthropic(api_key=api_key)
                response = ai.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=500,
                    temperature=temperature,
                    messages=[{"role": "user", "content": prompt}]
                )
                answer = response.content[0].text
                st.write(answer)

                # Show what was retrieved
                with st.expander("📄 Retrieved context"):
                    for i, chunk in enumerate(retrieved_chunks, 1):
                        st.markdown(f"**Chunk {i}:** {chunk}")

                # Save to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "context": retrieved_chunks
                })

            except anthropic.AuthenticationError:
                st.error("Invalid API key. Please check your Anthropic API key in the sidebar.")
            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")
