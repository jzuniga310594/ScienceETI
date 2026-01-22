from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from .models import Assignment, AssignmentProblem, Submission
from .services import get_or_create_instance
from .utils import is_within_tolerance
from .forms import SignupForm


def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    feedback = None
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
        else:
            feedback = "Revisa los datos: usuario/código/contraseñas."
    else:
        form = SignupForm()

    return render(request, "core/signup.html", {"form": form, "feedback": feedback})


@login_required
def dashboard(request):
    profile = request.user.studentprofile
    assignments = Assignment.objects.filter(group=profile.group).order_by("-start_at")
    return render(request, "core/dashboard.html", {"assignments": assignments})


@login_required
def start_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if not assignment.is_open():
        return render(request, "core/message.html", {"msg": "Esta actividad no está disponible en este momento."})

    items = assignment.items.select_related("problem").all()

    # Asegurar instancias y elegir el primer ejercicio NO resuelto
    first_pending_id = None
    for ap in items:
        inst = get_or_create_instance(ap, request.user)
        solved = inst.submissions.filter(is_correct=True).exists()
        if not solved and first_pending_id is None:
            first_pending_id = ap.id

    if first_pending_id is None:
        # Ya resolvió todo (o al menos lo resolvió correctamente en cada uno)
        return redirect("results", assignment_id=assignment.id)

    return redirect("solve_problem", assignment_problem_id=first_pending_id)



@login_required
def solve_problem(request, assignment_problem_id):
    ap = get_object_or_404(
        AssignmentProblem.objects.select_related("assignment", "problem"),
        id=assignment_problem_id
    )
    assignment = ap.assignment
    if not assignment.is_open():
        return render(request, "core/message.html", {"msg": "Esta actividad ya no está disponible."})

    inst = get_or_create_instance(ap, request.user)
    already_solved = inst.submissions.filter(is_correct=True).exists()
    if already_solved:
        attempts_left = 0  # desactiva el formulario aunque el alumno regrese
        feedback = "Este ejercicio ya fue resuelto correctamente. ✅"

    tpl = ap.problem

    attempts_used = inst.submissions.count()
    attempts_left = max(0, assignment.max_attempts_per_problem - attempts_used)

    feedback = None
    if request.method == "POST" and attempts_left > 0 and not already_solved:
        raw = request.POST.get("answer", "").strip()
        try:
            submitted = float(raw)
        except:
            submitted = None

        if submitted is not None:
            ok = is_within_tolerance(inst.correct_answer, submitted, tpl.tolerance_abs, tpl.tolerance_rel)
            score = ap.points if ok else 0.0
            Submission.objects.create(
                instance=inst,
                submitted_answer=submitted,
                is_correct=ok,
                score=score,
            )
            if assignment.show_feedback:
                feedback = "Correcto ✅" if ok else "Incorrecto ❌"

    prompt = tpl.prompt_template.format(**inst.params)

    items = list(assignment.items.all())
    idx = [x.id for x in items].index(ap.id)
    prev_id = items[idx - 1].id if idx > 0 else None
    next_id = items[idx + 1].id if idx < len(items) - 1 else None

        

    return render(request, "core/solve.html", {
        "assignment": assignment,
        "ap": ap,
        "prompt": prompt,
        "unit": tpl.unit,
        "attempts_left": attempts_left,
        "feedback": feedback,
        "prev_id": prev_id,
        "next_id": next_id,
        "instance_id": inst.id,
    })
    
    



@login_required
def results(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    items = assignment.items.all()
    total = 0.0
    earned = 0.0

    for ap in items:
        total += ap.points
        inst = ap.probleminstance_set.filter(student=request.user).first()
        if not inst:
            continue
        best = inst.submissions.order_by("-score").first()
        if best:
            earned += best.score

    grade = (earned / total * 100.0) if total > 0 else 0.0
    return render(request, "core/results.html", {"assignment": assignment, "earned": earned, "total": total, "grade": grade})
