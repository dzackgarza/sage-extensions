from sage_extensions.all import *


def test_isotropic_sublattice_orbit_decomposition_uses_cusp_stabilizers_and_transporters() -> None:
    lattice = NamedLattices.E10
    group = lattice.O()
    locus = lattice.primitive_isotropic_sublattices(rank=1)
    decomposition = group.orbit_decomposition(locus)

    assert decomposition in Sets()
    assert decomposition.group() is group
    assert decomposition.locus() is locus
    assert decomposition.representatives().cardinality() == 1

    representative = decomposition.representatives()[0]
    assert representative in locus
    assert decomposition.stabilizer(representative).one() == group.one()
    transporter = decomposition.transporter(representative, representative)
    image = transporter(representative.inclusion()(representative.basis_vector(0)))
    assert image.parent() is lattice
