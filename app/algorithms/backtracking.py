"""
Algorithm  : Backtracking (Depth-First Search — Constraint Satisfaction Problem)
"""

from typing import List, Optional, Dict, Any
import json
from ..models import Instructor, Venue, CourseName, TimeTable


class TimetableEntry:
    def __init__(self, course, instructor, venue, time_start, time_end, day, session_type):
        self.course       = course
        self.instructor   = instructor
        self.venue        = venue
        self.time_start   = time_start
        self.time_end     = time_end
        self.day          = day
        self.session_type = session_type

    def __repr__(self):
        return (f"TimetableEntry({self.course}, {self.instructor}, "
                f"{self.venue}, {self.day} {self.time_start}-{self.time_end}, "
                f"{self.session_type})")


class BacktrackingTimetableAlgorithm:

    DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    # 1 hour lecture slots (12:00-13:00 is lunch, so excluded)
    LECTURE_SLOTS = [
        ('08:00', '09:00'), ('09:00', '10:00'),
        ('10:00', '11:00'), ('11:00', '12:00'),
        ('13:00', '14:00'), ('14:00', '15:00'),
        ('15:00', '16:00'), ('16:00', '17:00'),
    ]

    # 2-hour contiguous lab slots allocated
    LAB_SLOTS = [
        ('08:00', '10:00'), ('10:00', '12:00'),
        ('13:00', '15:00'), ('15:00', '17:00'),
    ]

    # daily session limits
    MAX_LABS_PER_DAY     = 2
    MAX_LECTURES_PER_DAY = 4

    def is_overlap(self, start1, end1, start2, end2):
        # Returns True if two time intervals overlap (string HH:MM comparison works for 24h format)
        return not (end1 <= start2 or start1 >= end2)

    def is_valid(self, assignment: List[TimetableEntry], new_entry: TimetableEntry) -> bool:
        """
        Constraints:
          1. Same course cannot appear twice on the same day
          2. Instructor cannot teach two classes at overlapping times (same day)
          3. Venue cannot host two classes at overlapping times (same day)
          4. No two classes can overlap in time (same programme = same cohort)
          5. Max 4 lectures per day
          6. Max 2 labs per day
        """
        lectures_count = 0
        labs_count     = 0

        for entry in assignment:
            if entry.day == new_entry.day:
                # Count daily load
                if entry.session_type == 'Lab':
                    labs_count += 1
                else:
                    lectures_count += 1

                # no duplicate subject on same day
                if entry.course == new_entry.course:
                    return False

                # time overlap checks
                if self.is_overlap(entry.time_start, entry.time_end,
                                   new_entry.time_start, new_entry.time_end):
                    if entry.instructor == new_entry.instructor:  # constraint 2
                        return False
                    if entry.venue == new_entry.venue:            # constraint 3
                        return False
                    return False                                  # constraint 4 

        # daily limits
        if new_entry.session_type == 'Lab'  and labs_count     >= self.MAX_LABS_PER_DAY:
            return False
        if new_entry.session_type != 'Lab'  and lectures_count >= self.MAX_LECTURES_PER_DAY:
            return False

        return True

    def solve(self, programme, semester, year_of_study) -> Optional[Dict[str, Any]]:
        # Fetch workload from DB (credits determine number of weekly sessions)
        existing_entries = TimeTable.objects.filter(
            Programme__Programme=programme,
            Programme__Semister=semester,
            Programme__YearOfStudy=year_of_study
        )
        if not existing_entries.exists():
            return None

        course_assignments = [{
            'course'      : e.CourseName,
            'instructor'  : e.Instructor,
            'venue'       : e.Venue,
            'session_type': e.SessionType
        } for e in existing_entries]

        # Schedule Labs first which prevents 2-hour blocks from being fragmented
        course_assignments.sort(key=lambda x: 0 if x['session_type'] == 'Lab' else 1)

        # State-space tree containers (for Vis-Network.js visualization)
        self.tree_nodes    = [{"id": 0, "label": f"Start\n{programme}",
                               "shape": "box", "color": "#17a2b8",
                               "font": {"color": "white"}}]
        self.tree_edges    = []
        self.global_node_id = 0

        assignment = []
        success    = self._backtrack(course_assignments, 0, assignment, 0)
        tree_data  = {"nodes": self.tree_nodes, "edges": self.tree_edges}

        if success:
            print(f"[Backtracking] Solution found: {len(assignment)} sessions, 0 conflicts.")
        else:
            print(f"[Backtracking] Warning: partial solution {len(assignment)}/{len(course_assignments)}")

        return {"solution": assignment, "tree": json.dumps(tree_data)}

    def _backtrack(self, course_assignments, index, assignment, parent_node_id) -> bool:
        """
        Pure recursive DFS backtracking.
        Base case  : index == len(course_assignments), all sessions placed, True
        Recursion  : try each (day, slot), validate, commit, recurse deeper
        Backtrack  : if recursion returns False, assignment.pop(), try next slot
        Complexity : T(n) = O(S^N) worst | O(N·S) practical with pruning
        """
        # Base case — all sessions successfully scheduled
        if index >= len(course_assignments):
            return True

        req          = course_assignments[index]
        slots        = self.LAB_SLOTS if req['session_type'] == 'Lab' else self.LECTURE_SLOTS

        # Add course node to state-space tree
        self.global_node_id += 1
        course_node_id = self.global_node_id
        c_label = str(req['course'].CourseCode) if hasattr(req['course'], 'CourseCode') else str(req['course'])
        self.tree_nodes.append({"id": course_node_id,
                                "label": f"Schedule:\n{c_label} ({req['session_type']})",
                                "color": "#ffc107"})
        self.tree_edges.append({"from": parent_node_id, "to": course_node_id})

        # ── PRODUCTION: smart staggering — fast, rarely backtracks
        # start_day_idx = index % len(self.DAYS)
        # days_to_check = self.DAYS[start_day_idx:] + self.DAYS[:start_day_idx]

        # ── DEMO MODE: uncomment block below (and comment the 2 lines above)
        #              to force visible orange BACKTRACK nodes in the state-space tree
        if req['session_type'] == 'Lab':
            start_day_idx = 0           # all labs race for Monday → triggers backtracks
        else:
            start_day_idx = index % len(self.DAYS)
        days_to_check = self.DAYS[start_day_idx:] + self.DAYS[:start_day_idx]

        for day in days_to_check:
            for time_start, time_end in slots:
                entry = TimetableEntry(
                    course=req['course'], instructor=req['instructor'],
                    venue=req['venue'], time_start=time_start,
                    time_end=time_end, day=day,
                    session_type=req['session_type']
                )

                self.global_node_id += 1
                test_node_id = self.global_node_id

                if self.is_valid(assignment, entry):
                    # CHOOSE
                    assignment.append(entry)
                    self.tree_nodes.append({"id": test_node_id,
                                            "label": f"{day}\n{time_start}-{time_end}",
                                            "color": "#28a745", "font": {"color": "white"}})
                    self.tree_edges.append({"from": course_node_id, "to": test_node_id})

                    # RECURSE
                    if self._backtrack(course_assignments, index + 1, assignment, test_node_id):
                        return True

                    # BACKTRACK - assignment.pop() undoes the choice
                    assignment.pop()
                    self.global_node_id += 1
                    bt_node_id = self.global_node_id
                    self.tree_nodes.append({"id": bt_node_id,
                                            "label": "Backtracked!\nDead end",
                                            "color": "#fd7e14", "font": {"color": "white"}})
                    self.tree_edges.append({"from": test_node_id, "to": bt_node_id})

                else:
                    # Constraint pruning — branch rejected, entire sub-tree is skipped
                    self.tree_nodes.append({"id": test_node_id,
                                            "label": f"Conflict\n{day} {time_start}",
                                            "color": "#dc3545", "font": {"color": "white"}})
                    self.tree_edges.append({"from": course_node_id, "to": test_node_id})

        # All values exhausted for this course, signal parent to backtrack
        return False