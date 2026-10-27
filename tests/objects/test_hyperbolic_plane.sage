from sage_extensions.all import *


def hyperbolic_plane():
    return Lattices(ZZ)("U")


def test_the_named_and_the_gram_constructions_agree() -> None:
    assert hyperbolic_plane() == Lattices(ZZ)([[0, 1], [1, 0]])


def test_the_catalogue_entry_agrees() -> None:
    assert hyperbolic_plane() == NamedLattices.U


def test_the_categories_of_u() -> None:
    plane = hyperbolic_plane()
    assert plane in Lattices(ZZ)
    assert plane in EvenLattices(ZZ)
    assert plane in NondegenerateLattices(ZZ)
    assert plane in FormModules(ZZ)
    assert plane in Modules(ZZ)


def test_the_invariants_of_u() -> None:
    r"""$U$ is even unimodular of signature $(1,1)$ with $\det = -1$."""
    plane = hyperbolic_plane()
    e, f = plane.module_generator(0), plane.module_generator(1)
    assert plane.module_rank() == 2
    assert plane.b(e, e) == 0
    assert plane.b(f, f) == 0
    assert plane.b(e, f) == 1
    assert plane.b(e + f, e + f) == 2
    assert plane.determinant() == -1
    assert plane.signature_pair() == signature_pair(1, 1)
    assert plane.is_even()
    assert plane.is_unimodular()
    assert not plane.is_definite()
    assert plane.discriminant_group().cardinality() == 1
    # The actual Lattices(ZZ) object must retain the Nikulin invariant on
    # the even/unimodular join; requiring an explicit category cast masks the
    # method-resolution defect exercised by the Gram constructor.
    assert plane.delta() == 0
    assert plane.is_p_elementary(2)
    assert EvenTwoElementaryLattices(ZZ)(plane).delta() == 0
    assert plane.level() == 1
    assert plane.is_isometric(plane) is True
    assert plane.dual_lattice().is_isometric(plane)


def test_even_unimodular_gram_join_retains_delta_in_rank_twenty_eight() -> None:
    r"""The even-unimodular lattice ``2U + 3E8(-1)`` has trivial discriminant."""
    lattices = Lattices(ZZ)
    lattice = lattices.orthogonal_sum(
        (
            lattices("U"),
            lattices("U"),
            lattices("E8").twist(-1),
            lattices("E8").twist(-1),
            lattices("E8").twist(-1),
        )
    )
    # Exercise the object produced by the actual Gram construction, not an
    # explicit EvenTwoElementaryLattices cast that would hide a lost join.
    gram_lattice = lattices(lattice.gram_tensor())
    assert gram_lattice.module_rank() == 28
    assert gram_lattice.is_even()
    assert gram_lattice.is_unimodular()
    assert gram_lattice.is_p_elementary(2)
    assert gram_lattice.delta() == 0


def test_the_vectors_of_square_minus_two() -> None:
    r"""$b(xe + yf, xe + yf) = 2xy = -2$ exactly for $(x, y) = \pm(1, -1)$."""
    plane = hyperbolic_plane()
    assert plane.vectors_of_square(-2).cardinality() == 2
    assert Lattices(ZZ)("A1").Emb(plane).cardinality() == 2


def test_the_orthogonal_group_of_u() -> None:
    r"""An isometry preserves $xy$, so $O(U) = \{\pm 1, \pm\sigma\}$ with $\sigma$ the swap: the Klein four-group."""
    group = hyperbolic_plane().O()
    assert group.order() == 4
    assert group.is_isomorphic_to(Groups.V4())


def test_the_isotropic_lines_of_u() -> None:
    r"""The primitive isotropic vectors are $\pm e, \pm f$; the swap exchanges $\mathbb Ze$ and $\mathbb Zf$, and only $\pm1$ fix $\mathbb Ze$."""
    plane = hyperbolic_plane()
    line = plane.primitive_isotropic_subobject(plane.module_generator(0))
    assert plane.isotropic_line_orbit_representatives().cardinality() == 1
    assert line.module_rank() == 1
    assert line.is_totally_isotropic()
    assert plane.O().stabilizer(line).order() == 2


def test_the_twist_by_two() -> None:
    r"""$U(2)$ has $\det = -4$ and discriminant group $(\mathbb Z/2)^2$."""
    twisted = hyperbolic_plane().twist(2)
    assert twisted.determinant() == -4
    assert twisted.discriminant_group().cardinality() == 4
    assert twisted.is_p_elementary(2)
    assert twisted.is_isometric(NamedLattices.U_2)


def test_u_has_one_endomorphism_category() -> None:
    plane = hyperbolic_plane()
    endomorphisms = plane.Mor(plane)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert plane.Mor(plane) is endomorphisms
    assert identity * identity == identity
    assert identity.domain() is plane
