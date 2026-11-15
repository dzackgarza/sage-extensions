"""Every distinct frame of the recursion, with how often it appears."""

import collections
import os

from sage_extensions.all import *


def frames(error):
    trail = []
    tb = error.__traceback__
    while tb is not None:
        code = tb.tb_frame.f_code
        trail.append(f"{os.path.basename(code.co_filename)}:{tb.tb_lineno} in {code.co_name}")
        tb = tb.tb_next
    return trail


x = ZZ["x"].algebra_generator("x")
algebra = ZZ["x"].quotient_by_relations([2 * x])
try:
    algebra.is_torsion_free()
except RecursionError as error:
    trail = frames(error)
    print(f"frames: {len(trail)}; distinct: {len(set(trail))}")
    for entry, count in collections.Counter(trail).most_common():
        print(f"  {count:5d}  {entry}")
