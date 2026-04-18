"""
Management command to populate the database with PCCOE data.
Supports credit-based scheduling for Theory and Labs.
"""

from django.core.management.base import BaseCommand
from app.models import Department, Instructor, CourseName, Venue, TimeTableMain, TimeTable

class Command(BaseCommand):
    help = 'Populate database with credit-based PCCOE data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('\n=== Clearing old data ==='))
        TimeTable.objects.all().delete()
        TimeTableMain.objects.all().delete()
        CourseName.objects.all().delete()
        Venue.objects.all().delete()
        Instructor.objects.filter(is_superuser=False).delete()
        Department.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('  Old data cleared.'))

        # ---------------------------------------------
        # 1. DEPARTMENTS
        # ---------------------------------------------
        departments = {
            'Computer Engineering': 'Dr. Sonali D. Patil',
            'Information Technology': 'Dr. Rajesh M. Jalnekar',
            'Mechanical Engineering': 'Dr. Sunil S. Deshpande',
            'Civil Engineering': 'Dr. Anil Kumar Sharma',
            'AI & ML Engineering': 'Dr. Priya R. Kulkarni',
            'ENTC Engineering': 'Dr. Mahesh B. Gaikwad',
        }
        dept_objs = {}
        for dept_name, hod in departments.items():
            dept_objs[dept_name] = Department.objects.create(DepartmentName=dept_name, HeadOfDepartment=hod)

        # ---------------------------------------------
        # 2. VENUES
        # ---------------------------------------------
        venues = ['101CR', '102CR', '103CR', '104CR', '105CR', '201CR', '202CR', '203CR', '204CR', '205CR',
                  '101LA', '102LA', '103LA', '104LA', '105LA', '201LA', '202LA', '203LA', '204LA', '205LA']
        venue_objs = {v: Venue.objects.create(Venue=v) for v in venues}

        # ---------------------------------------------
        # 3. FACULTY, COURSES, TIMETABLE MAIN
        # ---------------------------------------------
        prog_data = {
            'Computer Engineering': ('B.Tech Computer Engineering', 'CS', [
                ('dr.sonali.patil', 'Dr. Sonali', 'Patil'), ('dr.rajeswari.k', 'Dr. K.', 'Rajeswari'),
                ('dr.sudeep.thepade', 'Dr. Sudeep', 'Thepade'), ('dr.swati.shinde', 'Dr. Swati', 'Shinde'),
                ('dr.sambare', 'Dr. G. B.', 'Sambare'), ('dr.reena.kharat', 'Dr. Reena', 'Kharat'),
                ('dr.srinivas.ambala', 'Dr. Srinivas', 'Ambala'), ('dr.pravin.game', 'Dr. Pravin', 'Game'),
                ('atul.pawar', 'Mr. Atul', 'Pawar'), ('deepali.jawale', 'Mrs. Deepali', 'Jawale'),
                ('madhuri.pagale', 'Mrs. Madhuri', 'Pagale'), ('ganesh.kadam', 'Mr. Ganesh', 'Kadam'),
            ]),
            'Information Technology': ('B.Tech Information Technology', 'IT', [
                ('dr.neha.sharma', 'Dr. Neha', 'S'), ('prof.vikas.deshmukh', 'Prof. Vikas', 'D'),
                ('prof.anita.kulkarni', 'Prof. Anita', 'K'), ('prof.sachin.pawar', 'Prof. Sachin', 'P'),
                ('prof.pooja.joshi', 'Prof. Pooja', 'J'), ('prof.ramesh.patil', 'Prof. Ramesh', 'P')
            ]),
            'Mechanical Engineering': ('B.Tech Mechanical Engineering', 'ME', [
                ('dr.rajendra.mane', 'Dr. Rajendra', 'Mane'), ('prof.suresh.jadhav', 'Prof. Suresh', 'J'),
                ('prof.ashok.nikam', 'Prof. Ashok', 'N'), ('prof.sandip.bhosale', 'Prof. Sandip', 'B'),
                ('prof.prashant.gawade', 'Prof. Prashant', 'G'), ('prof.deepak.sawant', 'Prof. Deepak', 'S')
            ]),
            'Civil Engineering': ('B.Tech Civil Engineering', 'CE', [
                ('dr.mahesh.wagh', 'Dr. Mahesh', 'Wagh'), ('prof.sanjay.more', 'Prof. Sanjay', 'M'),
                ('prof.nilesh.kale', 'Prof. Nilesh', 'K'), ('prof.amita.desai', 'Prof. Amita', 'D'),
                ('prof.vivek.chavan', 'Prof. Vivek', 'C'), ('prof.sneha.karpe', 'Prof. Sneha', 'K')
            ]),
            'AI & ML Engineering': ('B.Tech AI & ML', 'AI', [
                ('dr.amit.joshi', 'Dr. Amit', 'Joshi'), ('prof.snehal.thakkar', 'Prof. Snehal', 'T'),
                ('prof.rohan.deshpande', 'Prof. Rohan', 'D'), ('prof.manasi.bhate', 'Prof. Manasi', 'B'),
                ('prof.nikhil.wagh', 'Prof. Nikhil', 'W'), ('prof.prachi.kulkarni', 'Prof. Prachi', 'K')
            ]),
            'ENTC Engineering': ('B.Tech ENTC', 'EC', [
                ('dr.sunil.bhirud', 'Dr. Sunil', 'Bhirud'), ('prof.manoj.patil', 'Prof. Manoj', 'P'),
                ('prof.swapnil.kumbhar', 'Prof. Swapnil', 'K'), ('prof.vaishali.gaikar', 'Prof. Vaishali', 'G'),
                ('prof.tushar.salunkhe', 'Prof. Tushar', 'S'), ('prof.rashmi.joshi', 'Prof. Rashmi', 'J')
            ])
        }

        # Map branch prefix to subjects (5 Theory, 5 Labs)
        branch_subjects = {
            'CS': [
                ('OS', 'Operating Systems', 4, 'Lecture'), ('DAA', 'Design and Analysis of Algorithms', 4, 'Lecture'), ('SE', 'Software Engineering', 4, 'Lecture'), ('CMD', 'Cloud Computing', 4, 'Lecture'), ('UI', 'UI/UX Design', 4, 'Lecture'),
                ('OSL', 'Operating Systems Lab', 4, 'Lab'), ('DAAL', 'Algorithm Design Lab', 4, 'Lab'), ('SEL', 'Software Engineering Lab', 4, 'Lab'), ('CMDL', 'Cloud Computing Lab', 4, 'Lab'), ('UIL', 'UI/UX Lab', 4, 'Lab')
            ],
            'IT': [
                ('DBMS', 'Database Management', 4, 'Lecture'), ('CN', 'Computer Networks', 4, 'Lecture'), ('WD', 'Web Development', 4, 'Lecture'), ('AIN', 'Artificial Intelligence', 4, 'Lecture'), ('INS', 'Information Security', 4, 'Lecture'),
                ('DBMSL', 'DBMS Lab', 4, 'Lab'), ('CNL', 'Networking Lab', 4, 'Lab'), ('WDL', 'Web Dev Lab', 4, 'Lab'), ('AINL', 'AI Lab', 4, 'Lab'), ('INSL', 'Security Lab', 4, 'Lab')
            ],
            'ME': [
                ('TD', 'Thermodynamics', 4, 'Lecture'), ('FM', 'Fluid Mechanics', 4, 'Lecture'), ('DOM', 'Dynamics of Machinery', 4, 'Lecture'), ('HT', 'Heat Transfer', 4, 'Lecture'), ('CAD', 'Computer Aided Design', 4, 'Lecture'),
                ('TDL', 'Thermodynamics Lab', 4, 'Lab'), ('FML', 'Fluid Mechanics Lab', 4, 'Lab'), ('DOML', 'Machinery Lab', 4, 'Lab'), ('HTL', 'Heat Transfer Lab', 4, 'Lab'), ('CADL', 'CAD Lab', 4, 'Lab')
            ],
            'CE': [
                ('SM', 'Structural Mechanics', 4, 'Lecture'), ('GE', 'Geotechnical Engg', 4, 'Lecture'), ('HY', 'Hydraulics', 4, 'Lecture'), ('SUR', 'Surveying', 4, 'Lecture'), ('EM', 'Environmental Engg', 4, 'Lecture'),
                ('SML', 'Structural Lab', 4, 'Lab'), ('GEL', 'Geotechnical Lab', 4, 'Lab'), ('HYL', 'Hydraulics Lab', 4, 'Lab'), ('SURL', 'Surveying Lab', 4, 'Lab'), ('EML', 'Environmental Lab', 4, 'Lab')
            ],
            'AI': [
                ('ML', 'Machine Learning', 4, 'Lecture'), ('DL', 'Deep Learning', 4, 'Lecture'), ('NLP', 'Natural Language Processing', 4, 'Lecture'), ('CV', 'Computer Vision', 4, 'Lecture'), ('BDA', 'Big Data Analytics', 4, 'Lecture'),
                ('MLL', 'ML Lab', 4, 'Lab'), ('DLL', 'Deep Learning Lab', 4, 'Lab'), ('NLPL', 'NLP Lab', 4, 'Lab'), ('CVL', 'Computer Vision Lab', 4, 'Lab'), ('BDAL', 'Big Data Lab', 4, 'Lab')
            ],
            'EC': [
                ('SS', 'Signals and Systems', 4, 'Lecture'), ('DC', 'Digital Communication', 4, 'Lecture'), ('VLSI', 'VLSI Design', 4, 'Lecture'), ('MP', 'Microprocessors', 4, 'Lecture'), ('AC', 'Analog Circuits', 4, 'Lecture'),
                ('SSL', 'Signals Lab', 4, 'Lab'), ('DCL', 'Digital Comm Lab', 4, 'Lab'), ('VLSIL', 'VLSI Lab', 4, 'Lab'), ('MPL', 'Microprocessors Lab', 4, 'Lab'), ('ACL', 'Analog Circuits Lab', 4, 'Lab')
            ]
        }

        for dept_name, (prog_name, prefix, faculty_list) in prog_data.items():
            dept = dept_objs[dept_name]

            # Instructors
            instr_list = []
            for uname, fname, lname in faculty_list:
                instr = Instructor.objects.create(username=uname, FirstName=fname, LastName=lname, Department=dept, is_staff=False, is_superuser=False)
                instr.set_password('Faculty@123')
                instr.save()
                instr_list.append(instr)

            # Programme
            prog = TimeTableMain.objects.create(Programme=prog_name, YearOfStudy='Third Year', Semister='Semester 5', Department=dept)

            # Courses & Exact Workload Generation
            crs_idx = 1
            subjects = branch_subjects.get(prefix, [])
            for num, (sub_name, sub_desc, credits, stype) in enumerate(subjects):
                ccode = f"{prefix}3{str(crs_idx).zfill(2)}"
                course = CourseName.objects.create(Course=sub_name, CourseCode=ccode, CourseDescription=f"{dept_name} {sub_desc}", Credits=credits)
                crs_idx += 1

                instructor = instr_list[num % len(instr_list)]
                
                # Venue selection
                venue_name = f"{(num % 2) + 1}0{num % 5 + 1}" + ("LA" if stype == 'Lab' else "CR")
                if venue_name not in venue_objs:
                    venue_name = "101LA" if stype == 'Lab' else "101CR"
                venue = venue_objs[venue_name]

                # Sessions calculation
                if stype == 'Lab':
                    sessions = credits // 2
                else:
                    sessions = credits // 1

                # Generate placeholder sessions for backtracking later
                for s in range(sessions):
                    TimeTable.objects.create(
                        CourseName=course,
                        Instructor=instructor,
                        Venue=venue,
                        Timestart='09:00', # temporary
                        TimeEnd='10:00',   # temporary
                        Day='Monday',      # temporary
                        Programme=prog,
                        SessionType=stype,
                    )
            
            self.stdout.write(f'  {prog_name}: Created 10 courses and TimeTable placeholders.')

        self.stdout.write(self.style.SUCCESS('\n=== DATABASE POPULATION COMPLETE! ===\n'))
