# -*- coding: utf-8 -*-
"""Langgraph Chatbot with Tools.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/18JZxLtAbCBz66hsT59ADzZlZASLehUEO
"""

!pip install langgraph langsmith langchain langchain_groq langchain_community

from typing import Annotated
from typing_extensions import TypedDict

!pip install arxiv wikipedia

###  Working with Tools
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun
from langchain_community.utilities.arxiv import ArxivAPIWrapper
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper


## Arxiv and Wikipedia tools
arxiv_wrapper = ArxivAPIWrapper(top_k_results=1,doc_content_chars_max = 300)
arxiv_tool = ArxivQueryRun(api_wrapper=arxiv_wrapper)

wikipedia_wrapper = WikipediaAPIWrapper(top_k_results=1,doc_content_chars_max = 300)
wikipedia_tool = WikipediaQueryRun(api_wrapper=wikipedia_wrapper)

wikipedia_tool.invoke("Who is karl marx")

arxiv_tool.invoke("Attention is all you need")

tools = [wikipedia_tool, arxiv_tool]

## Langgraph Application
from langgraph.graph.message import add_messages

class State(TypedDict):
  messages:Annotated[list,add_messages]

from langgraph.graph import StateGraph,START,END
graph_builder= StateGraph(State)

from langchain_groq import ChatGroq

from google.colab import userdata
groq_api_key= userdata.get('GROQ_API_KEY')

llm = ChatGroq(groq_api_key=groq_api_key,model_name="Gemma2-9b-It")
llm

llm_with_tools=llm.bind_tools(tools=tools)

def chatbot(state:State):
  return {"messages":[llm_with_tools.invoke(state["messages"])]}

from langgraph.prebuilt import ToolNode, tools_condition

graph_builder.add_node("chatbot",chatbot)
graph_builder.add_edge(START,"chatbot")
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools",tool_node)
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition
)
graph_builder.add_edge("tools","chatbot")
graph_builder.add_edge("chatbot",END)

graph_final= graph_builder.compile()

from IPython.display import display, Image


try:
    display(Image(graph_final.get_graph().draw_mermaid_png()))
except Exception as e:
    print(f"Error displaying graph: {e}")

user_input ="Attention is all you need"
events=graph_final.stream(
    {
        "messages":[("user",user_input)]},stream_mode="values"

)
for event in events:
  event["messages"][-1].pretty_print()

