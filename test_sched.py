import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from app.algorithms.backtracking import BacktrackingTimetableAlgorithm
algo = BacktrackingTimetableAlgorithm()
solution = algo.solve('B.Tech Computer Engineering', 'Semester 5', 'Third Year')

from collections import defaultdict
day_counts = defaultdict(list)
for entry in solution['solution']:
    day_counts[entry.day].append(entry.course.Course)

for day, courses in day_counts.items():
    print(f"{day}: {courses}")
    
