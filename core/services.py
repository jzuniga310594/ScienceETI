from django.db import transaction
from .models import ProblemInstance
from .utils import generate_params, safe_eval

def build_seed(user_id: int, assignment_problem_id: int) -> int:
    return (user_id * 1000003) ^ (assignment_problem_id * 9176)

@transaction.atomic
def get_or_create_instance(assignment_problem, student_user):
    inst = ProblemInstance.objects.filter(
        assignment_problem=assignment_problem, student=student_user
    ).first()
    if inst:
        return inst

    tpl = assignment_problem.problem
    seed = build_seed(student_user.id, assignment_problem.id)
    params = generate_params(tpl.params_schema, seed)
    correct = safe_eval(tpl.answer_formula, params)

    inst = ProblemInstance.objects.create(
        assignment_problem=assignment_problem,
        student=student_user,
        params=params,
        correct_answer=correct,
    )
    return inst
