import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from app.views import index
from django.test import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage

factory = RequestFactory()
request = factory.post('/', {'programme': 'B.Tech Computer Engineering', 'semester': 'Semester 5', 'year_of_study': 'Third Year'})

setattr(request, 'session', 'session')
messages = FallbackStorage(request)
setattr(request, '_messages', messages)

index(request)
