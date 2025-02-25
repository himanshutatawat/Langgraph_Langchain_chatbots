# -*- coding: utf-8 -*-
"""Chatbot with RAG and tools.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1W6Q9HxMdStG0_yhrLCkCsvCkaelWoT14
"""

!pip install langchain langgraph cassio

import cassio

ASTRA_DB_APPLICATION_TOKEN="your_astra_db_application_token"
ASTRA_DB_ID="your_astra_db_id"
cassio.init(token=ASTRA_DB_APPLICATION_TOKEN,database_id=ASTRA_DB_ID)

!pip install langchain_community langchain-groq langchain tiktoken langchainhub chromadb langchain langgraph langchain_huggingface

## Build Index
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Cassandra
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import WebBaseLoader

urls = [
    "https://lilianweng.github.io/posts/2023-06-23-agent/",
    "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",
    "https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/"

]

## Load
docs = [WebBaseLoader(url).load() for url in urls]
doc_list = [item for sublist in docs for item in sublist]
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=500, chunk_overlap=0)
docs_splits = text_splitter.split_documents(doc_list)

docs_splits

from langchain_huggingface import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name = "all-MiniLM-L6-v2")

from langchain.vectorstores.cassandra import Cassandra
astra_vector_store= Cassandra(embedding=embeddings,
                              table_name="qa_mini_demo",
                              session=None,
                              keyspace=None)

from langchain.indexes.vectorstore import VectorStoreIndexWrapper
astra_vector_store.add_documents(docs_splits)
print("Inserted %i headlines." % len(docs_splits))
astra_vector_index= VectorStoreIndexWrapper(vectorstore=astra_vector_store)

retriever = astra_vector_store.as_retriever()
retriever.invoke("What is agent")

from typing import Literal
from langchain_core.prompts import ChatPromptTemplate

from langchain_core.pydantic_v1 import BaseModel, Field

class RouteQuery(BaseModel):
  """Route a user query to the mose relevant datasource."""
  datasource:Literal["vectorstore","wiki_search"]=Field(
      ...,
      description="Given a user question choose to route it to wikipedia or a vectorstore",


  )



from langchain_groq import ChatGroq
from google.colab import userdata
import os
groq_api_key = userdata.get('GROQ_API_KEY')

llm = ChatGroq(groq_api_key=groq_api_key,model_name= "llama-3.3-70b-Versatile")
llm

unstructured_llm_router = llm.with_structured_output(RouteQuery)

## Prompt
system = """ You are an expert at routing a user question to a vectorstore or wikipidea.
The vectorstore contains documents related to agents, prompt engineering and adversial attacks
Use the vectorstore for question on these topics otherwise use wiki-search
"""

route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{question}"),
    ]
)

question_router= route_prompt | unstructured_llm_router

print(question_router.invoke({"question":"What is agent"}))

print(question_router.invoke({"question":"who is shahrukh khan??"}))

!pip install langchain_community wikipedia

from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import WikipediaQueryRun
api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=500)
wiki= WikipediaQueryRun(api_wrapper=api_wrapper)

wiki("Tell me about shahrukh khan")

## AI agents application using Langgraph
from typing import List
from typing_extensions import TypedDict

class GraphState(TypedDict):
  """
  Represents the state of our graph
  Attributes:
    question:question
    generation:LLM generation
    documents:list of documents

  """
  question:str
  generation:str
  documents:List[str]

from langchain.schema import document

def retrieve(state):
  """
  Retrive documents
  Args:
    state(dict): The current graph state

  Return:
    state(dict): New key added to the state, documents, that contains retrived documents
    """
  print("--!!--Retrieved--!!--")
  questions = state["question"]
  retrieved_docs = retriever.invoke(questions)
  return {"documents":retrieved_docs, "question":questions}
#

from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import WikipediaQueryRun
from langchain.schema import Document

# Initialize Wikipedia API Wrapper
api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=500)
wiki = WikipediaQueryRun(api_wrapper=api_wrapper)

def wiki_search(state):
    """
    wiki search based on the re-phrased question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with appended web results
    """

    print("---wikipedia---")
    print("---HELLO--")
    question = state["question"]
    print(question)

    # Wiki search
    docs = wiki.invoke({"query": question})
    #print(docs["summary"])
    wiki_results = docs
    wiki_results = Document(page_content=wiki_results)

    return {"documents": wiki_results, "question": question}

### Edges ###
def route_question(state):
  """Route the question to wiki search or RAG.
  Args:
    state(dict): The current graph state
  Returns:
    str: Next node to call
  """
  print("---ROUTE Question---")
  question = state["question"]
  source = question_router.invoke({"question":question})
  if source.datasource == "wiki_search":
    print("---Route Question to Wiki Search---")
    return "wiki_search"
  elif source.datasource == "vectorstore":
    print("---Route Question to RAG---")
    return "vectorstore"
  else:
    raise ValueError(f"Unknown datasource {source.datasource}")

from langgraph.graph import START,END, StateGraph, StateGraph
workflow = StateGraph(GraphState)

workflow.add_node("wiki_search", wiki_search)
workflow.add_node("retrieve", retrieve)
workflow.add_conditional_edges(
    START,
    route_question,
        {"wiki_search": "wiki_search",
        "vectorstore":"retrieve"},

)
workflow.add_edge("retrieve",END)
workflow.add_edge("wiki_search",END)
app = workflow.compile()

from IPython.display import display, Image


try:
    display(Image(app.get_graph().draw_mermaid_png()))
except Exception as e:
    print(f"Error displaying graph: {e}")

# prompt: now write a code to print about some query which is given byuser byusing the above chatbot

# Assuming 'foo' is the variable holding the user's query from the input text field.
# If not, replace 'foo' with the actual variable name.

question = "what is agent" #@param {type:"string"}

# Execute the LangGraph application with the user's query
result = app.invoke({"question": question})

# Print the relevant results from the application output
if "documents" in result:
  print("Retrieved documents:\n", result["documents"])
elif "wiki_results" in result:
  print("Wikipedia results:\n", result["wiki_results"])
else:
  print("No relevant results found for the given query.")

# prompt: now write a code to print about some query which is given byuser byusing the above chatbot

# Assuming 'foo' is the variable holding the user's query from the input text field.
# If not, replace 'foo' with the actual variable name.

question = "avengers" #@param {type:"string"}

# Execute the LangGraph application with the user's query
result = app.invoke({"question": question})

# Print the relevant results from the application output
if "documents" in result:
  print("Retrieved documents:\n", result["documents"])
elif "wiki_results" in result:
  print("Wikipedia results:\n", result["wiki_results"])
else:
  print("No relevant results found for the given query.")

def chatbot_finall():
    """
    A chatbot that continuously asks for user queries, searches Wikipedia,
    and prints the retrieved information. The chatbot stops when the user enters 'Q' or 'QUIT'.
    """
    print("Welcome to the Wikipedia Search Chatbot!")
    print("Type 'Q' or 'QUIT' to exit.")

    while True:
        # Ask user for a query
        question = input("\nEnter a topic to search on Wikipedia: ").strip()

        # Exit condition
        if question.upper() in ["Q", "QUIT"]:
            print("Exiting chatbot. Have a great day!")
            break

        # Execute Wikipedia search
        result = app.invoke({"question": question})

        # Print Wikipedia results
        if "documents" in result:
            print("\nRetrieved RAG Result:\n")
            print(result["documents"])  # Wikipedia summary
        elif "wiki_results" in result:
            print("\nWikipedia results:\n", result["wiki_results"])
        else:
            print("\nNo relevant Wikipedia results found.")

# Run the chatbot
chatbot_finall()

result

