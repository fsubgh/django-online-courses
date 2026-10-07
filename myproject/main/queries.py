from django.db import models
from django.db.models import Avg, Count

from .models import (
    Course,
    Instructor,
    Student,
    Category,
    Enrollment
)


def get_published_courses():
    return Course.objects.filter(
        is_published=True
    )


def get_courses_by_level(level):
    return Course.objects.filter(
        level=level
    )


def get_instructor_courses(instructor_id):
    return Course.objects.filter(
        instructor_id=instructor_id
    )


def get_popular_courses(min_students):
    return Course.objects.annotate(
        student_count=Count(
            'enrollments',
            filter=~models.Q(
                enrollments__status=Enrollment.STATUS_CANCELLED
            )
        )
    ).filter(
        student_count__gte=min_students
    )


def get_student_active_courses(student_id):
    return Course.objects.filter(
        enrollments__student_id=student_id,
        enrollments__status=Enrollment.STATUS_IN_PROGRESS
    )


def get_category_with_subcategories(category_id):
    return Category.objects.filter(
        id=category_id
    ).prefetch_related(
        'subcategories'
    ).first()


def get_expensive_courses(min_price):
    return Course.objects.filter(
        price__gt=min_price
    )


def get_instructors_by_rating(min_rating):
    return Instructor.objects.filter(
        rating__gt=min_rating
    )


def get_courses_with_available_spots():
    courses = Course.objects.filter(
        max_students__isnull=False
    ).annotate(
        enrolled_count=Count(
            'enrollments',
            filter=~models.Q(
                enrollments__status=Enrollment.STATUS_CANCELLED
            )
        )
    ).filter(
        enrolled_count__lt=models.F('max_students')
    )

    return courses


def update_enrollment_progress(enrollment_id, progress):
    enrollment = Enrollment.objects.get(
        id=enrollment_id
    )

    enrollment.progress = progress
    enrollment.save()

    return enrollment


def complete_enrollment(enrollment_id, grade):
    enrollment = Enrollment.objects.get(
        id=enrollment_id
    )

    enrollment.status = Enrollment.STATUS_COMPLETED
    enrollment.progress = 100
    enrollment.grade = grade
    enrollment.save()

    return enrollment


def get_student_statistics(student_id):
    enrollments = Enrollment.objects.filter(
        student_id=student_id
    )

    completed = enrollments.filter(
        status=Enrollment.STATUS_COMPLETED
    )

    average_grade = completed.filter(
        grade__isnull=False
    ).aggregate(
        average=Avg('grade')
    )['average']

    return {
        'courses_count': enrollments.count(),
        'completed_courses': completed.count(),
        'average_grade': average_grade
    }


def get_instructor_statistics(instructor_id):
    courses = Course.objects.filter(
        instructor_id=instructor_id
    )

    students_count = Enrollment.objects.filter(
        course__instructor_id=instructor_id
    ).exclude(
        status=Enrollment.STATUS_CANCELLED
    ).values(
        'student'
    ).distinct().count()

    average_rating = courses.aggregate(
        average=Avg('instructor__rating')
    )['average']

    return {
        'courses_count': courses.count(),
        'students_count': students_count,
        'average_rating': average_rating
    }