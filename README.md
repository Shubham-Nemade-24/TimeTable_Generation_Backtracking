# TimeTable MIS — Timetable Management Information System

A Django-based web application for generating and managing academic timetables using a **Backtracking Algorithm**. The system automatically creates conflict-free schedules by assigning courses to time slots, venues, and instructors while respecting multiple constraints.

---

## Features

- **Automated Timetable Generation** using Backtracking Algorithm (constraint-satisfaction)
- **User Authentication** — Login, Signup, Logout
- **Dashboard** with statistics overview (courses, instructors, venues, timetables)
- **View Timetables** — Browse all scheduled timetable entries grouped by day
- **View Courses** — Browse all available courses with codes and descriptions
- **View Instructors** — Browse all registered instructors with department info
- **Email Timetable** — Send timetable to students/staff via email
- **Admin Panel** — Full CRUD operations via Django Admin (Jazzmin themed)
- **Role-based Access** — Regular users can view data; staff/admin can manage data

---

## Tech Stack

| Component       | Technology            |
|:----------------|:----------------------|
| Backend         | Django 4.2 (Python)   |
| Database        | SQLite3               |
| Frontend        | Bootstrap 5, AdminLTE |
| Admin Theme     | Django Jazzmin        |
| Forms           | Django Crispy Forms   |
| Algorithm       | Backtracking (CSP)    |

---

## Backtracking Algorithm — How It Works

The timetable generation uses a **Constraint Satisfaction Problem (CSP)** approach solved via backtracking:

### Algorithm Steps:
1. **Input**: List of courses, available instructors, venues, time slots, and days
2. **For each course**, try all possible combinations of `(day, time_slot, venue, instructor)`
3. **Validate constraints** before assigning:
   - **No instructor clash**: Same instructor cannot teach two courses at the same time
   - **No venue clash**: Same venue cannot be used by two courses at the same time
   - **No duplicate scheduling**: Same course cannot be in the same slot twice
   - **Daily limit**: Maximum 5 sessions per day per programme
4. **If valid**, assign and move to the next course (recurse)
5. **If no valid assignment exists**, **backtrack** to the previous course and try the next option
6. **Output**: A complete, conflict-free timetable

### Pseudocode:
```
function backtrack(courses, index, assignment):
    if index >= len(courses):
        return True  // All courses assigned — solution found!
    
    for each day in [Mon, Tue, Wed, Thu, Fri]:
        for each time_slot in available_slots:
            for each venue in venues:
                for each instructor in instructors:
                    if is_valid(assignment, new_entry):
                        assignment.add(new_entry)
                        if backtrack(courses, index+1, assignment):
                            return True
                        assignment.remove(new_entry)  // Backtrack
    
    return False  // No valid assignment — trigger backtracking
```

### Time Complexity:
- **Worst case**: O(D × T × V × I)^C where D=days, T=time slots, V=venues, I=instructors, C=courses
- **In practice**: Constraint pruning significantly reduces the search space

---

## Project Structure

```
TT_project/
├── manage.py                   # Django management script
├── db.sqlite3                  # SQLite database
├── README.md                   # This file
├── SETUP_COMMANDS.txt          # Setup and run commands
│
├── project/                    # Django project configuration
│   ├── settings.py             # Settings (DB, apps, middleware)
│   ├── urls.py                 # Root URL configuration
│   ├── wsgi.py                 # WSGI entry point
│   └── asgi.py                 # ASGI entry point
│
├── app/                        # Main application
│   ├── models.py               # Database models
│   ├── views.py                # View functions
│   ├── urls.py                 # App URL routes
│   ├── forms.py                # Django forms
│   ├── admin.py                # Admin configuration
│   │
│   ├── algorithms/             # Timetable generation algorithms
│   │   └── backtracking.py     # Backtracking algorithm implementation
│   │
│   ├── templates/              # HTML templates
│   │   ├── layouts/
│   │   │   └── base.html       # Base layout
│   │   ├── auth/
│   │   │   ├── login.html      # Login page
│   │   │   └── signup.html     # Registration page
│   │   ├── pages/
│   │   │   ├── index.html      # Home — timetable generator
│   │   │   ├── dashboard.html  # Dashboard with stats
│   │   │   ├── timetable_list.html  # All timetables
│   │   │   ├── course_list.html     # All courses
│   │   │   ├── instructor_list.html # All instructors
│   │   │   ├── send_timetable.html  # Email timetable form
│   │   │   └── support.html    # Support/disclaimer page
│   │   ├── includes/
│   │   │   ├── navigation-light.html  # Top navbar
│   │   │   └── footer.html     # Footer
│   │   └── emails/
│   │       └── timetable_email.html   # Email template
│   │
│   ├── static/                 # Static files (CSS, JS, fonts)
│   │   ├── dist/
│   │   ├── fonts/
│   │   └── plugins/
│   │
│   └── templatetags/
│       └── custom_filters.py   # Custom template filters
│
└── venv/                       # Python virtual environment
```

---

## Database Models

| Model          | Description                              |
|:---------------|:-----------------------------------------|
| `Department`   | Academic departments                     |
| `Instructor`   | Users/teachers (extends AbstractUser)    |
| `TimeTableMain`| Programme/semester/year configuration    |
| `CourseName`   | Courses with codes and descriptions      |
| `Venue`        | Classrooms/labs/halls                    |
| `TimeTable`    | Actual timetable entries (scheduled sessions) |

---

## Setup & Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step-by-step Setup

```bash
# 1. Clone or navigate to the project directory
cd TT_project

# 2. Create a virtual environment
python3 -m venv venv

# 3. Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install django>=4.2,<4.3 django-jazzmin crispy-bootstrap5 django-crispy-forms

# 5. Run database migrations
python manage.py migrate

# 6. Create a superuser (admin account)
python manage.py createsuperuser

# 7. Start the development server
python manage.py runserver

# 8. Open in browser
# Visit: http://127.0.0.1:8000/
# Admin: http://127.0.0.1:8000/admin/
```

---

## Usage

### 1. Setting Up Data (Admin)
1. Log in to the admin panel at `/admin/`
2. Add **Departments** (e.g., Computer Science, Mathematics)
3. Add **Venues** (e.g., Room 101, Lab A)
4. Add **Courses** (e.g., Data Structures - CS201)
5. Add **Instructors** (or they can sign up themselves)
6. Add **Programmes** via TimeTableMain (e.g., B.Tech CS, Semester 1)

### 2. Generating Timetable
1. Go to the home page (`/`)
2. Select a **Programme**, **Semester**, and **Year of Study**
3. Click **Search** — the backtracking algorithm generates a conflict-free timetable
4. View the generated timetable grouped by day

### 3. Viewing Data (All Users)
- **Dashboard** (`/dashboard/`) — Overview statistics
- **Timetables** (`/timetables/`) — All saved timetable entries
- **Courses** (`/courses/`) — All available courses
- **Instructors** (`/instructors/`) — All registered instructors

### 4. Sending Timetable via Email
1. Go to `/send-timetable/`
2. Enter the recipient email, select a day
3. Click Send — the timetable is emailed

---

## Default Admin Credentials

After running `createsuperuser`, use those credentials to log in.  
Example setup:
```
Username: admin
Email: admin@example.com
Password: (your chosen password)
```

---

## License

This project is developed for academic purposes as part of a college project.

---

## Authors

- Shubham Nemade
