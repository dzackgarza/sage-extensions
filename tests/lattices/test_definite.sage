r"""Definite and small indefinite lattices: minima, isometry classes, orthogonal groups, orbits."""

from sage_extensions.all import *


def test_lll_and_hkz_reduced_bases_begin_with_a_shortest_vector() -> None:
    r"""\(4x^2+2xy+2y^2\) has minimum 2; \(\langle 10,3,1;8,2;6\rangle\) has minimum 6.

    In rank 2 an LLL-reduced basis is Lagrange-reduced, so its first vector is
    shortest; an HKZ-reduced basis begins with a shortest vector in every rank
    (Cohen, *A Course in Computational Algebraic Number Theory*, 2.6).
    Both reductions are changes of basis, so the reduced lattice is isometric
    to the original.  Minima computed by hand (rank 2) and in plain Sage (rank 3).
    """
    binary = Lattices(ZZ)([[4, 1], [1, 2]])
    lll = binary.lll_reduction().reduced
    assert binary.minimum() == 2
    assert lll.module_generators()[0].q() == 2
    assert lll.is_isometric(binary) is True

    ternary = Lattices(ZZ)([[10, 3, 1], [3, 8, 2], [1, 2, 6]])
    hkz = ternary.hkz_reduction().reduced
    assert ternary.minimum() == 6
    assert hkz.module_generators()[0].q() == 6
    assert hkz.is_isometric(ternary) is True


def test_negative_definite_root_lattice_shortest_vectors_are_actual_roots() -> None:
    a2 = Lattices(ZZ)("A2")
    assert a2.is_negative_definite()
    assert a2.minimum() == -2
    shortest = a2.shortest_vectors()
    assert shortest.cardinality() == 6
    assert all(vector.q() == -2 and vector.is_root() for vector in shortest)
    assert a2.kissing_number() == 6


def test_square_lattice_minimum_theta_and_packing_radius() -> None:
    lattice = Lattices(ZZ)(2)
    assert lattice.minimum() == 1
    assert lattice.vectors_of_square(1).cardinality() == 4
    theta = lattice.theta_series(5)
    assert theta[0] == 1
    assert theta[1] == 4
    assert lattice.packing_radius() == QQ(1) / 2
    assert lattice.kissing_number() == 4


def test_the_two_classes_of_discriminant_minus_20_are_separated_by_isometry() -> None:
    r"""Binary forms of discriminant \(-20\): two classes, \(x^2+5y^2\) and \(2x^2+2xy+3y^2\).

    Cox, *Primes of the form x^2+ny^2*, 2.A (\(h(-20)=2\)).  The Gram matrix
    \([[7,3],[3,2]]\) is \([[3,1],[1,2]]\) in the basis \(e_1+e_2, e_2\), so the two
    are isometric; \([[3,1],[1,2]]\) is \(3x^2+2xy+2y^2\sim 2x^2+2xy+3y^2\), the
    non-principal class, so it is not isometric to \(\langle 1\rangle\oplus\langle 5\rangle\).
    """
    lattice = Lattices(ZZ)([[3, 1], [1, 2]])
    reframed = Lattices(ZZ)([[7, 3], [3, 2]])

    witness = reframed.Isom(lattice).an_element()
    for left in reframed.module_generators():
        for right in reframed.module_generators():
            assert reframed.b(left, right) == lattice.b(witness(left), witness(right))
    assert reframed.is_isometric(lattice) is True
    assert lattice.is_isometric(Lattices(ZZ)([[1, 0], [0, 5]])) is False
    assert lattice.is_isometric(Lattices(ZZ)([[1, 0], [0, 1]])) is False


