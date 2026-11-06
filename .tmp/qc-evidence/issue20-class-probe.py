"""Issue #20: the class whose reduction is the failing one, and its own datum."""
import pickle

from sage_extensions.all import *  # noqa: F401,F403

submonoid_parent = QQ.__dict__.get("_localization_submonoid")
klass = type(submonoid_parent)
reduction = klass.__dict__.get("_reduction", "<inherited>")
print("class:", klass.__name__, flush=True)
print("metaclass:", type(klass).__name__, flush=True)
print("reduction function:", reduction[0] if isinstance(reduction, tuple) else reduction, flush=True)
if isinstance(reduction, tuple):
    for position, argument in enumerate(reduction[1]):
        print(f"  arg[{position}]: {type(argument).__name__} {str(argument)[:80]}", flush=True)
        if isinstance(argument, type):
            inner = argument.__dict__.get("_reduction", "<inherited>")
            print(f"     its _reduction: {str(inner)[:160]}", flush=True)
            print(f"     its metaclass: {type(argument).__name__}", flush=True)
        try:
            pickle.dumps(argument)
            print("     pickles", flush=True)
        except Exception as error:
            print(f"     RAISED {type(error).__name__}: {str(error)[:160]}", flush=True)
print("DONE", flush=True)
