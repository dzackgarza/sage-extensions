r"""Hyperbolic lattices and their exact reflection-domain constructions.

For the hyperbolic plane ``U`` with basis ``e,f`` and ``b(e,f)=1``, the vector
``t=e+f`` lies in one component of the positive cone.  Up to sign there is one
root orthogonal to the wall of that component, ``e-f`` of square ``-2``; its
reflection exchanges ``e`` and ``f``.  Thus the Weyl group has order two and
finite index in ``O(U)``, while its one-dimensional chamber is noncompact.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _hyperbolic_plane():
    return HyperbolicLattices(ZZ)(NamedLattices.U)


def _timelike_vector(lattice):
    return lattice.module_generator(0) + lattice.module_generator(1)


def test_hyperbolic_plane_refines_the_lattice_and_selects_a_positive_component() -> None:
    lattice = _hyperbolic_plane()
    timelike = _timelike_vector(lattice)
    component = lattice.positive_cone_component(timelike)
    space = lattice.hyperbolic_space(timelike)
    isotropic = lattice.isotropic_elements_below_height(timelike, 1)
    e, f = lattice.module_generator(0), lattice.module_generator(1)

    assert lattice in HyperbolicLattices(ZZ)
    assert lattice in Lattices(ZZ)
    assert lattice.base_ring() is NamedLattices.U.base_ring() is ZZ
    assert lattice.gram_tensor() == NamedLattices.U.gram_tensor()
    assert lattice.module_rank() == NamedLattices.U.module_rank() == 2
    assert lattice.signature_pair() == signature_pair(1, 1)
    assert isinstance(e, lattice.ElementType)
    assert timelike in component
    assert -timelike not in component
    assert space is not None
    assert lattice.zero() in isotropic
    assert e in isotropic and -e in isotropic
    assert f in isotropic and -f in isotropic


def test_hyperbolic_plane_vinberg_data_has_one_wall_and_weyl_group_of_order_two() -> None:
    lattice = _hyperbolic_plane()
    roots = tuple(lattice.vinberg_algorithm(max_roots=8, max_decompositions=8))
    simple_roots = tuple(lattice.vinberg_simple_roots(max_roots=8, max_decompositions=8))
    diagram = lattice.reflection_coxeter_diagram(max_roots=8, max_decompositions=8)
    reflection_group = lattice.reflection_group(max_roots=8, max_decompositions=8)
    weyl_group = lattice.weyl_group(max_roots=8, max_decompositions=8)
    lengths = lattice.possible_root_lengths()

    assert len(roots) == 1
    assert simple_roots == roots
    assert abs(lattice.b(simple_roots[0], simple_roots[0])) == 2
    assert diagram.cardinality() == cardinal(1)
    assert reflection_group.order() == 2
    assert weyl_group.order() == 2
    assert 2 in lengths
    assert lattice.is_reflective(max_roots=8, max_decompositions=8)
    assert not lattice.is_cocompact(max_roots=8, max_decompositions=8)


def test_hyperbolic_plane_builds_its_chamber_polyhedron_and_weyl_complex() -> None:
    lattice = _hyperbolic_plane()
    timelike = _timelike_vector(lattice)
    chamber = lattice.fundamental_chamber(max_roots=8, max_decompositions=8)
    dominant = lattice.dominant_cone(max_roots=8, max_decompositions=8)
    polyhedron = lattice.coxeter_polyhedron(timelike, max_roots=8, max_decompositions=8)
    complex_ = lattice.chamber_complex(max_roots=8, max_decompositions=8)

    assert chamber is not None
    assert dominant is not None
    assert polyhedron is not None
    assert complex_ is not None


def test_allcock_edgewalk_on_u_recovers_the_same_reflective_wall() -> None:
    lattice = _hyperbolic_plane()
    report = lattice.allcock_edgewalk()
    roots = tuple(lattice.edgewalk_simple_roots())

    assert report is not None
    assert len(roots) == 1
    assert abs(lattice.b(roots[0], roots[0])) == 2
    assert lattice.edgewalk_is_reflective()


def test_hyperbolic_lattice_morphisms_have_identity() -> None:
    lattice = _hyperbolic_plane()
    identity = lattice.Mor(lattice).identity()

    assert identity(lattice.module_generator(0)) == lattice.module_generator(0)
    assert identity * identity == identity
