from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import DocSerializer,StaffSerializer
from django.contrib.auth.models import User
from .models import Doc,Staff
from .permissions.permit import permit_one
from .ai.tools import l_doc,get_doc,TavilySearchTool
from .ai.llms_config import config_llm
from .ai.agent_conf import agent_res
from langgraph.checkpoint.memory import InMemorySaver
import tempfile, os
from django.conf import settings
import uuid
import time
from langchain_community.tools.file_management.read import ReadFileTool
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langchain.tools import tool
from langchain_community.tools.file_management.read import ReadFileTool
from pydantic import BaseModel
from typing import List, Dict



@api_view(['POST'])
def get_views(request):
    r1=request.data
    username=request.data.get("owner")
    if not r1:
        return Response({"status": "error", "message": "No data provided"}, status=400)

        
    user,created=User.objects.get_or_create(username=username)
    if created:
        return Response({"status": "success", "data": user.username})

    serializer = DocSerializer(data=r1)
    if serializer.is_valid():
        instance=serializer.save(owner=user)
        return Response({"status": "success", "data": serializer.data,"creatred_at":instance.created_at,"owner":instance.owner.username})
    else:
        return Response({"status": "error", "errors": serializer.errors}, status=400)

@api_view(['POST'])
def staff_create_user(request):
    if request.method == 'POST':
        data = request.data
        username = request.data.get('owner')
        if not username:
            return Response({"status": "error", "message": "Username and password are required"}, status=400)
        
        user, created = User.objects.get_or_create(username=username)
        if not created:
            return Response({
                "status": "error",
                "message": "User already exists",
                "username": user.username,
                "role":f"staff {user.is_staff} / admin {user.is_superuser}"
            }, status=200)

        user.is_staff = True
        user.save()

        
        serializer = DocSerializer(data=data)
        if serializer.is_valid():
            instance=serializer.save(owner=user)
            permit_one(None,user)
            return Response({
                "status": "success",
                "message": "User & Doc created successfully",
                "data": serializer.data,
                "created_at":instance.created_at,
                "role":user.is_staff
            }, status=201)
        else:
            user.delete()
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=400)

@api_view(['GET'])
def check(request):
    return Response({"RESPONSE":l_doc.invoke({"request": None})},status=200)

@api_view(['GET'])
def get_records(request):
    primary_obj=request.GET.get('owner')
    if not primary_obj:
        return Response({"Invalid":"Owner not passed in parameters"},status=402)
    return Response({"RESPONSE":get_doc.invoke({"request":None,"param":primary_obj})},status=200)

@api_view(["POST"])
def call_model(request):
    model=config_llm(None)
    return Response({"Response":model.invoke("Who are you?")})

@api_view(['POST'])
def call_agent(request):
    checkpointer=InMemorySaver()
    agent=agent_res(None,checkpointer)
    response=agent.invoke({"messages":[{"role":"user","content":"Get me 3 recent Documents"}]})

    return Response({"Response":response['messages'][-1].content})

class CVReviewState(BaseModel):
    agent_response: str
    search_query: str
    parsed_suggestions: List[str] = []
    tavily_references: Dict = {}
    cv_review_enhanced: Dict = {}

def run_tavily_tool(state: CVReviewState) -> dict:
    query = state.search_query
    result = TavilySearchTool.invoke({"query": query})
    return {"tavily_references": result}

def get_cv_review_agent():
    graph = StateGraph(CVReviewState)

    graph.add_node("ParseAgentResponse", parse_agent_response)
    graph.add_node("TavilySearch", run_tavily_tool)
    graph.add_node("CombineResults", combine_results)

    graph.add_edge("ParseAgentResponse", "CombineResults")
    graph.add_edge("TavilySearch", "CombineResults")

    graph.add_edge("__start__", "ParseAgentResponse")
    graph.add_edge("__start__", "TavilySearch")
    graph.set_finish_point("CombineResults")

    return graph.compile()

def process_agent_review(agent_response:str):
    checkpointer=InMemorySaver()
    try:
        print("I am at Process Agent Review func.\n",agent_response)
        cv_agent = get_cv_review_agent()
        cv_agent = cv_agent.with_config({
            "checkpoint_dir": os.path.join(settings.BASE_DIR, "checkpoints"),
            "checkpoint_interval": 50,
            "thread_id": str(uuid.uuid4()),
        })
        inputs = {
            "agent_response": agent_response,
            "search_query": "CV improvement examples Tavily"
        }

        result = cv_agent.invoke(inputs)

        return result["cv_review_enhanced"]
    finally:
        pass

def parse_agent_response(state: CVReviewState) -> dict:
    agent_response = state.agent_response
    lines = agent_response.splitlines()
    suggestions = [line.strip() for line in lines if line.strip().startswith(('-', '1.', '•'))]
    return {"parsed_suggestions": suggestions}

def combine_results(state: dict) -> dict:
    return {
        "cv_review_enhanced": {
            "suggestions": state.parsed_suggestions,
            "tavily_references": state.tavily_references
        }
    }

@api_view(['POST','GET'])
def get_user_prompt(request):
    if request.method=='POST':
        checkpointer=InMemorySaver()
        payload=request.data
        uploaded = request.FILES["docs"]
        with tempfile.NamedTemporaryFile(suffix=uploaded.name, delete=False) as tmp:
            for chunk in uploaded.chunks():
                tmp.write(chunk)
            file_path = tmp.name
        
        try:
            read_tool = ReadFileTool(root_dir=os.path.dirname(file_path))
            agent=agent_res(None,checkpointer)
            agent = agent.with_config({
                "checkpoint_dir": os.path.join(settings.BASE_DIR, "checkpoints"),
                "checkpoint_interval": 50,
                "thread_id": str(uuid.uuid4()),
            })

            result = agent.invoke({
            "file_path": file_path,
            "messages": [
                {
                    "role": "user",
                    "content": f"I have uploaded a file named '{file_path}'. Please use the `CV_reader` tool to open and analyze it as a CV."
                }
            ]
        })
            next_node= result['messages'][-1].content

            enhanced = process_agent_review(next_node)
            return Response({"review":enhanced})
        finally:
            os.remove(file_path)