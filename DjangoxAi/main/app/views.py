from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import DocSerializer,StaffSerializer
from django.contrib.auth.models import User
from .models import Doc,Staff
from .permissions.permit import permit_one
from .ai.tools import l_doc,get_doc
from .ai.llms_config import config_llm
from .ai.agent_conf import agent_res
from langgraph.checkpoint.memory import InMemorySaver
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