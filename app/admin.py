from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
from django.utils.html import format_html

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('DepartmentName', 'HeadOfDepartment', 'registered_date_formatted')
    search_fields = ('DepartmentName', 'HeadOfDepartment')
    list_filter = ('RegisteredDate',)
    
    def registered_date_formatted(self, obj):
        return format_html('<span class="badge bg-info">{}</span>', obj.RegisteredDate.strftime('%Y-%m-%d'))
    registered_date_formatted.short_description = 'Registered Date'

@admin.register(Instructor)
class InstructorAdmin(UserAdmin):
    list_display = ('username', 'email', 'FirstName', 'LastName', 'Department', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'Department')
    search_fields = ('username', 'FirstName', 'LastName', 'email')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('FirstName', 'LastName', 'email', 'Department')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'FirstName', 'LastName', 'email', 'Department'),
        }),
    )

@admin.register(TimeTableMain)
class TimeTableMainAdmin(admin.ModelAdmin):
    list_display = ('Programme', 'YearOfStudy', 'Semister', 'Department', 'registered_date_formatted')
    list_filter = ('YearOfStudy', 'Semister', 'Department')
    search_fields = ('Programme',)
    
    def registered_date_formatted(self, obj):
        return format_html('<span class="badge bg-info">{}</span>', obj.RegisteredDate.strftime('%Y-%m-%d'))
    registered_date_formatted.short_description = 'Registered Date'

@admin.register(CourseName)
class CourseNameAdmin(admin.ModelAdmin):
    list_display = ('Course', 'CourseCode', 'CourseDescription')
    search_fields = ('Course', 'CourseCode')
    list_filter = ('RegisteredDate',)

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('Venue', 'registered_date_formatted')
    search_fields = ('Venue',)
    
    def registered_date_formatted(self, obj):
        return format_html('<span class="badge bg-info">{}</span>', obj.RegisteredDate.strftime('%Y-%m-%d'))
    registered_date_formatted.short_description = 'Registered Date'

@admin.register(TimeTable)
class TimeTableAdmin(admin.ModelAdmin):
    list_display = ('get_course', 'Day', 'Timestart', 'TimeEnd', 'Venue', 'Instructor', 'SessionType')
    list_filter = ('Day', 'SessionType', 'Programme', 'Venue')
    search_fields = ('CourseName__Course', 'Instructor__username', 'Venue__Venue')
    date_hierarchy = 'RegisteredDate'
    
    def get_course(self, obj):
        return f"{obj.CourseName.Course} ({obj.CourseName.CourseCode})"
    get_course.short_description = 'Course'
    
    fieldsets = (
        ('Course Information', {
            'fields': ('CourseName', 'Instructor', 'Programme')
        }),
        ('Schedule', {
            'fields': ('Day', 'Timestart', 'TimeEnd', 'SessionType')
        }),
        ('Location', {
            'fields': ('Venue',)
        }),
    )
