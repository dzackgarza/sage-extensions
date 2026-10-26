r"""Every complement isometry lifts across an integral orthogonal direct sum.

For L=U(s) perpendicular K(sign*s) and e the first null basis vector,
the integral block map id_U(s) perpendicular g fixes e and induces g on
e-perp/Ze=K(sign*s). This holds for both signs and s=2 as well as s=1; scaling a direct sum
does not create a gluing obstruction. The orders of O(A1), O(A2), O(E8)
are 2, 12, 696729600 (Conway--Sloane, SPLAG, Ch. 4, §6).
"""

import pytest

from sage_extensions.all import *


@pytest.mark.parametrize("name", ("A1", "A2", "E8"))
@pytest.mark.parametrize("scale", (1, 2))
@pytest.mark.parametrize("sign", (1, -1))
def test_every_complement_generator_has_a_pointwise_line_lift(name, scale, sign):
    complement = Lattices(ZZ)(name).twist(sign * scale)
    lattice = NamedLattices.U.twist(scale) + complement
    isotropic = lattice.basis_vector(0)
    reduction = isotropic.isotropic_reduction()
    levi = reduction.levi_action()
    quotient_group = reduction.O()
    family = tuple(quotient_group.group_generators())
    order = {"A1": 2, "A2": 12, "E8": 696729600}[name]

    assert isotropic.q() == 0
    assert isotropic.is_primitive()
    assert reduction.isotropic_embedding()(
        reduction.isotropic_sublattice().module_generators()[0]
    ) == isotropic
    assert reduction.is_isometric(complement) is True
    assert quotient_group.subgroup(family).cardinality() == order
    for generator in family:
        lift = levi.lift(generator)
        assert lift.preserves_form_exactly()
        assert lift.domain() is lattice and lift.codomain() is lattice
        assert lift(isotropic) == isotropic
        assert (~lift)(isotropic) == isotropic
        assert levi(lift) == generator
