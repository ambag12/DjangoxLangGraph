from django.db import models
from django.conf import settings

User=settings.AUTH_USER_MODEL

class Doc(models.Model):
    
    owner=models.ForeignKey(User,on_delete=models.CASCADE,to_field="username")
    title=models.CharField(default="Title")
    active_at=models.DateTimeField(auto_now=True)
    updated_at=models.DateTimeField(auto_now=True)
    created_at=models.DateTimeField(auto_now_add=True)
    content = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title}"

class Staff(models.Model):
    staff_user=models.ForeignKey(User,on_delete=models.CASCADE,limit_choices_to={'is_staff': True})
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.owner.username}:{self.staff_user.username}"
    
