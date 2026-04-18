import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from app.algorithms.backtracking import BacktrackingTimetableAlgorithm
from app.views import index
from django.test import RequestFactory

factory = RequestFactory()
request = factory.post('/', {'programme': 'B.Tech Computer Engineering', 'semester': 'Semester 5', 'year_of_study': 'Third Year'})
response = index(request)
html = response.content.decode('utf-8')

import re
match = re.search(r'var treeData = (.*?);', html, re.DOTALL)
if match:
    # Print the first 500 characters of the matched JSON
    print("MATCH FOUND:")
    print(match.group(1)[:500])
else:
    print("MATCH NOT FOUND")
