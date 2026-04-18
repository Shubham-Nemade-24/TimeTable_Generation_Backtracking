import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from app.views import index
from app.models import TimeTableMain
from django.test import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage

factory = RequestFactory()

for prog in TimeTableMain.objects.all():
    print(f"Generating for {prog.Programme}...")
    request = factory.post('/', {'programme': prog.Programme, 'semester': prog.Semister, 'year_of_study': prog.YearOfStudy})
    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)
    index(request)

print("All databases successfully wiped and regenerated!")
