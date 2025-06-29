from django.contrib.auth.models import Permission
from ..models import Doc,Staff
from ..serializers import DocSerializer,StaffSerializer
from django.contrib.auth.models import User

def permit_one(request,user):
    pq=User.objects.get(username=user,is_staff=True)
    print(f"USER OBJECTS GET ALL the STAFF PERMISSIONS {pq}")

# Regex search with Where
# rights = Permission.objects.filter(
#     codename__iregex=r'VIEW|CHANGE|DELETE|ADD'
# )
# It is a Where in ORM query
    rights=Permission.objects.filter(codename__icontains='CHANGE')
    for r in rights:
        print(f"USER OBJECTS GET ALL the STAFF Rights available {r.codename}")
    pq.user_permissions.add(*rights)



def check(request):
    pq=User.objects.filter(username=user,is_staff=True)
    print(f"USER OBJECTS GET ALL the STAFF PERMISSIONS {pq}")

    rights=Permission.objects.values_list('codename', flat=True)

    print(f"USER OBJECTS GET ALL the STAFF Rights available {rights}")