def test_exact_cvp_babai_minima_and_voronoi_geometry_on_square_lattice() -> None:
    lattice = Lattices(ZZ)(2)
    e1, _e2 = lattice.module_generators()
    target = (QQ(3) / 4, QQ(1) / 4)

    assert lattice.closest_vector(target) == e1
    assert lattice.babai(target) == e1
    minima = lattice.successive_minima()
    assert minima.cardinality() == 2
    assert minima[0] == 1
    assert minima[1] == 1
    assert lattice.hadamard_ratio() == 1
    assert lattice.covering_radius() ** 2 == QQ(1) / 2
    assert lattice.center_density() == QQ(1) / 4
    assert lattice.contact_polytope().n_vertices() == 4
    assert lattice.voronoi_relevant_vectors().cardinality() == 4


def test_orthogonal_group_of_a2_has_order_12() -> None:
    r"""\(O(A_2)=W(A_2)\times\{\pm1\}\), of order \(6\cdot 2=12\) (Conway--Sloane, SPLAG 4.6.1)."""
    lattice = Lattices(ZZ)("A2")
    group = lattice.O()

    assert group.order() == 12
    for automorphism in group.group_generators():
        for left in lattice.module_generators():
            for right in lattice.module_generators():
                assert lattice.b(left, right) == lattice.b(
                    automorphism(left), automorphism(right)
                )


def test_indefinite_isometry_ladder_uses_parity_as_an_exact_obstruction() -> None:
    even = Lattices(ZZ)("U")
    odd = Lattices(ZZ)([[1, 0], [0, -1]])

    assert even.signature_pair() == odd.signature_pair() == signature_pair(1, 1)
    assert even.Isom(odd).is_empty() is True
    assert even.is_isometric(odd) is False


def test_indefinite_unimodular_binary_lattices_are_classified_by_parity() -> None:
    r"""Indefinite unimodular lattices are determined by rank, signature and parity.

    Serre, *A Course in Arithmetic*, V.2.2.  \([[2,1],[1,0]]\) is even unimodular of
    signature \((1,1)\), hence \(U\) (explicitly: \(y, x-y\) is a hyperbolic basis);
    \([[1,2],[2,3]]\) is odd unimodular of signature \((1,1)\), hence
    \(\langle 1\rangle\oplus\langle -1\rangle\) (it is that form in the basis \(e_1, 2e_1+e_2\)).
    """
    assert Lattices(ZZ)([[2, 1], [1, 0]]).is_isometric(Lattices(ZZ)("U")) is True
    assert Lattices(ZZ)([[1, 2], [2, 3]]).is_isometric(
        Lattices(ZZ)([[1, 0], [0, -1]])
    ) is True


def test_definite_target_embedding_mor_enumerates_all_a1_into_a2_roots() -> None:
    source = Lattices(ZZ)("A1")
    target = Lattices(ZZ)("A2")
    mor = source.Emb(target)
    embeddings = mor

    assert mor.cardinality() == 6
    source_generator = source.module_generators()[0]
    images = Set(embedding(source_generator) for embedding in embeddings)
    assert images == Set(target.roots())
    assert mor.is_empty() is False
    assert mor.an_element()(source_generator) in images


def test_even_overlattice_inclusions_enumerate_isotropic_glue_for_u2() -> None:
    lattice = Lattices(ZZ)([[0, 2], [2, 0]])
    inclusions = lattice.even_overlattice_inclusions()

    assert inclusions.cardinality() == 3
    assert inclusions.condition_set(lambda inclusion: inclusion.index() == ZZ(1)).cardinality() == 1
    assert inclusions.condition_set(lambda inclusion: inclusion.index() == ZZ(2)).cardinality() == 2
    assert all(inclusion.codomain().is_even() for inclusion in inclusions)
    assert sum(inclusion.codomain().is_unimodular() for inclusion in inclusions) == 2


def test_integral_overlattice_inclusions_are_the_bilinear_isotropic_subgroups() -> None:
    cases = (
        ([[0, 1], [1, 0]], 1),
        ([[2, -1], [-1, 2]], 1),
        ([[16]], 3),
        ([[2, 0], [0, 2]], 2),
        ([[0, 2], [2, 0]], 4),
        ([[2, -1, 0], [-1, 2, -1], [0, -1, 2]], 2),
        ([[2, -1, 0, 0], [-1, 2, -1, -1], [0, -1, 2, 0], [0, -1, 0, 2]], 4),
    )
    for gram, expected in cases:
        lattice = Lattices(ZZ)(gram)
        assert int(lattice.integral_overlattice_inclusions().cardinality()) == expected


