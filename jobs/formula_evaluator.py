import inspect

from simpleeval import NameNotDefined, SimpleEval


def evaluate_kpi_formula(formula: str, variables: dict) -> float:
    """
    Evalua formulas de indicadores KPI de forma segura.
    Solo permite operaciones aritmeticas sobre variables predefinidas.
    """
    if not formula or not formula.strip():
        return 0.0

    evaluator = SimpleEval()
    evaluator.names = {
        key: (value if value is not None else 0) for key, value in variables.items()
    }

    try:
        result = evaluator.eval(formula)
    except NameNotDefined as exc:
        raise ValueError(f"Variable no definida en la formula: {exc}") from exc
    except Exception as exc:
        raise ValueError(f"Error al evaluar formula: {exc}") from exc

    if result is None:
        return 0.0

    return float(result)


def evaluate_kpi_formula_from_scope(formula: str) -> float:
    """Evalua una formula usando variables en mayusculas del scope llamador."""
    caller_locals = inspect.currentframe().f_back.f_locals
    variables = {
        key: (value if value is not None else 0)
        for key, value in caller_locals.items()
        if isinstance(key, str) and key.isupper() and isinstance(value, (int, float))
    }
    return evaluate_kpi_formula(formula, variables)
