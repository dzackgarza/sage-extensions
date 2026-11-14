"""Exact finite coset actions, sections and Schreier images."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a_transposition_of_s3_has_three_left_and_three_right_cosets() -> None:
    r"""$[S_3 : \langle (1\,2) \rangle] = |S_3|/2 = 6/2 = 3$.

    $S_3$ has $3! = 6$ elements and a transposition has order two, so
    Lagrange's theorem gives three left and three right cosets.
    """
    group = Groups.S(3)
    subgroup = group.subgroup((group((1, 2)),))
    left = group.left_cosets(subgroup)

    assert left.cardinality() == cardinal(3)
    assert left in FiniteGSets(group)
    assert group.one() in left.base_point()
    assert left.projection().codomain() is left
    assert left.is_transitive_action()
    assert group.right_cosets(subgroup).cardinality() == cardinal(3)
    for point in left:
        assert left.coset_of(left.representative_map()(point)) == point
    for first in group:
        for second in group:
            assert left.act(first, left.coset_of(second)) == left.coset_of(first * second)


def test_the_preimage_of_c2_in_c4_has_a_schreier_cover_of_order_two() -> None:
    r"""The identity preimage of $\langle s^2 \rangle$ in $C_4$ has order two.

    The preimage of $\langle s^2 \rangle$ under the identity is
    $\langle s^2 \rangle$ itself, of order two because $s$ has order four, and
    its Schreier images must generate it.
    """
    group = Groups.C(4)
    generator = next(iter(group.group_generators()))
    subgroup = group.subgroup((generator**2,))
    preimage = group.Mor(group).identity().preimage_subgroup(subgroup)
    augmentation = preimage.schreier_generating_morphism()
    images = tuple(augmentation(word) for word in augmentation.domain().group_generators())

    assert all(image in subgroup for image in images)
    assert group.subgroup(images).cardinality() == cardinal(2)


def test_split_four_dimensional_form_cosets_are_its_nonzero_singular_vectors() -> None:
    r"""O^+(4,2) acts transitively on its nine nonzero singular vectors.

    Every expected value is counted from the constructions in the test. The
    Gram matrix $[[0,2],[2,0]]$ has determinant $-4$, so its discriminant group
    has order four; with $q(x_1,x_2) = x_1x_2$ on two isotropic generators,
    two orthogonal copies make $F_2^4$ carrying $q(x) = x_1x_2 + x_3x_4$ --
    $q$ written additively in $F_2$, its values lying in $\tfrac12 Z/Z$, so
    that $q = 1$ means $q = 1/2$ -- and the discriminant form has
    $4 \cdot 4 = 16$ vectors. $q$ vanishes exactly when
    $x_1x_2 = x_3x_4$, and the pair $(x_1,x_2)$ takes a fixed value of
    $x_1x_2$ in $3$ ways when that value is $0$ and $1$ way when it is $1$:
    $3 \cdot 3 + 1 \cdot 1 = 10$ vectors are singular, so nine of them are
    nonzero.

    An isometry is determined by the images of a hyperbolic basis, and every
    choice counted here is realized because the Gram data of a hyperbolic basis
    fix $q$ and $B$ on the span. The first isotropic vector has the nine
    singular nonzero vectors as images. For the second, $v$ with $q(v) = 0$ and
    $B(u,v) = 1$ when $u$ is fixed: the eight $v$ with $B(u,v) = 1$ are paired
    by $v \mapsto v + u$, which sends $q = 0$ to $q = 1$ since
    $q(v + u) = q(v) + q(u) + B(u,v) = q(v) + 1$, so four are singular. The
    orthogonal complement of that pair is again a hyperbolic plane -- the Arf
    invariants of the whole space and of the plane are both $0$ and they add
    modulo two on an orthogonal sum -- so it holds two singular nonzero
    vectors, the choices for the third; the fourth is then forced, since the
    plane holds two $f$ with $B(w,f) = 1$, of which $q(w') = 0$ while
    $q(w + w') = q(w) + q(w') + B(w,w') = 1$. Hence
    $|O(q)| = 9 \cdot 4 \cdot 2 \cdot 1 = 72$, the orbit of a singular vector
    is the nine of them, and orbit-stabilizer leaves $72/9 = 8$ in its
    stabilizer: $|G| = 72$, nine cosets, eight in the stabilizer.
    """
    form = (Lattices(ZZ)([[0, 2], [2, 0]]) ** 2).discriminant_group()
    group = form.orthogonal_group()
    vector = next(iter(form.module_generators()))
    vector_stabilizer = group.stabilizer_of_element(vector)
    stabilizer = group.subgroup_on(tuple(vector_stabilizer.group_generators()))
    cosets = group.left_cosets(stabilizer)
    section = cosets.representative_map()

    assert form.cardinality() == 16
    assert group.cardinality() == 72
    assert stabilizer.cardinality() == 8
    assert cosets.cardinality() == 9
    assert group.orbit_of_element(vector).cardinality() == cosets.cardinality()
    # One coset per singular vector: the section carries the cosets onto the
    # orbit of the distinguished vector, so its images are the nine of them.
    assert set(section(point)(vector) for point in cosets) == set(group.orbit_of_element(vector))
    for point in cosets:
        assert cosets.coset_of(section(point)) == point
        for generator in group.group_generators():
            assert section(cosets.act(generator, point))(vector) == generator(section(point)(vector))
    augmentation = cosets.schreier_generating_morphism()
    images = tuple(augmentation(generator) for generator in augmentation.domain().group_generators())
    assert group.subgroup_on(images).cardinality() == 8


def test_anisotropic_ternary_plane_cosets_are_its_unit_vectors() -> None:
    r"""O(x^2+y^2,F3) has order eight and is transitive on +/-e1, +/-e2.

    Every expected value is counted from the constructions in the test. The
    Gram matrix $[[3,0],[0,3]]$ has determinant $9$, so the discriminant group
    is $(Z/3)^2$ of order nine, carrying $q(x,y) = (x^2+y^2)/3$. Since $-1$ is
    not a square modulo $3$, $q$ vanishes only at the origin, takes $1/3$ on
    $\pm e_1, \pm e_2$ and $2/3$ on $\pm(1,1), \pm(1,2)$.

    An isometry preserves the norm, so it carries the four vectors of norm
    $1/3$ among themselves and the image of $e_1$ has four choices. The image
    of $e_2$ must have norm $1/3$ and be orthogonal to that image, and the
    discriminant bilinear form is $B(x,y) = (x_1y_1 + x_2y_2)/3$, so
    $B(e_1,e_1) = 1/3 \neq 0$ while $B(e_1,e_2) = 0$: it is one of the two
    vectors of the other pair. That is $4 \cdot 2 = 8$ choices, all realized by
    the sign changes and the swap
    $(x,y) \mapsto (\pm x,\pm y), (\pm y,\pm x)$, which leave $x^2+y^2$
    unchanged. So $|G| = 8$, the orbit of $e_1$ is the four unit vectors, the
    stabilizer of $e_1$ is the sign change of the second coordinate, of order
    $2$, and $8/2 = 4$ is the number of cosets.
    """
    form = Lattices(ZZ)([[3, 0], [0, 3]]).discriminant_bilinear_form()
    group = form.orthogonal_group()
    vector = next(iter(form.module_generators()))
    stabilizer = group.subgroup_on(tuple(group.stabilizer_of_element(vector).group_generators()))
    cosets = group.left_cosets(stabilizer)
    section = cosets.representative_map()

    assert form.cardinality() == 9
    assert group.cardinality() == 8
    assert stabilizer.cardinality() == 2
    assert cosets.cardinality() == 4
    assert group.orbit_of_element(vector).cardinality() == cosets.cardinality()
    # One coset per unit vector: the section carries the cosets onto the orbit.
    assert set(section(point)(vector) for point in cosets) == set(group.orbit_of_element(vector))
    for point in cosets:
        assert cosets.coset_of(section(point)) == point
        for generator in group.group_generators():
            assert section(cosets.act(generator, point))(vector) == generator(section(point)(vector))
    augmentation = cosets.schreier_generating_morphism()
    images = tuple(augmentation(generator) for generator in augmentation.domain().group_generators())
    assert group.subgroup_on(images).cardinality() == 2