def test_nikulin_even_unimodular_embedding_existence_controls_embedding_mor() -> None:
    target = Lattices(ZZ)("U")
    a1 = Lattices(ZZ)("A1")
    a2 = Lattices(ZZ)("A2")
    odd = Lattices(ZZ)([[-1]])

    assert a1.embeds_in_even_unimodular(1, 1)
    assert not a2.embeds_in_even_unimodular(1, 1)
    assert a1.Emb(target).is_empty() is False
    assert a2.Emb(target).is_empty() is True
    assert odd.Emb(target).is_empty() is True


def test_a2_discriminant_representation_is_onto_order_two_and_so_a2_has_order_6() -> None:
    r"""\(D(A_2)\cong\mathbf Z/3\), \(O(q_{A_2})=\{\pm1\}\), and \(-1\in O(A_2)\) maps onto \(-1\).

    \(SO(A_2)\) is the rotation group of the hexagon, of order 6.
    """
    lattice = Lattices(ZZ)("A2")
    automorphisms = lattice.Aut()
    discriminant = lattice.discriminant_group()
    representation = lattice.discriminant_representation()

    for automorphism in automorphisms.group_generators():
        induced = automorphism.discriminant_isometry()
        for generator in discriminant.module_generators():
            assert representation(automorphism)(generator) == induced(generator)

    image = lattice.discriminant_image()
    assert image.cardinality() == discriminant.O().cardinality() == 2
    assert lattice.discriminant_representation_is_surjective()

    stable = lattice.stable_orthogonal_group()
    assert all(
        representation(automorphism) == discriminant.O().one()
        for automorphism in automorphisms
        if automorphism in stable
    )

    special = lattice.SO()
    determinant_one = automorphisms.condition_set(lambda automorphism: automorphism.determinant() == 1)
    assert determinant_one.cardinality() == 6
    assert all(
        (automorphism in special) == (automorphism.determinant() == 1)
        for automorphism in automorphisms
    )


def test_discriminant_group_of_a1_plus_a2_is_cyclic_of_order_6() -> None:
    r"""\(D(L\oplus M)=D(L)\oplus D(M)\), so \(D(A_1\oplus A_2)=\mathbf Z/2\oplus\mathbf Z/3\cong\mathbf Z/6\)."""
    ambient = Lattices(ZZ)("A1") + Lattices(ZZ)("A2")
    discriminant = ambient.discriminant_group()

    assert discriminant.cardinality() == 6
    assert discriminant.is_cyclic()


def test_discriminant_form_of_u_plus_12_has_orthogonal_group_of_order_4() -> None:
    r"""\(D(U\oplus\langle12\rangle)=\mathbf Z/12\) with \(q(x)=1/12 \bmod 2\).

    \(u\in(\mathbf Z/12)^\times\) is an isometry iff \(u^2\equiv1 \bmod 24\), true for all
    four units \(1,5,7,11\); so \(|O(q)|=4\) (hand derivation, checked in plain Sage).
    """
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)([[12]])
    discriminant = lattice.discriminant_group()

    assert discriminant.cardinality() == 12
    assert discriminant.O().order() == 4


def test_primitive_complement_glue_map_is_the_discriminant_anti_isometry() -> None:
    ambient = Lattices(ZZ)("U")
    e, f = ambient.module_generators()
    first = ambient.subobject_on((e + f,))
    second = ambient.subobject_on((e - f,))
    glue = ambient.glue_map(first, second)

    assert first.is_primitive() and second.is_primitive()
    assert first.sum(second).index() == 2
    assert glue.domain().cardinality() == glue.codomain().cardinality() == 2
    for generator in glue.domain().module_generators():
        assert glue.domain().q(generator) == glue.codomain().q(glue(generator))


