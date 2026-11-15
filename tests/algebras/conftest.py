r"""Run one algebra test's session script in a fresh Sage process.

The placement of ``FreeAlgebras.ParentMethods`` and
``AlgebrasWithChosenFinitePresentation.ParentMethods`` in an object's parent
class follows the order in which a session first built the two categories, so a
row that has to see both orders cannot run in one process: by the time the
second order would be asked for, the first has already decided every parent
class it touched.

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

if os.environ["ALGEBRA_TEST_POLYNOMIAL_RING_FIRST"] == "1":
    QQ.polynomial_ring("y")

algebra = AffineSemigroupAlgebras(QQ)(((1, 0), (0, 1)),)
generator = algebra.algebra_generator(
    next(iter(algebra.algebra_generating_set()))
)
assert algebra.presentation_ring() is algebra
assert algebra.relations().index_set().cardinality() == 0
assert algebra.algebra_presentation_morphism().parent() is algebra.Mor(algebra)
assert algebra.lift_to_presentation(generator) == generator
"""


def session_order_verdict(*, polynomial_ring_first: bool) -> int:
    r"""Return the exit status of one fresh session in the requested order.

    ``0`` is that session's assertions holding; anything else is the interpreter
    failing, and the row that asks for it reports the failure as its own.
    """
    environment = dict(os.environ)
    environment["ALGEBRA_TEST_POLYNOMIAL_RING_FIRST"] = (
        "1" if polynomial_ring_first else "0"
    )
    completed = subprocess.run(
        (sys.executable, "-c", _SCRIPT),
        capture_output=True,
        text=True,
        env=environment,
        timeout=600,
        check=False,
    )
    return completed.returncode


builtins.session_order_verdict = session_order_verdict
