import random
import math
import ast
import operator as op

_ALLOWED_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
}

_ALLOWED_FUNCS = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "pi": math.pi,
}

def safe_eval(expr: str, names: dict) -> float:
    def _eval(node):
        if isinstance(node, ast.Num):
            return node.n
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.Name):
            if node.id in names:
                return float(names[node.id])
            if node.id in _ALLOWED_FUNCS:
                return _ALLOWED_FUNCS[node.id]
            raise ValueError("Nombre no permitido")
        if isinstance(node, ast.BinOp):
            return _ALLOWED_OPS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp):
            return _ALLOWED_OPS[type(node.op)](_eval(node.operand))
        if isinstance(node, ast.Call):
            func = _eval(node.func)
            args = [_eval(a) for a in node.args]
            return func(*args)
        raise ValueError("Expresión no permitida")

    tree = ast.parse(expr, mode="eval")
    return float(_eval(tree.body))


def generate_params(schema: dict, seed: int) -> dict:
    rng = random.Random(seed)
    params = {}
    for k, spec in schema.items():
        mn, mx = spec["min"], spec["max"]
        step = spec.get("step", 1)
        values = []
        v = mn
        while v <= mx + 1e-9:
            values.append(v)
            v += step
        params[k] = rng.choice(values)
    return params


def is_within_tolerance(correct: float, submitted: float, tol_abs: float, tol_rel: float) -> bool:
    if abs(submitted - correct) <= tol_abs:
        return True
    if correct != 0 and abs(submitted - correct) / abs(correct) <= tol_rel:
        return True
    return False
