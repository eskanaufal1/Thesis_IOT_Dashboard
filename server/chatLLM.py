import os
import requests
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, MessagesState
from dotenv import load_dotenv
from rich import print

# Load environment variables from .env file
load_dotenv()

# Initialize the chatbot model (using Qwen3-235B from Together AI)
model_name = "Qwen/Qwen3-235B-A22B-fp8-tput"  # The specific model you want to use
model = init_chat_model(model_name, model_provider="together")

# Define the workflow with memory
workflow = StateGraph(state_schema=MessagesState)

# Define a simple model calling function
def call_model(state: MessagesState):
    response = model.invoke(state["messages"])  # Call the model
    return {"messages": response}

# Define the workflow with one node - 'model' 
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

# Set up in-memory memory saver to save chat history
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# Define the conversation config (using a thread ID for memory persistence)
config = {"configurable": {"thread_id": "user1"}}  # This can represent different user conversations

def chatbot_conversation():
    print("Hello! I'm your chatbot. Type 'exit' to end the conversation.\n")
    
    # Start conversation loop
    while True:
        user_input = input("You: ")  # Get input from the user
        
        # Exit condition
        if user_input.lower() == 'exit':
            print("Goodbye! Ending the conversation.")
            break
        
        input_messages = [HumanMessage(content=user_input)]
        
        # Get the assistant's full response
        output = app.invoke({"messages": input_messages}, config) # type: ignore

        # Get the AI's response and print it in full
        assistant_response = output["messages"][-1].content
        print(f"Assistant: {assistant_response}")

# Start the interactive chatbot
chatbot_conversation()
