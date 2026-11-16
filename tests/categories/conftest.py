r"""Run one arrow-type test's session script in a fresh Sage process.

Sage orders the parent classes of two categories that are not subcategories of
each other by the order in which a session first built them
(``sage/misc/c3_controlled.pyx``), and a fixed Mor's arrow type is generated
from the Mor classes its declared graph holds.  A row that has to see two
construction orders therefore cannot run in one process: by the time the second
order would be asked for, the first has already populated the family's arrow
types.

The test lint admits no import beside the session one in a test file (``TL01``),
so the runner lives here and is bound as a builtin, which is the mechanism the
lint documents for a directory's session abbreviations.
"""

from __future__ import annotations

import builtins
import os
import subprocess
import sys

# The script is not read by the test lint: it is ordinary Python run by a fresh
# interpreter, and it is the only place that may branch on the session order.
_SCRIPT = r"""
import os

from sage_extensions.all import *

differential_graded = DifferentialGradedAlgebras(ZZ)
de_rham = DeRhamAlgebras(ZZ).an_object()
gamma = DividedPowerAlgebras(ZZ)(ZZ.free_module(("x",)))
divided = differential_graded(gamma, lambda element: gamma.zero())

# The de Rham algebra is framed, so its algebra Mor class is ``AlgebraMor``;
# the divided-power algebra is not, so its class is
# ``UnitalMultiplicativeAlgebraMor``.  Both differential graded algebras are
# objects of one category, so their Mors are Mors of one family.
if os.environ["ARROW_TYPE_DE_RHAM_FIRST"] == "1":
    de_rham_mor = differential_graded.Mor(de_rham, de_rham)
    divided_mor = differential_graded.Mor(divided, divided)
    module_mor = Modules(ZZ).Mor(gamma, gamma)
    slice_mor = AugmentedAlgebras(ZZ).Mor(gamma, gamma)
else:
    divided_mor = differential_graded.Mor(divided, divided)
    de_rham_mor = differential_graded.Mor(de_rham, de_rham)
    slice_mor = AugmentedAlgebras(ZZ).Mor(gamma, gamma)
    module_mor = Modules(ZZ).Mor(gamma, gamma)

# Each Mor's arrows are the arrows its own declared graph states: the two
# differential graded algebra Mors differ in the algebra Mor class their
# domains select, and a module Mor and a slice Mor of one algebra are arrows
# of different theories.
assert de_rham_mor.element_class is not divided_mor.element_class
assert module_mor.element_class is not slice_mor.element_class
assert module_mor.identity() in module_mor
"""


def arrow_type_order_run(*, de_rham_first: bool) -> subprocess.CompletedProcess:
    r"""Run the arrow-type session script in a fresh Sage process, in the stated order.

    The completed process carries the exit status and the child's standard
    error, so a row asserting a zero status shows the child's traceback when it
    fails.  The child gets two minutes: every construction in it is a rank-one
    free module or the de Rham algebra on it, and a Mor that does not return in
    that time has not terminated.
    """
    environment = dict(os.environ)
    environment["ARROW_TYPE_DE_RHAM_FIRST"] = "1" if de_rham_first else "0"
    return subprocess.run(
        (sys.executable, "-c", _SCRIPT),
        capture_output=True,
        text=True,
        env=environment,
        timeout=120,
        check=False,
    )


builtins.arrow_type_order_run = arrow_type_order_run
