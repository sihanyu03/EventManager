from tools import tools

import os

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage

from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, MessagesState, END
from langgraph.checkpoint.memory import MemorySaver


def query_or_respond(state: MessagesState):
    """Generate tool call or respond."""
    model_with_tools = model.bind_tools(tools)
    response = model_with_tools.invoke(state['messages'])
    return {'messages': response}


def generate(state: MessagesState):
    """Generate answer."""
    tool_content = state['messages'][-1].content

    system_message_content = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of received information to answer the question"
        "If the retrieved information tells that a task is done, tell this to the user. "
        "If the retrieved tells that an error occurred, tell that to the user as well"
        f"{tool_content}"
    )

    conversation_messages = list(filter(lambda message: message.type == 'human' or (message.type == 'ai' and not message.tool_calls), state['messages']))
    prompt = [SystemMessage(system_message_content)] + conversation_messages
    response = model.invoke(prompt)
    return {'messages': [response]}


def stream_answer(query: str, thread_id: str):
    for message, _ in graph.stream(
        {'messages': [{'role': 'user', 'content': query}]},
        config={'configurable': {'thread_id': thread_id}},
        stream_mode='messages'
    ):
        if isinstance(message, AIMessage):
            print(message.content, end='')
    print()


load_dotenv()
API_KEY = os.getenv('OPENAI_API_KEY')

model = ChatOpenAI(model='gpt-4o-mini', openai_api_key=API_KEY)

graph_builder = StateGraph(MessagesState)
graph_builder.add_node(query_or_respond)
graph_builder.add_node(ToolNode(tools))
graph_builder.add_node(generate)

graph_builder.set_entry_point('query_or_respond')
graph_builder.add_conditional_edges('query_or_respond', tools_condition, {END: END, 'tools': 'tools'})
graph_builder.add_edge('tools', 'generate')
graph_builder.add_edge('generate', END)

checkpointer = MemorySaver()
graph = graph_builder.compile(checkpointer=checkpointer)

thread_id = 'abc123'

while True:
    query = input('You: ')

    if query in ('exit', 'end', 'quit'):
        break

    print('AI: ', end='')
    stream_answer(query, thread_id)
