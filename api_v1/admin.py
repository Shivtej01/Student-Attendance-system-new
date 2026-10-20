from django.contrib import admin, messages
from django.utils import timezone
from .models import (
    AdminSignupRequest, Department, Subject, Student, StudentSubject, Attendance,
)


@admin.register(AdminSignupRequest)
class AdminSignupRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'created_at', 'status')
    list_filter = ('approved_at',)
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    actions = ('approve_requests',)

    @admin.display(description='Email')
    def email(self, obj):
        return obj.user.email

    @admin.display(description='Status')
    def status(self, obj):
        return 'Approved' if obj.approved_at else 'Pending'

    @admin.action(description='Approve selected admin signup requests')
    def approve_requests(self, request, queryset):
        pending = queryset.filter(approved_at__isnull=True)
        count = pending.count()
        for signup_request in pending.select_related('user'):
            user = signup_request.user
            user.is_active = True
            user.is_staff = True
            user.save(update_fields=('is_active', 'is_staff'))
            signup_request.approved_at = timezone.now()
            signup_request.save(update_fields=('approved_at',))
        self.message_user(
            request,
            f'{count} admin signup request(s) approved.',
            messages.SUCCESS,
        )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    search_fields = ('name', 'code')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subject_code', 'title', 'department', 'credits', 'is_active')
    list_filter = ('department', 'is_active')
    search_fields = ('title',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'first_name', 'last_name', 'email', 'department', 'is_active')
    list_filter = ('department', 'is_active')
    search_fields = ('first_name', 'last_name', 'email', 'roll_number')
    readonly_fields = ('student_id', 'created_at', 'updated_at')


@admin.register(StudentSubject)
class StudentSubjectAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'created_at')
    list_filter = ('subject',)
    search_fields = ('student__first_name', 'student__last_name')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'lecture_date', 'status', 'marked_by')
    list_filter = ('status', 'subject', 'lecture_date')
    search_fields = ('student__first_name', 'student__last_name')
    date_hierarchy = 'lecture_date'
