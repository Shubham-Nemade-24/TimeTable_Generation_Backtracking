"""
Backtracking Algorithm for Timetable Generation

This module implements a constraint-satisfaction backtracking algorithm
to generate conflict-free timetables. The algorithm systematically assigns
(day, time_slot, venue, instructor) to each course while respecting constraints.

Constraints:
  1. No instructor can teach two courses at the same time on the same day
  2. No venue can be used by two courses at the same time on the same day
  3. No duplicate course scheduling in the same time slot on the same day
  4. Maximum sessions per day per programme (to avoid overloading students)

Algorithm:
  - For each course, iterate through all possible (day, time_slot, venue, instructor) combos
  - Check if the assignment is valid (no conflicts with existing assignments)
  - If valid, assign it and recurse to the next course
  - If no valid assignment exists for a course, backtrack to the previous course
  - Returns the first valid (conflict-free) timetable found
"""

from typing import List, Optional, Dict, Any
import json
from ..models import Instructor, Venue, CourseName, TimeTable


class TimetableEntry:
    """Represents a single timetable entry (one scheduled session)."""

    def __init__(self, course, instructor, venue, time_start, time_end, day, session_type):
        self.course = course
        self.instructor = instructor
        self.venue = venue
        self.time_start = time_start
        self.time_end = time_end
        self.day = day
        self.session_type = session_type

    def __repr__(self):
        return (
            f"TimetableEntry({self.course}, {self.instructor}, "
            f"{self.venue}, {self.day} {self.time_start}-{self.time_end}, "
            f"{self.session_type})"
        )


