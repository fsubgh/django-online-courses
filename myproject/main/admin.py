from django.contrib import admin

# Register your models here.

from .models import (
    Instructor,
    Category,
    Course,
    Student,
    Enrollment
)


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = (
        'first_name',
        'last_name',
        'email',
        'specialization',
        'rating',
        'start_date',
        'is_active'
    )

    list_filter = (
        'is_active',
        'specialization'
    )

    search_fields = (
        'first_name',
        'last_name',
        'email'
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'parent'
    )

    search_fields = (
        'name',
        'slug'
    )

    list_filter = (
        'parent',
    )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'instructor',
        'category',
        'level',
        'price',
        'is_published',
        'max_students'
    )

    list_filter = (
        'level',
        'is_published',
        'category'
    )

    search_fields = (
        'name',
        'description'
    )

    inlines = [
        EnrollmentInline
    ]


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'first_name',
        'last_name',
        'email',
        'registered_at'
    )

    search_fields = (
        'first_name',
        'last_name',
        'email'
    )


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'course',
        'enrolled_at',
        'status',
        'progress',
        'grade'
    )

    list_filter = (
        'status',
    )

    search_fields = (
        'student__first_name',
        'student__last_name',
        'course__name'
    )