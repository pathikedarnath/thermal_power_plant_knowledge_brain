@echo off
echo Starting Ollama in the background...
start "" ollama serve

echo Starting the Streamlit app...
call ..\.venv\Scripts\activate
streamlit run app.py

echo Streamlit closed. Shutting down Ollama...
taskkill /IM ollama.exe /F
taskkill /IM ollama_llama_server.exe /F
echo All processes stopped.
pause