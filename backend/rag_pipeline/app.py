import os
import streamlit as st
from dotenv import load_dotenv, find_dotenv
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_groq import ChatGroq
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv(find_dotenv())

# --- Page Configuration ---
st.set_page_config(page_title="Power Plant Knowledge Base", page_icon="🏭")
st.title("🏭 Thermal Power Plant Assistant")
st.markdown("Ask any question about plant operations, safety protocols, or maintenance.")

# --- Initialize RAG Components (Cached for speed) ---
@st.cache_resource
def setup_rag():
    # 1. Connect to local ChromaDB
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vector_store = Chroma(
        collection_name="normal_collection",
        persist_directory="./vector_db",
        embedding_function=embeddings
    )
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    
    # 2. Connect to Groq
    llm = ChatGroq(model_name="openai/gpt-oss-20b")
    
    # 3. Create prompt and chain
    prompt = ChatPromptTemplate.from_template(
        "You are a helpful Thermal Power Plant Assistant. "
        "If the user says a greeting like 'hi' or 'hello', politely say hello back and ask how you can help with the power plant. "
        "For all technical questions, answer briefly and accurately based ONLY on the following context:\n{context}\n\nQuestion: {input}\nAnswer:"
    )
    chain = create_retrieval_chain(retriever, create_stuff_documents_chain(llm, prompt))
    return chain

chain = setup_rag()

# --- Chat Interface Logic ---
# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("E.g., What are the emergency cooldown limits?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response with a loading spinner
    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base..."):
            try:
                # Query the RAG pipeline
                response = chain.invoke({"input": prompt})
                answer = response["answer"]
                st.markdown(answer)
                
                # Optionally, you can add an expander to show the retrieved chunks!
                with st.expander("View Source Documents"):
                    for i, doc in enumerate(response["context"]):
                        st.write(f"**Source {i+1}:**")
                        st.caption(doc.page_content)
                        
            except Exception as e:
                answer = f"⚠️ An error occurred: {str(e)}"
                st.error(answer)
                
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": answer})