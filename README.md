# Chatbot Projects using LangGraph and LangChain

## Overview
This repository contains three chatbot projects built using **LangGraph**, **LangChain**, and **Groq API**. Each project introduces different capabilities such as basic chatbot interactions, tool integration (Wikipedia & Arxiv), and a RAG (Retrieval-Augmented Generation) chatbot.

## Projects

### 1️⃣ Basic Chatbot with LangGraph
This project builds a simple chatbot using **LangGraph** and **LangChain** to process user queries and generate responses with the **Gemma2-9b-It** model.

#### Features
- Basic chatbot functionality
- Uses LangGraph for building conversation flow
- Powered by Groq's LLM

#### Setup
```sh
pip install langgraph langchain langchain_groq
```

#### Usage
Run the script and interact with the chatbot:
```sh
python chatbot.py
```
Type 'quit' or 'q' to exit the chatbot.

---

### 2️⃣ LangGraph Chatbot with Tools
This project enhances the chatbot with Wikipedia and Arxiv tools for fetching real-world data in response to user queries.

#### Features
- Integrates **Wikipedia** and **Arxiv** tools
- Dynamically routes queries to fetch relevant information
- Uses LangGraph for flow management

#### Setup
```sh
pip install langgraph langsmith langchain langchain_groq langchain_community arxiv wikipedia
```

#### Usage
Run the script and provide queries related to research topics or general knowledge:
```sh
python chatbot_with_tools.py
```

---

### 3️⃣ Chatbot with RAG and Tools
This project integrates **Retrieval-Augmented Generation (RAG)** using Cassandra as a vector store. It routes queries between **vector search** and **Wikipedia search** dynamically.

#### Features
- **RAG-based retrieval** using Astra DB (Cassandra)
- **HuggingFace embeddings** for document indexing
- **Automated query routing** between Wikipedia and vector database

#### Setup
```sh
pip install langchain langgraph cassio langchain_community langchain-groq langchain_huggingface chromadb wikipedia
```

Set up Astra DB credentials in the script:
```python
ASTRA_DB_APPLICATION_TOKEN = "your_astra_db_token"
ASTRA_DB_ID = "your_astra_db_id"
```

#### Usage
Run the script and provide a query:
```sh
python chatbot_rag.py
```
The chatbot will retrieve results from Wikipedia or the vector store based on query relevance.

---

## 💡 Future Enhancements
- Improve LLM response quality with **fine-tuning**.
- Support **multi-turn conversations**.
- Add **real-time API endpoints**.

## 📜 License
This project is open-source and available under the MIT License.
