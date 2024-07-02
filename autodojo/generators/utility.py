from typing import Callable

from django.db.models import Model


def ensure_unique_name(model_class: Model, view_func: Callable) -> Callable:
    """
    Ninja router's use the view function's name internally.
    As such, different models cannot have the same name for
    their view functions. As a result, we pre-pend the relevant
    model's name to the function.
    """
    view_func.__name__ = f"{model_class._meta.object_name.lower()}_{view_func.__name__}"
    return view_func
