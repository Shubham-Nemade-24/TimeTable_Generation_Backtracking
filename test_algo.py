import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from app.algorithms.backtracking import BacktrackingTimetableAlgorithm

algo = BacktrackingTimetableAlgorithm()

existing_entries = algo.solve('B.Tech Computer Engineering', 'Semester 5', 'Third Year')
if existing_entries:
    print(f"Success! Generated {len(existing_entries)} entries.")
    labs = sum(1 for e in existing_entries if e.session_type == 'Lab')
    lectures = sum(1 for e in existing_entries if e.session_type != 'Lab')
    print(f"Labs: {labs}, Lectures: {lectures}")
else:
    print("Failed to generate a solution.")

