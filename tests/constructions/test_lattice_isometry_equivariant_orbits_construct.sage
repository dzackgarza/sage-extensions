r"""Identity lattice isometries retain fixed isotropic data and centralizer orbit information."""

from sage_extensions.all import *  # noqa: F401,F403


def test_identity_transports_the_primitive_isotropic_line_of_u_to_itself() -> None:
    lattice = NamedLattices.U
    isotropic = lattice.primitive_isotropic_subobject(lattice.module_generator(0))
    identity = lattice.O().one()

    assert identity.transport_isotropic_object(isotropic) == isotropic


def test_identity_builds_the_one_term_equivariant_isotropic_flag() -> None:
    lattice = NamedLattices.U
    isotropic = lattice.primitive_isotropic_subobject(lattice.module_generator(0))
    identity = lattice.O().one()
    flag = identity.equivariant_flag((isotropic,))

    assert flag.flag_length() == 1
    assert flag.top() is isotropic
    assert identity.equivariant_flag_orbit_decomposition((flag,)) is not None


def test_identity_centralizer_has_one_orbit_on_the_selected_pell_norm_one_vectors() -> None:
    lattice = Lattices(ZZ)([[1, 0], [0, -2]])
    identity = lattice.O().one()
    representatives = identity.equivariant_vector_orbit_representatives(1)

    assert representatives.cardinality() == cardinal(1)
    assert identity.equivariant_vector_orbit_decomposition(1) is not None


def test_identity_sublattice_orbit_decomposition_accepts_a_stable_line() -> None:
    lattice = Lattices(ZZ)("A2")
    identity = lattice.O().one()
    line = lattice.subobject_on((lattice.module_generator(0),))

    assert identity.equivariant_sublattice_orbit_decomposition((line,)) is not None
