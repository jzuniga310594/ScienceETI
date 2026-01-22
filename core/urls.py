from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("", views.dashboard, name="dashboard"),
    path("assignment/<int:assignment_id>/start/", views.start_assignment, name="start_assignment"),
    path("solve/<int:assignment_problem_id>/", views.solve_problem, name="solve_problem"),
    path("assignment/<int:assignment_id>/results/", views.results, name="results"),
]
