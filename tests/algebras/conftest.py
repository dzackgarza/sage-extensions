r"""Run one algebra test's session script in a fresh Sage process.

Sage orders the parent classes of two categories that are not subcategories of
each other by the order in which a session first built them
(``sage/misc/c3_controlled.pyx``), so a row that has to see two construction
orders cannot run in one process: by the time the second order would be asked
for, the first has already decided every parent class it touched.

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
from sage_extensions.categories.algebras.free_algebras import FramedFreeAlgebraMor

if os.environ["ALGEBRA_TEST_POLYNOMIAL_RING_FIRST"] == "1":
    QQ.polynomial_ring("y")

algebra = AffineSemigroupAlgebras(QQ)(((1, 0), (0, 1)),)
s0, s1 = (algebra.algebra_generator(label) for label in algebra.algebra_generating_set())
endomorphisms = algebra.Mor(algebra)

# The quotient by s0 s1 is presented on the algebra by that one relation.
quotient = algebra.quotient_by_relations((s0 * s1,))
assert quotient.presentation_ring() is algebra
relations = quotient.relations()
assert relations.index_set().cardinality() == 1
assert relations.value(next(iter(relations.index_set()))) == s0 * s1
projection = quotient.algebra_presentation_morphism()
assert projection.domain() is algebra and projection.codomain() is quotient
assert projection(s0) * projection(s1) == quotient.zero()
assert projection(s0) != quotient.zero()
assert projection(s0) ** 2 != quotient.zero()
assert projection(s0) != projection(s1)

# A free algebra's arrows are determined by the images of its generators.
assert algebra._algebra_mor_class() is FramedFreeAlgebraMor, algebra._algebra_mor_class()

# Its identity and the augmentation of its degree-zero resolution are arrows of
# its own Mor.
identity = endomorphisms.identity()
assert identity.parent() is endomorphisms
augmentation = algebra.selected_algebra_resolution().augmentation()
assert augmentation.parent() is endomorphisms, augmentation.parent()
assert augmentation == identity
assert augmentation(s0 * s1) == s0 * s1

# It presents itself: its own generators and no relations.
assert algebra.presentation_ring() is algebra
assert algebra.relations().index_set().cardinality() == 0
assert algebra.algebra_presentation_morphism().parent() is endomorphisms
assert algebra.lift_to_presentation(s0) == s0
"""


def session_order_run(*, polynomial_ring_first: bool) -> subprocess.CompletedProcess:
    r"""Run the session script in a fresh Sage process, in the requested order.

    The completed process carries the exit status and the child's standard
    error, so a row asserting a zero status shows the child's traceback when
    it fails.  The child gets two minutes: every assertion is on a rank-two
    polynomial algebra, and a quotient that does not return in that time has
    not terminated.
    """
    environment = dict(os.environ)
    environment["ALGEBRA_TEST_POLYNOMIAL_RING_FIRST"] = (
        "1" if polynomial_ring_first else "0"
    )
    return subprocess.run(
        (sys.executable, "-c", _SCRIPT),
        capture_output=True,
        text=True,
        env=environment,
        timeout=120,
        check=False,
    )


builtins.session_order_run = session_order_run
