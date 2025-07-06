from django.conf import settings
from langchain_cohere import ChatCohere

def config_llm(request):
    llm = ChatCohere(
    model="command-r",
    api_key=settings.CHAT_COHERE_API_KEY,
    temperature=0.7,
    max_tokens=512
    )
    return llm
