"""Issue #20: does the parameterized category pickle as an instance?

The owned class reductions name classes, and pickling a class reaches its
category, whose own class derives from an owned `subcategory_class` that Sage
builds with `picklable=False` (`sage/categories/category.py:1667`).  If the
category pickles as an *instance*, the repair is to reduce owned engine-backed
classes through their category rather than through the classes.
"""
import pickle

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.abstract_categories.arrow_categories import SubobjectCategory

category = SubobjectCategory(Modules(ZZ), ZZ)
print("category:", category, flush=True)
for label, thing in (
    ("category instance", category),
    ("category class", type(category)),
    ("parent_class", category.parent_class),
    ("element_class", category.element_class),
    ("subcategory_class", category.subcategory_class),
):
    try:
        payload = pickle.dumps(thing)
        restored = pickle.loads(payload)
        print(f"-- {label} {type(thing).__name__}: pickles ({len(payload)} bytes), restores to {restored is thing}", flush=True)
    except Exception as error:
        print(f"-- {label} {type(thing).__name__}: RAISED {type(error).__name__}: {str(error)[:120]}", flush=True)
print("DONE", flush=True)
