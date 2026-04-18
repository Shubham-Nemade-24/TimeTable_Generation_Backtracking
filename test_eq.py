import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()
from app.models import CourseName
c1 = CourseName.objects.first()
c2 = CourseName.objects.first()
print(f"Direct EQ: {c1 == c2}")
print(f"ID string memory: {id(c1) == id(c2)}")
