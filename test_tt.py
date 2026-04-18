import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from app.algorithms.backtracking import BacktrackingTimetableAlgorithm
from app.models import TimeTable

algo = BacktrackingTimetableAlgorithm()
solution = algo.solve('B.Tech Computer Engineering', 'Semester 5', 'Third Year')

for entry in solution['solution']:
    print(f"{entry.day} {entry.time_start}-{entry.time_end} : {entry.course.CourseCode} ({entry.course.Course})")
