from langgraph.prebuilt import create_react_agent
from .llms_config import config_llm
from .tools import l_doc,get_doc

def agent_res(request,checkpointer=None):
    model=config_llm(None)
    myagent=create_react_agent(
        model=model,
        tools=[l_doc,get_doc],
        prompt="You are a helpful assistant",
        checkpointer=checkpointer
    )
    return myagent
