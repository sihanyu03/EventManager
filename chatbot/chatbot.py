from tools import tools

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage

from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, MessagesState, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command


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


load_dotenv()

model = ChatOpenAI(model='gpt-4o-mini')

builder = StateGraph(MessagesState)
builder.add_node(query_or_respond)
builder.add_node(ToolNode(tools))
builder.add_node(generate)

builder.set_entry_point('query_or_respond')
builder.add_conditional_edges('query_or_respond', tools_condition, {END: END, 'tools': 'tools'})
builder.add_edge('tools', 'generate')
builder.add_edge('generate', END)

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

config = {'configurable': {'thread_id': '1'}}

while True:
    snapshot = graph.get_state(config)

    if snapshot.tasks and snapshot.tasks[0].interrupts:
        print(f'AI: {snapshot.tasks[0].interrupts[0].value}')
        confirmation = input('You: ')
        inp = Command(resume=confirmation)
    else:
        query = input('You: ')
        if query in ('exit', 'end', 'quit'):
            break
        inp = {'messages': [HumanMessage(content=query)]}

    first = True
    for message, _ in graph.stream(
            inp,
            config=config,
            stream_mode='messages'
    ):
        if isinstance(message, AIMessage) and message.content:
            if first:
                first = False
                print('AI: ', end='')
            print(message.content, end='')

    if not first:
        print()