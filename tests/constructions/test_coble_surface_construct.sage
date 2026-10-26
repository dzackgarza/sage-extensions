r"""The Coble catalogue retains its seventeen cusp vectors and rank-ten Coxeter configuration."""

from sage_extensions.all import *  # noqa: F401,F403


def test_coble_retains_seventeen_isotropic_vectors_and_their_lattice_images() -> None:
    vectors = Coble.isotropic_vectors()
    in_enriques = Coble.isotropic_vectors_in_TEn()
    in_period = Coble.isotropic_vectors_in_TdP()

    assert set(vectors) == set(in_enriques) == set(in_period)
    assert len(vectors) == 17
    assert all(vector.q() == 0 for vector in vectors.values())
    assert all(vector.parent() is NamedLattices.TEn for vector in in_enriques.values())
    assert all(vector.parent() is NamedLattices.TdP for vector in in_period.values())


def test_coble_rank_ten_roots_and_diagram_have_eleven_vertices() -> None:
    lattice, roots = Coble.rank_ten_coxeter_roots()
    diagram = Coble.rank_ten_diagram()

    assert lattice.module_rank() == cardinal(10)
    assert len(roots) == 11
    assert all(root.parent() is lattice for root in roots)
    assert all(root.q() in (-2, -4) for root in roots)
    assert diagram.cardinality() == cardinal(11)
