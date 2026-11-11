r"""The coloured-vector transporter returns on three hyperbolic planes (#277).

The transporter of two coloured vector families is computed from a canonical form of the coloured
graph (``coloured_vector_families._transporter`` calls ``canonical_form(..., certificate=True)``),
and a Sage whose Bliss extension was built without ``BLISS_USE_GMP`` against a GMP-enabled
``libbliss`` terminated the interpreter there with SIGSEGV: issue #277, whose minimal reproducer
is ``canonical_form(graphs.CompleteGraph(3), certificate=True)``, exit 139.

A crash leaves no assertion to fail, so what this module measures is that the call returns and
that the witness it returns transports the family: the image of the family under the witness and
the target family are two independently computed sets and must agree.

The lattice is ``Lattices(ZZ)("U")`` summed three times and the family is its six-vector basis
with the coordinates of the first two hyperbolic planes exchanged — the transpose of the
isometry swapping those planes, so a witness exists and is not the identity.
"""

from sage_extensions.all import *


def test_the_coloured_vector_transporter_returns_on_three_hyperbolic_planes() -> None:
    r"""The call returns a witness, and that witness carries the family onto its target.

    The target is the same family with the first two planes' basis vectors exchanged,
    so the witness is the plane swap up to the family's stabilizer; the set the
    witness produces and the target set are computed separately and compared.
    """
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)("U")
    basis = tuple(lattice.module_generators())
    indices = Sets.Δ[5]
    exchange = (1, 0, 3, 2, 4, 5)
    family = Sets().Mor(indices, lattice)(lambda position: basis[int(position)])
    exchanged = Sets().Mor(indices, lattice)(lambda position: basis[exchange[int(position)]])

    witness = lattice.O().transporter(family, exchanged)

    assert witness in lattice.O()
    assert {witness(family(position)) for position in indices} == {
        exchanged(position) for position in indices
    }