def test_a_hyperbolic_isometry_of_x2_minus_2y2_has_infinite_order() -> None:
    r"""On \(\langle1\rangle\oplus\langle-2\rangle\), \(e\mapsto3e+2f\), \(f\mapsto4e+3f\) is an isometry
    (\(9-8=1\), \(16-18=-2\), \(12-12=0\)) of trace 6 > 2, so it has infinite order:
    it is multiplication by the unit \(3+2\sqrt2\) of \(\mathbf Z[\sqrt2]\).
    """
    lattice = Lattices(ZZ)([[1, 0], [0, -2]])
    e, f = lattice.module_generators()
    isometry = lattice.Aut()((3 * e + 2 * f, 4 * e + 3 * f))

    assert isometry.determinant() == 1
    assert isometry.cyclic_subgroup().cardinality() == aleph0


def test_norm_one_vectors_of_x2_minus_2y2_form_one_orbit() -> None:
    r"""Solutions of the Pell equation \(x^2-2y^2=1\) are \(\pm(3+2\sqrt2)^n\) and conjugates
    (Niven--Zuckerman--Montgomery 7.8), so \(O(\langle1\rangle\oplus\langle-2\rangle)\) is transitive
    on vectors of square 1.  The stabilizer of \(e\) preserves \(e^\perp=\mathbf Zf\), so it is
    \(\{1, f\mapsto -f\}\), of order 2.
    """
    lattice = Lattices(ZZ)([[1, 0], [0, -2]])
    e, f = lattice.module_generators()
    group = lattice.O()

    assert group.vector_orbit_representatives(1).cardinality() == 1
    witness = group.vector_equivalence_witness(e, 3 * e + 2 * f)
    assert witness(e) == 3 * e + 2 * f
    assert group.subgroup(group.vector_stabilizer_generators(e)).cardinality() == 2


def test_isotropic_lines_of_u_form_one_orbit_under_o_and_two_under_so() -> None:
    r"""\(O(U)=\{\pm1,\pm\sigma\}\) with \(\sigma\) the swap \(e\leftrightarrow f\) (\(\det\sigma=-1\)), so
    \(SO(U)=\{\pm1\}\).  The primitive isotropic lines are \(\mathbf Ze\) and \(\mathbf Zf\):
    exchanged by \(\sigma\), each fixed by \(\pm1\).
    """
    lattice = Lattices(ZZ)("U")

    assert lattice.O().order() == 4
    assert lattice.SO().order() == 2
    assert lattice.O().isotropic_orbit_representatives(1).cardinality() == 1
    special_representatives = lattice.SO().isotropic_orbit_representatives(1)
    assert special_representatives.cardinality() == 2
    assert not lattice.SO().isotropic_are_equivalent(
        special_representatives[0], special_representatives[1]
    )


def test_primitive_isotropic_vectors_of_u_plus_u_form_one_orbit() -> None:
    r"""Eichler criterion: in a lattice containing \(U\oplus U\), the orbit of a primitive
    vector is determined by its square and its class in the discriminant group
    (Gritsenko--Hulek--Sankaran, *Abelianisation of orthogonal groups*, Lemma 3.5).
    \(U\oplus U\) is unimodular, so its primitive isotropic lines form one orbit.
    """
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U")

    assert lattice.isotropic_line_orbit_representatives().cardinality() == 1


