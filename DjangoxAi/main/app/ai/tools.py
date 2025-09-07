from ..models import Doc,Staff
from ..serializers import DocSerializer,StaffSerializer
from langchain_core.tools import tool
from rest_framework.response import Response
from django.contrib.auth.models import User
from pydantic import BaseModel
from pdfminer.high_level import extract_text as extract_pdf_text
import os
import docx
import re
from .llms_config import config_llm 

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

@tool
def CV_reader(file_path: str):
    """
    Read the Uploaded Document as a Technical Recruiter
    """
    file_path =file_path
    print("I AM IN TOOLS")
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        raw = extract_pdf_text(file_path)
    elif ext in (".docx", ".doc"):
        doc = docx.Document(file_path)
        raw = "\n".join(p.text for p in doc.paragraphs)
    else:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            raw = f.read()

    raw=re.sub(r'\s+',' ',raw)
    raw = raw.strip()[:3000]
    prompt = (
    "You are a technical recruiter. Below is the **plain text** extracted from a candidate's CV.\n\n"
    "Please review and return your reveiw should be on the basis of candidates degree,education,experience:\n"
    "1. Strengths\n2. Weaknesses\n3. Suggestions\n\n"
    f"{raw}"
    )
    llm=config_llm(None)
    res=llm.invoke(prompt)
    return {"content": res.content}


@tool
def TavilySearchTool(query: str) -> str:
    """
    Perform web search on Tavily to find CV improvement examples.
    """
    return {"content": query}

@tool
def Rag_get_tool():
    """
    Rag Tool
    """
    pass
