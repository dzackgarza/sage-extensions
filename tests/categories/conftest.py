r"""Run one arrow-type session script in a fresh Sage process and read its report.

Sage orders the parent classes of two categories that are not subcategories of
each other by the order in which a session first built them
(``sage/misc/c3_controlled.pyx``), and a fixed Mor's arrow type is generated
from the Mor classes its declared graph holds.  A row that has to see two
construction orders therefore cannot run in one process: by the time the second
order would be asked for, the first has already populated the family's arrow
types.

The test lint admits no import beside the session one in a test file (``TL01``),
so the runner lives here and is bound as a builtin, which is the mechanism the
lint documents for a directory's session abbreviations.  It reports a child's
answer as data, never as prose: the arrow type of each Mor is described by the
providers of its operations (the classes of its MRO), which is what the type is.
"""

from __future__ import annotations

import builtins
import json
import os
import subprocess
import sys

# The script is not read by the test lint: it is ordinary Python run by a fresh
# interpreter, and it is the only place that may branch on the session order.
# It builds the four Mors whose arrow types #550 names and reports, for each,
# the classes whose operations its arrows carry, outermost first.
_SCRIPT = r"""
import json
import os

from sage_extensions.all import *

differential_graded = DifferentialGradedAlgebras(ZZ)
de_rham = DeRhamAlgebras(ZZ).an_object()
generating_module = ZZ.free_module(("x",))
gamma = DividedPowerAlgebras(ZZ)(generating_module)
divided = differential_graded(gamma, lambda element: gamma.zero())

# The de Rham algebra ``Lambda(Q[1], x_0)`` is a framed algebra, so its algebra
# Mor class is ``AlgebraMor``, the class that carries the generator-image
# construction.  The divided-power algebra ``Gamma(Z[x])`` is not framed, so its
# class is ``UnitalMultiplicativeAlgebraMor``.  Both differential graded
# algebras are objects of one category, so their Mors are one family's.
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

arrow_types = {}
algebra_morphism_arrows = {}
for name, mor in (
    ("de_rham", de_rham_mor),
    ("divided_power", divided_mor),
    ("module", module_mor),
    ("slice", slice_mor),
):
    arrow_type = mor.element_class
    arrow_types[name] = [ancestor.__qualname__ for ancestor in arrow_type.__mro__]
    algebra_morphism_arrows[name] = issubclass(arrow_type, AlgebraMor.ElementMethods)
print(json.dumps({"arrow_types": arrow_types, "algebra_morphism_arrows": algebra_morphism_arrows}))
"""


class ArrowTypeRun:
    r"""One session's answer: its exit status, its errors, and its arrow types.

    ``arrow_types`` maps a Mor's name to the qualified names of the classes
    whose operations that Mor's arrows carry, outermost first; two sessions
    whose tuples agree gave that Mor one arrow type, which is how a row reads
    "the same type" across processes.  ``algebra_morphism_arrows`` maps the
    same names to whether that type is one of ``AlgebraMor``'s arrow classes,
    decided in the session by ``issubclass`` against the library's own class.
    Both are ``None`` when the session did not finish, and every row that reads
    them first states that the session finished.
    """

    def __init__(
        self,
        *,
        returncode: int,
        stderr: str,
        arrow_types,
        algebra_morphism_arrows,
    ) -> None:
        self.returncode = returncode
        self.stderr = stderr
        self.arrow_types = arrow_types
        self.algebra_morphism_arrows = algebra_morphism_arrows


_RUNS = {}


def arrow_type_order_run(*, de_rham_first: bool) -> ArrowTypeRun:
    r"""Run the arrow-type session script in a fresh Sage process, in the stated order.

    Each order is run once and remembered, so the rows that read one order
    share a session rather than rebuilding it per assertion.  The runner sets
    no deadline of its own: how long a session may take is the suite's time
    gate to state, and a second clock here would turn a loaded machine into a
    failure of the mathematics.
    """
    remembered = _RUNS.get(de_rham_first)
    if remembered is not None:
        return remembered
    environment = dict(os.environ)
    environment["ARROW_TYPE_DE_RHAM_FIRST"] = "1" if de_rham_first else "0"
    completed = subprocess.run(
        (sys.executable, "-c", _SCRIPT),
        capture_output=True,
        text=True,
        env=environment,
        check=False,
    )
    arrow_types = None
    algebra_morphism_arrows = None
    if completed.returncode == 0:
        report = json.loads(completed.stdout.splitlines()[-1])
        arrow_types = {
            name: tuple(classes)
            for name, classes in report["arrow_types"].items()
        }
        algebra_morphism_arrows = dict(report["algebra_morphism_arrows"])
    run = ArrowTypeRun(
        returncode=completed.returncode,
        stderr=completed.stderr,
        arrow_types=arrow_types,
        algebra_morphism_arrows=algebra_morphism_arrows,
    )
    _RUNS[de_rham_first] = run
    return run


builtins.arrow_type_order_run = arrow_type_order_run