def test_positive_cone_character_and_real_spinor_norm_are_independent_computations() -> None:
    lattice = Lattices(ZZ)("U")
    e, f = lattice.module_generators()
    positive_reflection = lattice.reflection(e + f)
    negative_reflection = lattice.reflection(e - f)

    assert positive_reflection.determinant() == -1
    assert negative_reflection.determinant() == -1
    assert positive_reflection.preserves_positive_cone() is False
    assert negative_reflection.preserves_positive_cone() is True
    real_spinor_norm = lattice.spinor_norm(QQ.Mor(RR)(lambda rational: RR(rational)))
    real_square_classes = RR.square_class_group()
    assert real_spinor_norm(positive_reflection) == real_square_classes(-1)
    assert real_spinor_norm(negative_reflection) == real_square_classes(1)

    cone_group = lattice.positive_cone_subgroup()
    o_plus = lattice.O_plus()
    assert negative_reflection in cone_group
    assert positive_reflection not in cone_group
    assert negative_reflection in o_plus
    assert positive_reflection not in o_plus


def test_the_component_character_is_multiplicative_and_cuts_out_the_cone_subgroup() -> None:
    r"""\(\chi_\Omega\) separates the two reflections of \(U\) and is a morphism.

    \(e+f\) and \(e-f\) are orthogonal, so \(s_{e+f}s_{e-f}=-\mathrm{id}\),
    which exchanges the two components of the positive cone.  A character
    that merely recorded the determinant would send that product to the
    identity and fail here.
    """
    lattice = Lattices(ZZ)("U")
    e, f = lattice.module_generators()
    exchanging = lattice.reflection(e + f)
    preserving = lattice.reflection(e - f)
    negation = lattice.O()(lambda label: -lattice.module_generator(label))
    character = lattice.component_character()
    trivial = character.codomain().one()

    assert exchanging * preserving == negation
    assert character(preserving) == trivial
    assert character(exchanging) != trivial
    assert character(negation) == character(exchanging) * character(preserving)
    assert character(negation) != trivial

    cone_group = lattice.positive_cone_subgroup()
    assert preserving in cone_group
    assert exchanging not in cone_group
    assert negation not in cone_group


def test_definite_vector_orbit_equivalence_stabilizer_and_representatives() -> None:
    lattice = Lattices(ZZ)("A2")
    roots = lattice.roots()
    left, right = roots[0], roots[1]
    orthogonal_group = lattice.O()

    witness = orthogonal_group.vector_equivalence_witness(left, right)
    assert witness(left) == right
    assert orthogonal_group.vectors_are_equivalent(left, right)

    stabilizer_generators = orthogonal_group.vector_stabilizer_generators(left)
    assert all(generator(left) == left for generator in stabilizer_generators)
    assert orthogonal_group.subgroup(stabilizer_generators).cardinality() == 2

    representatives = orthogonal_group.vector_orbit_representatives(-2)
    assert representatives.cardinality() == 1
    assert representatives[0].q() == -2
    assert all(
        orthogonal_group.vectors_are_equivalent(root, representatives[0])
        for root in roots
    )


def test_vector_primitive_extension_recovers_index_two_glue_in_u() -> None:
    lattice = Lattices(ZZ)("U")
    e, f = lattice.module_generators()
    extension = lattice.vector_primitive_extension(e + f)

    assert extension.vector.q() == 2
    assert extension.line.module_rank() == extension.complement.module_rank() == 1
    assert extension.sum_lattice.module_rank() == lattice.module_rank() == 2
    assert extension.index == 2
    assert extension.inclusion.index() == 2
    assert extension.gluing_subgroup.cardinality() == 2
    assert extension.gluing_subgroup.is_isotropic()
    assert extension.line_discriminant_inclusion.is_injective()
    assert extension.complement_discriminant_inclusion.is_injective()


def test_definite_complement_extensions_exhaust_the_u_vector_cosets() -> None:
    lattice = Lattices(ZZ)("U")
    e, f = lattice.module_generators()
    vector = e + f

    stabilizer = lattice.definite_complement_extensions(vector, vector)
    opposite_coset = lattice.definite_complement_extensions(vector, -vector)

    assert stabilizer.cardinality() == 2
    assert opposite_coset.cardinality() == 2
    assert all(isometry(vector) == vector for isometry in stabilizer)
    assert all(isometry(vector) == -vector for isometry in opposite_coset)
