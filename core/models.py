from django.conf import settings
from django.db import models
from django.utils import timezone


class ClassGroup(models.Model):
    name = models.CharField(max_length=60)               # Ej: "2°B"
    code = models.CharField(max_length=20, unique=True)  # Ej: "2B-2026"

    def __str__(self):
        return f"{self.name} ({self.code})"


class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey(ClassGroup, on_delete=models.PROTECT)

    def __str__(self):
        return self.user.get_username()


class ProblemTemplate(models.Model):
    TOPICS = [
        ("CIN", "Cinemática"),
        ("DIN", "Dinámica"),
        ("ENE", "Trabajo y energía"),
        ("POT", "Potencia"),
    ]

    title = models.CharField(max_length=120)
    topic = models.CharField(max_length=3, choices=TOPICS)

    # Texto con llaves: {a}, {t}, etc.
    prompt_template = models.TextField()

    # Ej: {"a":{"min":1,"max":6,"step":1}, "t":{"min":2,"max":10,"step":1}}
    params_schema = models.JSONField(default=dict)

    # Fórmula (segura) con parámetros: "a*t", "F*d*cos(theta)", etc.
    answer_formula = models.CharField(max_length=200)

    unit = models.CharField(max_length=20, blank=True)  # Ej: "m/s"
    tolerance_abs = models.FloatField(default=0.01)
    tolerance_rel = models.FloatField(default=0.02)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class Assignment(models.Model):
    title = models.CharField(max_length=120)
    group = models.ForeignKey(ClassGroup, on_delete=models.CASCADE)

    start_at = models.DateTimeField()
    end_at = models.DateTimeField()

    max_attempts_per_problem = models.PositiveIntegerField(default=3)
    show_feedback = models.BooleanField(default=True)

    def is_open(self):
        now = timezone.now()
        return self.start_at <= now <= self.end_at

    def __str__(self):
        return f"{self.title} - {self.group.name}"


class AssignmentProblem(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="items")
    problem = models.ForeignKey(ProblemTemplate, on_delete=models.CASCADE)
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("assignment", "order")
        ordering = ["order"]

    def __str__(self):
        return f"{self.assignment.title} #{self.order} - {self.problem.title}"


class ProblemInstance(models.Model):
    assignment_problem = models.ForeignKey(AssignmentProblem, on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    params = models.JSONField(default=dict)
    correct_answer = models.FloatField()

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("assignment_problem", "student")

    def __str__(self):
        return f"Instance {self.id} - {self.student} - {self.assignment_problem}"


class Submission(models.Model):
    instance = models.ForeignKey(ProblemInstance, on_delete=models.CASCADE, related_name="submissions")
    submitted_answer = models.FloatField()
    is_correct = models.BooleanField(default=False)
    score = models.FloatField(default=0.0)

    submitted_at = models.DateTimeField(default=timezone.now)

    # Campos listos para “control” (se conectan después con JS)
    seconds_spent = models.PositiveIntegerField(default=0)
    tab_switches = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Sub {self.id} - {self.instance_id}"
