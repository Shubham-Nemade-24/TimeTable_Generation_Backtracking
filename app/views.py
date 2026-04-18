from django.shortcuts import render, redirect
from .models import *
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import CustomUserCreationForm, EmailTimetableForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .algorithms.backtracking import BacktrackingTimetableAlgorithm

# Get the current date
today = datetime.now()
# Calculate the date of Monday and Friday of the current week
monday = today - timedelta(days=today.weekday())
friday = monday + timedelta(days=4)
# Get the current year
current_year = today.year
# Format the dates
monday_formatted = monday.strftime('%Y-%m-%d')
friday_formatted = friday.strftime('%Y-%m-%d')


def index(request):
    """Home page with timetable generation form using backtracking algorithm."""
    # Fetch distinct programmes, semesters, and years of study from TimeTableMain model
    programmes = TimeTableMain.objects.values_list('Programme', flat=True).distinct()
    semesters = TimeTableMain.objects.values_list('Semister', flat=True).distinct()
    years_of_study = TimeTableMain.objects.values_list('YearOfStudy', flat=True).distinct()

    timetable_data = {}
    selected_programme = None
    department = None

    # Handle POST request — generate timetable using backtracking
    if request.method == 'POST':
        programme = request.POST.get('programme')
        semester = request.POST.get('semester')
        year_of_study = request.POST.get('year_of_study')
        selected_programme = programme

        # Get department for display
        try:
            tt_main = TimeTableMain.objects.get(Programme=programme)
            department = tt_main.Department
        except TimeTableMain.DoesNotExist:
            department = None

        # Use backtracking algorithm to generate timetable
        algorithm = BacktrackingTimetableAlgorithm()
        solution = algorithm.solve(programme, semester, year_of_study)

        if solution and "solution" in solution:
            # Parse the tree data
            tree_data_json = solution["tree"]
            
            # We delete the old Unassigned placeholder tables so we can save the new ones
            TimeTable.objects.filter(
                Programme__Programme=programme,
                Programme__Semister=semester,
                Programme__YearOfStudy=year_of_study
            ).delete()

            # Convert solution entries to TimeTable-like objects for template rendering
            timetable_entries = []
            for entry in solution["solution"]:
                # Convert string 24h to time object for Django templates
                t_start_obj = datetime.strptime(entry.time_start, "%H:%M").time()
                t_end_obj = datetime.strptime(entry.time_end, "%H:%M").time()

                tt_entry = TimeTable(
                    CourseName=entry.course,
                    Instructor=entry.instructor,
                    Venue=entry.venue,
                    Timestart=t_start_obj,
                    TimeEnd=t_end_obj,
                    Day=entry.day,
                    Programme=tt_main,
                    SessionType=entry.session_type,
                )
                tt_entry.save() # Commits exact schedule to Database properly!
                timetable_entries.append(tt_entry)

            # Group entries by day (ordered)
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            timetable_data = {day: [] for day in day_order}
            for entry in timetable_entries:
                if entry.Day in timetable_data:
                    timetable_data[entry.Day].append(entry)

            # Remove empty days
            timetable_data = {day: entries for day, entries in timetable_data.items() if entries}

            messages.success(request, f'Timetable generated successfully using Backtracking Algorithm! ({len(solution)} sessions scheduled)')
        else:
            messages.warning(request, 'Could not generate timetable. Please add more courses, instructors, and venues first.')

    context = {
        'programmes': programmes,
        'semesters': semesters,
        'years_of_study': years_of_study,
        'timetable_data': timetable_data,
        'tree_data': tree_data_json if 'tree_data_json' in locals() else None,
        'selected_programme': selected_programme,
        'department': department,
        'monday': monday_formatted,
        'friday': friday_formatted,
        'current_year': current_year,
    }
    return render(request, 'pages/index.html', context)


def support(request):
    """Support and disclaimer page."""
    return render(request, 'pages/support.html')


def signup(request):
    """User registration page."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'auth/signup.html', {'form': form})


@login_required
def dashboard(request):
    """Dashboard with statistics overview — accessible to all logged-in users."""
    context = {
        'total_courses': CourseName.objects.count(),
        'total_instructors': Instructor.objects.count(),
        'total_venues': Venue.objects.count(),
        'total_timetables': TimeTable.objects.count(),
        'total_departments': Department.objects.count(),
        'total_programmes': TimeTableMain.objects.count(),
    }
    return render(request, 'pages/dashboard.html', context)


@login_required
def timetable_list(request):
    """View all timetable entries — accessible to all logged-in users."""
    timetables = TimeTable.objects.select_related(
        'CourseName', 'Instructor', 'Venue', 'Programme'
    ).order_by('Day', 'Timestart')

    # Group by day for display
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    timetable_data = {day: [] for day in day_order}
    for entry in timetables:
        if entry.Day in timetable_data:
            timetable_data[entry.Day].append(entry)

    # Remove empty days
    timetable_data = {day: entries for day, entries in timetable_data.items() if entries}

    context = {
        'timetable_data': timetable_data,
        'total_entries': timetables.count(),
    }
    return render(request, 'pages/timetable_list.html', context)


@login_required
def course_list(request):
    """View all courses — accessible to all logged-in users."""
    courses = CourseName.objects.all().order_by('Course')
    context = {
        'courses': courses,
        'total_courses': courses.count(),
    }
    return render(request, 'pages/course_list.html', context)


@login_required
def instructor_list(request):
    """View all instructors — accessible to all logged-in users."""
    instructors = Instructor.objects.select_related('Department').all().order_by('username')
    context = {
        'instructors': instructors,
        'total_instructors': instructors.count(),
    }
    return render(request, 'pages/instructor_list.html', context)


def send_timetable_email(request):
    """Send timetable via email."""
    if request.method == 'POST':
        form = EmailTimetableForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            day = form.cleaned_data['day']
            programme = form.cleaned_data['programme']

            # Get timetable entries for the selected day and programme
            timetable_entries = TimeTable.objects.filter(
                Day=day,
                Programme__Programme=programme
            ).order_by('Timestart')

            # Prepare email content
            context = {
                'day': day,
                'programme': programme,
                'timetable_entries': timetable_entries,
            }

            html_message = render_to_string('emails/timetable_email.html', context)
            plain_message = strip_tags(html_message)

            try:
                send_mail(
                    subject=f'Timetable for {day}',
                    message=plain_message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    html_message=html_message,
                    fail_silently=False,
                )
                messages.success(request, 'Timetable has been sent to your email!')
            except Exception as e:
                messages.error(request, f'Failed to send email: {str(e)}')

            return redirect('dashboard')
    else:
        form = EmailTimetableForm()

    return render(request, 'pages/send_timetable.html', {'form': form})