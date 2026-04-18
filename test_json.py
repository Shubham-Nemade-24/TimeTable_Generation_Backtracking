import os, django, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from app.algorithms.backtracking import BacktrackingTimetableAlgorithm

algo = BacktrackingTimetableAlgorithm()
solution = algo.solve('B.Tech Computer Engineering', 'Semester 5', 'Third Year')

tree_str = solution["tree"]
print(f"Tree Str Type: {type(tree_str)}")
print(f"Starts with: {tree_str[:50]}")