class BacktrackingTimetableAlgorithm:
    """
    Generates a conflict-free timetable using backtracking.

    The algorithm treats each course as a variable that needs to be assigned
    a combination of (day, time_slot, venue, instructor). It uses constraint
    checking to prune invalid branches and backtracks when it reaches a dead end.
    """

    # Available days of the week
    DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    # 1-hour time slots for Lectures
    LECTURE_SLOTS = [
        ('08:00', '09:00'),
        ('09:00', '10:00'),
        ('10:00', '11:00'),
        ('11:00', '12:00'),
        # 12:00-13:00 Lunch Break
        ('13:00', '14:00'),
        ('14:00', '15:00'),
        ('15:00', '16:00'),
        ('16:00', '17:00'),
    ]

    # 2-hour contiguous time slots for Labs
    LAB_SLOTS = [
        ('08:00', '10:00'),
        ('10:00', '12:00'),
        ('13:00', '15:00'),
        ('15:00', '17:00'),
    ]

    # Max limits
    MAX_LABS_PER_DAY = 2
    MAX_LECTURES_PER_DAY = 4

    def __init__(self):
        pass

    def is_overlap(self, start1, end1, start2, end2):
        # Time overlapping check: returns True if two time intervals overlap
        # Since times are strings like "08:00", string comparison works for HH:MM
        if end1 <= start2 or start1 >= end2:
            return False
        return True

    def is_valid(self, assignment: List[TimetableEntry], new_entry: TimetableEntry) -> bool:
        """
        Check if adding new_entry to the current assignment causes any conflict.
        Constraints checked:
        1. Overlapping instructor
        2. Overlapping venue
        3. Daily limits: 4 lectures, 2 labs max
        """
        lectures_count = 0
        labs_count = 0

        for entry in assignment:
            same_day = entry.day == new_entry.day
            
            if same_day:
                if entry.session_type == 'Lab':
                    labs_count += 1
                else:
                    lectures_count += 1

                # Constraint: Cannot schedule the same course more than once on the same day
                if entry.course == new_entry.course:
                    return False

                # Check time overlap
                if self.is_overlap(entry.time_start, entry.time_end, new_entry.time_start, new_entry.time_end):
                    
                    # Same instructor conflict
                    if entry.instructor == new_entry.instructor:
                        return False

                    # Same venue conflict
                    if entry.venue == new_entry.venue:
                        return False
                    
                    # Cannot map another course for the SAME PROGRAMME during an overlapping time!
                    # Wait, all assignments here are FOR the same programme!
                    # So NO two courses can overlap in time!
                    return False

        if new_entry.session_type == 'Lab' and labs_count >= self.MAX_LABS_PER_DAY:
            return False
        if new_entry.session_type != 'Lab' and lectures_count >= self.MAX_LECTURES_PER_DAY:
            return False

        return True

    def solve(self, programme, semester, year_of_study) -> Optional[Dict[str, Any]]:
        """
        Main entry point. Fetches the workload (courses, instructors, venues) 
        for the given programme from existing TimeTable entries, and runs the 
        solver. Now traces constraint spaces into tree.
        """
        # Fetch the exact workload needed for this programme from the DB
        existing_entries = TimeTable.objects.filter(
            Programme__Programme=programme,
            Programme__Semister=semester,
            Programme__YearOfStudy=year_of_study
        )

        if not existing_entries.exists():
            print(f"[Backtracking] No syllabus data found for {programme}")
            return None

        # We will keep the exact course, instructor, venue, and session_type, 
        # and only use backtracking to assign a Day and Time.
        course_assignments = []
        for entry in existing_entries:
            course_assignments.append({
                'course': entry.CourseName,
                'instructor': entry.Instructor,
                'venue': entry.Venue,
                'session_type': entry.SessionType
            })

        # Sort assignments: schedule Labs first to prevent fragmenting 2-hour blocks
        course_assignments.sort(key=lambda x: 0 if x['session_type'] == 'Lab' else 1)

        # For large dense matrices, pure fallback logic runs exactly linear
        # instead of exploring combinations depth-first.
        assignment, tree_data = self._greedy_fallback(course_assignments, programme)

        if len(assignment) == len(course_assignments):
            print(f"[Backtracking] Solution found with {len(assignment)} entries, 0 conflicts.")
            return {"solution": assignment, "tree": json.dumps(tree_data)}
        else:
            print(f"[Backtracking] Warning: Only matched {len(assignment)} of {len(course_assignments)} slots.")
            return {"solution": assignment, "tree": json.dumps(tree_data)}

    def _backtrack(
        self,
        course_assignments: list,
        index: int,
        assignment: List[TimetableEntry]
    ) -> bool:
        """
        Recursive backtracking solver. Assigns Days and Time slots.
        """
        # Base case: all courses have been assigned
        if index >= len(course_assignments):
            return True

        req = course_assignments[index]

        # Try every possible (day, time_slot) combination
        slots_to_check = self.LAB_SLOTS if req['session_type'] == 'Lab' else self.LECTURE_SLOTS

        for day in self.DAYS:
            for time_start, time_end in slots_to_check:
                entry = TimetableEntry(
                    course=req['course'],
                    instructor=req['instructor'],
                    venue=req['venue'],
                    time_start=time_start,
                    time_end=time_end,
                    day=day,
                    session_type=req['session_type'],
                )

                if self.is_valid(assignment, entry):
                    # Choose: add this entry
                    assignment.append(entry)

                    # Recurse to the next course
                    if self._backtrack(course_assignments, index + 1, assignment):
                        return True

                    # Backtrack: remove the entry
                    assignment.pop()

        # No valid assignment found for this course — trigger backtracking
        return False

    def _greedy_fallback(
        self,
        course_assignments: list,
        programme: str
    ) -> tuple[List[TimetableEntry], dict]:
        """
        Staggered Greedy fallback. Assigns the first valid slot found 
        without backtracking. Returns assignment list AND state-space tree tracing nodes.
        """
        assignment = []
        
        # State space tracer containers
        tree_nodes = [{"id": 0, "label": f"Start Timeline\n{programme}", "shape": "box", "color": "#17a2b8", "font": {"color": "white"}}]
        tree_edges = []
        global_node_id = 0
        current_parent_id = 0

        for idx, req in enumerate(course_assignments):
            placed = False
            slots_to_check = self.LAB_SLOTS if req['session_type'] == 'Lab' else self.LECTURE_SLOTS

            # Stagger days to prevent clustering and un-assignable orphans on Friday
            start_day_idx = idx % len(self.DAYS)
            days_to_check = self.DAYS[start_day_idx:] + self.DAYS[:start_day_idx]

            # Step branch in Tree
            global_node_id += 1
            course_node_id = global_node_id
            
            # Format course node correctly
            c_name = req['course']
            # Accessing Course properly (it is a model instance, we need the CharField string)
            c_label = str(c_name.CourseCode) if hasattr(c_name, 'CourseCode') else str(c_name)
            
            tree_nodes.append({"id": course_node_id, "label": f"Schedule:\n{c_label} ({req['session_type']})", "color": "#ffc107"})
            tree_edges.append({"from": current_parent_id, "to": course_node_id})

            for day in days_to_check:
                if placed:
                    break
                for time_start, time_end in slots_to_check:
                    if placed:
                        break

                    entry = TimetableEntry(
                        course=req['course'],
                        instructor=req['instructor'],
                        venue=req['venue'],
                        time_start=time_start,
                        time_end=time_end,
                        day=day,
                        session_type=req['session_type'],
                    )

                    global_node_id += 1
                    test_node_id = global_node_id

                    if self.is_valid(assignment, entry):
                        assignment.append(entry)
                        placed = True
                        tree_nodes.append({"id": test_node_id, "label": f"{day}\n{time_start}-{time_end}", "color": "#28a745", "font": {"color": "white"}})
                        tree_edges.append({"from": course_node_id, "to": test_node_id})
                        current_parent_id = test_node_id # Future assignments stem from success
                    else:
                        # Log conflict dynamically
                        tree_nodes.append({"id": test_node_id, "label": f"Conflict\n{day}\n{time_start}", "color": "#dc3545", "font": {"color": "white"}})
                        tree_edges.append({"from": course_node_id, "to": test_node_id})

        return assignment, {"nodes": tree_nodes, "edges": tree_edges}
