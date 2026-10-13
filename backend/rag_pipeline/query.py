import os
from dotenv import load_dotenv, find_dotenv
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_groq import ChatGroq
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

load_dotenv(find_dotenv())

# 1. Ollama Embeddings + Point to your populated collection
embeddings = OllamaEmbeddings(model="nomic-embed-text")
vector_store = Chroma(
    collection_name="normal_collection",
    persist_directory="./vector_db",
    embedding_function=embeddings
)

# 2. Check chunk count in this collection
collection = vector_store._collection
print(f"Total chunks in 'normal_collection': {collection.count()}")

# 3. Setup Retriever & Inspect matches
question = "To what exact temperature does the maintenance cooling loop lower the HTS?"
retriever = vector_store.as_retriever(search_kwargs={"k": 3})
retrieved_docs = retriever.invoke(question)

print(f"\n--- RETRIEVED CHUNKS ({len(retrieved_docs)}) ---")
for i, doc in enumerate(retrieved_docs):
    print(f"\n[Chunk {i+1}]:")
    print(doc.page_content[:300] + ("..." if len(doc.page_content) > 300 else ""))

# 4. Groq LLM Generation
llm = ChatGroq(model_name="openai/gpt-oss-20b")
prompt = ChatPromptTemplate.from_template(
    "Answer based ONLY on this context and keep the answer concise to max 3 lines:\n{context}\n\nQuestion: {input}\nAnswer:"
)
chain = create_retrieval_chain(retriever, create_stuff_documents_chain(llm, prompt))

response = chain.invoke({"input": question})

print("\n--- FINAL ANSWER ---")
print(response["answer"])