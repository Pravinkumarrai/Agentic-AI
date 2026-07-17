from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, START, END
from langchain_ollama import OllamaLLM

# State definition
class State(TypedDict):
    messages: List[Dict[str, str]]

# Load Ollama model
llm = OllamaLLM(model="llama3.1")

# Chatbot node
def chatbot(state: State):
    user_message = state["messages"][-1]["content"]

    response = llm.invoke(user_message)

    state["messages"].append(
        {
            "role": "assistant",
            "content": response
        }
    )

    return {"messages": state["messages"]}


# Build graph
graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()


def main():
    state = {"messages": []}

    print("Chatbot started! Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        state["messages"].append(
            {
                "role": "user",
                "content": user_input
            }
        )

        result = graph.invoke(state)

        assistant_reply = result["messages"][-1]["content"]

        print(f"Bot: {assistant_reply}\n")

        state = result


if __name__ == "__main__":
    main()

    # ollama serve
    # ollama run llama3.1