from ..models import Doc,Staff
from ..serializers import DocSerializer,StaffSerializer
from langchain_core.tools import tool
from rest_framework.response import Response
from django.contrib.auth.models import User
from pydantic import BaseModel

@tool
def l_doc():
    """
    Get 5 recent Documents of users
    """
    qs=User.objects.filter(is_staff=True).order_by("-date_joined")[:5]
    res_data=[]
    for obj in qs:
        doc_data=Doc.objects.filter(owner=obj.username)
        for doc_data in doc_data:
            res_data.append({
                "title":doc_data.title,
                "name":doc_data.owner.username
            })
    return res_data

@tool
def get_doc(param:str):
    """
    Get a user record from query param
    """
    try:     
        user=User.objects.get(username=param,is_staff=True)
    except User.DoesNotExist:
        raise Exception({"Result":"No data found"})
    doc_data=Doc.objects.get(owner=user.username)
    res=[]
    res.append({
        "title":doc_data.title,
        "name":doc_data.owner.username
    })
    return res
