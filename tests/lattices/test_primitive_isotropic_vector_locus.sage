from sage_extensions.all import *


def test_primitive_isotropic_orbit_decomposition_retains_representative_stabilizer_and_transporter() -> None:
    lattice = NamedLattices.E10
    group = lattice.O()
    locus = lattice.primitive_isotropic_vectors()
    decomposition = group.orbit_decomposition(locus)

    assert decomposition in Sets()
    assert decomposition.group() is group
    assert decomposition.locus() is locus
    assert decomposition.representatives().cardinality() == 1

    representative = decomposition.representatives()[0]
    assert representative in locus
    assert decomposition.stabilizer(representative).one() == group.one()
    transporter = decomposition.transporter(representative, representative)
    assert transporter(representative) == representative
