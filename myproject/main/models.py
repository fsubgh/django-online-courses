from django.db import models

# Create your models here.
from django.core.validators import MinValueValidator, MaxValueValidator


class Instructor(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    specialization = models.CharField(max_length=200)
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5)
        ]
    )
    start_date = models.DateField()
    biography = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Course(models.Model):
    LEVEL_BEGINNER = 'beginner'
    LEVEL_INTERMEDIATE = 'intermediate'
    LEVEL_ADVANCED = 'advanced'

    LEVEL_CHOICES = [
        (LEVEL_BEGINNER, 'Начальный'),
        (LEVEL_INTERMEDIATE, 'Средний'),
        (LEVEL_ADVANCED, 'Продвинутый'),
    ]

    name = models.CharField(max_length=200)
    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.CASCADE,
        related_name='courses'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='courses'
    )
    description = models.TextField()
    duration_hours = models.PositiveIntegerField()
    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    max_students = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    students = models.ManyToManyField(
        'Student',
        through='Enrollment',
        related_name='courses'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'

    def __str__(self):
        return self.name

    def get_available_spots(self):
        if self.max_students is None:
            return None

        enrolled_count = self.enrollments.exclude(
            status=Enrollment.STATUS_CANCELLED
        ).count()

        return max(self.max_students - enrolled_count, 0)


class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def get_completed_courses(self):
        return Course.objects.filter(
            enrollments__student=self,
            enrollments__status=Enrollment.STATUS_COMPLETED
        )


class Enrollment(models.Model):
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_IN_PROGRESS, 'В процессе'),
        (STATUS_COMPLETED, 'Завершен'),
        (STATUS_CANCELLED, 'Отменен'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_IN_PROGRESS
    )
    progress = models.PositiveIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
    )
    grade = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
    )

    class Meta:
        ordering = ['-enrolled_at']
        verbose_name = 'Запись на курс'
        verbose_name_plural = 'Записи на курсы'
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'course'],
                name='unique_student_course'
            )
        ]

    def __str__(self):
        return f'{self.student} — {self.course}'