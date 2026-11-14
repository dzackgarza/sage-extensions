"""Issue #20: which class in the reduction chain carries `_reduction = None`.

Pickling QQ's parent walks a chain of dynamic classes, each reducing by
construction (`_reduction`), and the innermost class answers None.  This walks
the chain from the parent's state and names the class, so the repair is aimed at
its builder rather than at pickling.
"""
import pickle

from sage_extensions.all import *  # noqa: F401,F403

SEEN = set()


def walk(label, thing, depth=0):
    indent = "  " * depth
    if isinstance(thing, type):
        reduction = thing.__dict__.get("_reduction", "<inherited>")
        metaclass = type(thing).__name__
        print(f"{indent}{label}: class {thing.__name__} | metaclass {metaclass} | _reduction {str(reduction)[:120]}", flush=True)
        if reduction in (None, "<inherited>"):
            return
        if isinstance(reduction, tuple) and reduction:
            for position, argument in enumerate(reduction[1]):
                walk(f"arg[{position}]", argument, depth + 1)
        return
    if isinstance(thing, (tuple, list)):
        for position, item in enumerate(thing):
            walk(f"{label}[{position}]", item, depth + 1)
        return
    if isinstance(thing, dict):
        for key, value in thing.items():
            walk(f"{label}[{key!r}]", value, depth + 1)
        return
    print(f"{indent}{label}: {type(thing).__name__}", flush=True)


parent = QQ
print("== QQ parent state ==", flush=True)
_reduction = parent.__reduce_ex__(4)
walk("state", _reduction[2] if len(_reduction) > 2 else None)
print("== QQ element class ==", flush=True)
element = QQ(3) / QQ(4)
print("element class:", type(element).__name__, flush=True)
print("element class _reduction:", str(type(element).__dict__.get("_reduction", "<inherited>"))[:200], flush=True)
print("== pickle of the submonoid alone ==", flush=True)
submonoid = parent.__dict__.get("_localization_submonoid")
try:
    pickle.dumps(submonoid)
    print("submonoid pickles", flush=True)
except Exception as error:
    print("submonoid RAISED", type(error).__name__, error, flush=True)
    print("submonoid class:", type(submonoid).__name__, flush=True)
    print("its _reduction:", str(type(submonoid).__dict__.get("_reduction", "<inherited>"))[:300], flush=True)
print("DONE", flush=True)
