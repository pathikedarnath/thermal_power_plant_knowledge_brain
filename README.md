# Thermal Power Plant RAG AI Chatbot

An interactive Retrieval-Augmented Generation (RAG) knowledge base built for thermal power plant operations. This platform ingests technical manuals, safety protocols, and operational guidelines to provide instant, source-grounded answers, targeting the working hours lost to information search in asset-intensive industries.

![App Screenshot](thermal_rag_screenshot.png) 

## Features
* **Source-Grounded AI:** Answers are strictly generated from indexed technical documents to prevent LLM hallucination.
* **Conversational Interface:** A responsive chat UI built with Streamlit featuring conversation memory.
* **Hybrid Processing:** Utilizes local embeddings for secure document processing and a cloud-based LLM for lightning-fast inference.
* **Document Traceability:** Users can expand a "View Source Documents" panel to verify the exact text chunks used to generate the answer.

## Tech Stack
* **Frontend:** Streamlit
* **Orchestration:** LangChain
* **Vector Database:** ChromaDB
* **Embeddings:** Ollama (`nomic-embed-text` running locally)
* **LLM:** Groq API (`openai/gpt-oss-20b` for high-speed generation)

## Prerequisites
* Python 3.10+
* [Ollama](https://ollama.com/) installed and running locally
* A free [Groq API Key](https://console.groq.com/)

## Local Setup & Installation

1. **Clone the repository**
   ```bash
   git clone [https://github.com/yourusername/thermal_power_plant_rag_ai_chatbot.git](https://github.com/yourusername/thermal_power_plant_rag_ai_chatbot.git)
   cd thermal_power_plant_rag_ai_chatbot