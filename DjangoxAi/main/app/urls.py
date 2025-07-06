
from django.urls import path
from .views import get_views,staff_create_user,check,get_records,call_model,call_agent,get_user_prompt

print("URL Patterns")
urlpatterns = [
    path("doc",get_views,name="document"),
    path("staff_create",staff_create_user),
    path("check",check),
    path('get_records',get_records),
    path('call_model',call_model),
    path('call_agent',call_agent),
    path('get_user_prompt',get_user_prompt),
]