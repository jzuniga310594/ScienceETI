from django.contrib import admin
from .models import (
    ClassGroup, StudentProfile,
    ProblemTemplate, Assignment, AssignmentProblem,
    ProblemInstance, Submission
)

admin.site.register(ClassGroup)
admin.site.register(StudentProfile)
admin.site.register(ProblemTemplate)
admin.site.register(Assignment)
admin.site.register(AssignmentProblem)
admin.site.register(ProblemInstance)
admin.site.register(Submission)
