r"""A subgroup built from a subgroup names that subgroup by its own description.

A construction that builds one subgroup out of another states the words a
timing record prints for the result: the conjugate ``g H g^-1``, the normalizer
``N_G(H)``, the preimage ``rho_L^{-1}(H)``, the image ``f(H)``, the stabilizer
``Gamma cap P_I``, the intersection ``B cap Gamma``.  Those words describe the
input, so ``CONTRIBUTING.md`` ENV-03 ("What a name is") takes them from the
owner's own public words and never from a rendering.

The subgroup such a construction operates on has words of its own: the
description its own construction stated
(``Subgroups.ParentMethods.description``).  Its rendering is a different
sentence, ``Subgroup of ...``, which names the pair and says nothing about which
subgroup it is -- two conjugates in one ambient group render alike.  So each
test below writes the expected name out of the operand's own public
description, and the equality is the assertion: the name identifies the
subgroup, and the sentence that renders the operand does not.

Two things are asserted of a name here, because a sentence that is right but
formed while the subgroup is built is the same defect in another shape.
Constructing a subgroup computes nothing for its name (``AGENTS.md``,
"Construction is instant"), so the counting specimens hand the operand a
description that records each time it is asked, and require that building the
subgroup asks it nothing and that reading the name asks it.

The specimens are subgroups of $S_4$ and of $\mathrm{GL}_2(\mathbb Z)$, whose
constructions state the condition cutting each one out, and the discriminant
data of $L = A_2$ and of $U \oplus U \oplus \langle -2 \rangle$, whose
$\widetilde O(L)$ is $\ker\rho_L$: the group whose discriminant image is the
identity.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _symmetric_group_of_four():
    r"""$S_4$: a four-cycle and the subgroups it conjugates."""
    return Groups.S(4)


def _small_lattice():
    r"""$L = U \oplus U \oplus \langle -2 \rangle$: rank five, $A_L = Z/2$."""
    return Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[-2]])


class _CountedWords(str):
    r"""The words of a predicate subgroup's condition, recording each rendering.

    A condition is a string when a construction states it as words, and a
    function of nothing when the construction asks for it at read; this object
    is both, so one specimen measures the two implementations: formatting it
    records the render a construction that formed its sentence would have made,
    and calling it records the read a construction that asks for it makes.
    """

    def __new__(cls, asked, words):
        instance = str.__new__(cls, words)
        instance.asked = asked
        instance.plain = words
        return instance

    def __call__(self):
        self.asked.append(1)
        return self.plain

    def __format__(self, specification):
        self.asked.append(1)
        return str.__format__(self, specification)


def _counting_description(subgroup):
    r"""Give ``subgroup`` a description that records each time it is asked for."""
    asked = []
    stated = subgroup.description

    def description():
        asked.append(1)
        return stated()

    subgroup.description = description
    return asked


def test_a_conjugate_names_the_subgroup_it_conjugates_by_that_subgroups_description() -> None:
    r"""$g C_{S_4}((1\,2)) g^{-1}$ is named after the condition cutting it out.

    The centralizer of a transposition states its own description, and it is
    not normal: its conjugate by a four-cycle is a different subgroup of the
    same order.  The name is the sentence ``the conjugate of <description> by
    <element>``, and it separates the two subgroups.
    """
    group = _symmetric_group_of_four()
    centralizer = group.centralizer(group((1, 2)))
    cycle = group((1, 2, 3, 4))
    conjugate = group.conjugate_subgroup(cycle, centralizer)

    assert centralizer.description() == "the subgroup where g commutes with (1 2)"
    assert conjugate.description() == (
        "the conjugate of " + centralizer.description() + f" by {cycle}"
    )
    assert conjugate.description() != centralizer.description()
    assert conjugate != centralizer
    assert conjugate.order() == centralizer.order()


def test_a_conjugate_of_a_generated_subgroup_names_the_family_it_was_built_from() -> None:
    r"""The name reads the operand's description whatever that description says.

    A subgroup given by its own generators states that and nothing more, so the
    conjugate of $\langle (1\,2)\rangle$ is named after it; the conjugate by a
    four-cycle is the different subgroup $\langle (2\,3)\rangle$ of the same
    order.
    """
    group = _symmetric_group_of_four()
    transposition = group.subgroup((group((1, 2)),))
    cycle = group((1, 2, 3, 4))
    conjugate = group.conjugate_subgroup(cycle, transposition)

    assert transposition.description() == "a subgroup given by its own generators"
    assert conjugate.description() == (
        "the conjugate of " + transposition.description() + f" by {cycle}"
    )
    assert conjugate != transposition
    assert conjugate.order() == transposition.order()


def test_a_normalizer_names_the_subgroup_it_normalizes_by_that_subgroups_description() -> None:
    r"""$N_{S_4}(C_{S_4}((1\,2)))$ is named after the centralizer it stabilizes.

    The normalizer is the setwise stabilizer of the centralizer under
    conjugation, so it is a subgroup built from that subgroup: the name states
    the condition with the centralizer's own description, and the normalizer is
    a strictly larger subgroup than the centralizer it contains.
    """
    group = _symmetric_group_of_four()
    centralizer = group.centralizer(group((1, 2)))
    normalizer = group.normalizer(centralizer)

    assert normalizer.description() == (
        "the subgroup where normalizer of "
        + centralizer.description()
        + f" in {group}"
    )
    swapping = group((1, 3)) * group((2, 4))
    assert normalizer != centralizer
    assert normalizer.is_parent_of(swapping) is True
    assert centralizer.is_parent_of(swapping) is False
    assert normalizer.order() > centralizer.order()


def test_a_preimage_names_the_subgroup_it_is_the_preimage_of_by_its_description() -> None:
    r"""$\widetilde O(L) = \rho_L^{-1}(1)$ is named after the subgroup $1 \le O(A_L)$.

    The stable orthogonal group is the preimage of the trivial subgroup of
    $O(A_L)$, which states that it is given by its own generators; the name is
    the condition ``rho_L(g) lies in <that description>``.
    """
    lattice = _small_lattice()
    stable = lattice.stable_orthogonal_group()
    target = lattice.discriminant_group().orthogonal_group().subgroup_on(())

    assert target.description() == "a subgroup given by its own generators"
    assert target.order() == 1
    assert stable.description() == (
        "the subgroup where rho_L(g) lies in " + target.description()
    )


def test_a_discriminant_image_is_named_by_the_subgroup_it_is_the_image_of() -> None:
    r"""$\rho(\widetilde O(L))$ is named by $\widetilde O(L)$'s description.

    For $L = A_2$ the discriminant group is $\mathbb Z/3$ and its orthogonal
    group has order two, so $O(A_L)$ is bigger than the identity: the
    assertions below separate the trivial image of $\widetilde O(L) = \ker
    \rho_L$ from the whole target that an implementation returning its target
    would give.
    """
    lattice = Lattices(ZZ)("A2")
    stable = lattice.stable_orthogonal_group()
    discriminant_group = lattice.discriminant_group().orthogonal_group()
    image = stable.discriminant_image()

    assert discriminant_group.order() == 2
    assert image.description() == (
        "the joint discriminant image of "
        + stable.description()
        + f" in {discriminant_group}"
    )
    assert image.supergroup() is discriminant_group
    assert image.order() == 1


def test_a_projected_discriminant_image_names_the_intersection_it_projects_by_its_description() -> None:
    r"""A subgroup of $\ker\rho_L$ has its image by projection.

    The intersection of $\widetilde O(L)$, $SO(L)$ and $O^+(L)$ lies inside
    $\widetilde O(L) = \ker\rho_L$, so its discriminant image is the identity,
    and the name is that construction's sentence formed from the intersection's
    own description.
    """
    lattice = _small_lattice()
    stable = lattice.stable_orthogonal_group()
    first = stable.intersection(lattice.SO())
    kernel = first.intersection(lattice.O_plus())
    discriminant_group = lattice.discriminant_group().orthogonal_group()
    image = kernel.finite_character_quotient().discriminant_image()

    assert first.description() == "the intersection of " + " and ".join(
        sorted((stable.description(), lattice.SO().description()))
    )
    assert kernel.description() == "the intersection of " + " and ".join(
        sorted((first.description(), lattice.O_plus().description()))
    )
    assert image.description() == (
        "the projected discriminant image of "
        + kernel.description()
        + f" in {discriminant_group}"
    )
    assert image.supergroup() is discriminant_group
    assert image.order() == 1


def test_building_a_conjugate_asks_the_subgroup_it_conjugates_for_no_description() -> None:
    r"""The conjugate's name is formed when it is read, not when it is built."""
    group = _symmetric_group_of_four()
    centralizer = group.centralizer(group((1, 2)))
    cycle = group((1, 2, 3, 4))
    expected = "the conjugate of " + centralizer.description() + f" by {cycle}"
    asked = _counting_description(centralizer)

    conjugate = group.conjugate_subgroup(cycle, centralizer)

    assert tuple(asked) == ()
    assert conjugate.description() == expected
    assert tuple(asked) == (1,)


def test_building_a_normalizer_asks_the_subgroup_it_normalizes_for_no_description() -> None:
    r"""The normalizer's name is formed when it is read, not when it is built."""
    group = _symmetric_group_of_four()
    centralizer = group.centralizer(group((1, 2)))
    expected = "the subgroup where normalizer of " + centralizer.description() + f" in {group}"
    asked = _counting_description(centralizer)

    normalizer = group.normalizer(centralizer)

    assert tuple(asked) == ()
    assert normalizer.description() == expected
    assert tuple(asked) == (1,)


def test_building_a_preimage_asks_the_subgroup_it_is_the_preimage_of_for_no_description() -> None:
    r"""The preimage's name is formed when it is read, not when it is built."""
    lattice = _small_lattice()
    target = lattice.discriminant_group().orthogonal_group().subgroup_on(())
    representation = lattice.discriminant_representation()
    expected = "the subgroup where rho_L(g) lies in " + target.description()
    asked = _counting_description(target)

    stable = representation.preimage_subgroup(
        target, stated_clause=lambda: "rho_L(g) lies in " + target.description()
    )

    assert tuple(asked) == ()
    assert stable.description() == expected
    assert tuple(asked) == (1,)


def test_an_image_names_the_subgroup_it_is_the_image_of_by_its_description() -> None:
    r"""$f(H)$ is ``the image of <H's description> under <f>``.

    The image of the subgroup $C_4$ generates in $C_4$ is the whole of $C_2$,
    and the name says which subgroup it is the image of: the rendering of that
    subgroup names the pair and not the subgroup.
    """
    four, two = Groups.C(4), Groups.C(2)
    generator = next(iter(four.group_generators()))
    class_of_one = next(iter(two.group_generators()))
    reduction = four.Mor(two)({generator: class_of_one})
    source = four.subgroup((generator,))
    image = source.image_under(reduction)

    assert image.description() == (
        "the image of " + source.description() + f" under {reduction}"
    )
    assert image.supergroup() is two
    assert image.order() == 2


def test_building_an_image_asks_the_subgroup_it_projects_for_no_description() -> None:
    r"""The image's name is formed when it is read, not when it is built."""
    four, two = Groups.C(4), Groups.C(2)
    generator = next(iter(four.group_generators()))
    class_of_one = next(iter(two.group_generators()))
    reduction = four.Mor(two)({generator: class_of_one})
    source = four.subgroup((generator,))
    expected = "the image of " + source.description() + f" under {reduction}"
    asked = _counting_description(source)

    image = source.image_under(reduction)

    assert tuple(asked) == ()
    assert image.description() == expected
    assert tuple(asked) == (1,)


def test_a_cusp_stabilizer_names_the_subobject_it_fixes() -> None:
    r"""$\Gamma \cap P_I$ is named after the representative $I$ it preserves.

    In $\langle 6 \rangle$ the zero sublattice is the unique primitive null
    sublattice, and its stabilizer in $O(\langle 6 \rangle) = \{1, -1\}$ is the
    whole group: the name states the subobject it preserves, and the subgroup
    contains both isometries.
    """
    ambient = Lattices(ZZ)([[6]])
    orthogonal = ambient.O()
    subgroup = orthogonal.predicate_subgroup(
        lambda automorphism: True, lambda: "the whole orthogonal group"
    )
    cusp = next(iter(subgroup.cusps(rank=0)))
    stabilizer = cusp.stabilizer()

    expected = "the subgroup where g preserves " + f"{cusp.representative()}"
    assert stabilizer.description() == expected
    assert stabilizer.order() == 2
    assert all(generator in stabilizer for generator in orthogonal.group_generators())


def test_a_flag_stabilizer_names_the_flag_it_preserves() -> None:
    r"""$\{g \in \mathrm{GL}_2(\mathbb Z) : g(T) = T\}$ is named after the flag $T$.

    The stabilizer of the line $\mathbb Z e_0$ is the upper triangular matrices,
    a proper subgroup of $\mathrm{GL}_2(\mathbb Z)$: it contains the shear
    $e_0 \mapsto e_0$, $e_1 \mapsto e_0 + e_1$ and not the swap.
    """
    points = Sets.Δ[1]
    plane = ZZ.free_module(points)
    first, second = plane.module_generator(points(0)), plane.module_generator(points(1))
    general_linear = plane.general_linear_group()
    flag = FiniteOrderedSets()((plane.subobject_on(Set((first,))),))
    stabilizer = general_linear.flag_stabilizer(flag)
    shear = general_linear({points(0): first, points(1): first + second})
    swap = general_linear({points(0): second, points(1): first})

    expected = "the subgroup where g preserves the flag " + f"{flag} of {plane}"
    assert stabilizer.description() == expected
    assert stabilizer.is_parent_of(shear) is True
    assert stabilizer.is_parent_of(swap) is False


def test_a_restricted_character_intersection_forms_no_sentence_about_the_character_subgroup() -> None:
    r"""$B \cap \Gamma$ is cut out inside $B$ by a condition read, not formed.

    The intersection of a generated subgroup $B$ with the character subgroup
    $\Gamma = \{g : \det g = 1\}$ is cut out inside $B$ by membership in
    $\Gamma$, and that condition names $\Gamma$ when it is read.  Reaching the
    generators forms no sentence about $\Gamma$: its clause is asked only by a
    reader.  (Retaining the two operands in one set does render them, which is
    the set's own act and not this construction's, so the count starts after
    the intersection exists.)

    Every generator the intersection hands out lies in both operands.
    """
    lattice = Lattices(ZZ)([[2, 0], [0, 2]])
    group = lattice.O()
    asked = []
    determinant_one = group.predicate_subgroup(
        lambda automorphism: automorphism.determinant() == 1,
        _CountedWords(asked, "det(g)=1"),
        character_data={"determinant_kernel": True},
        character_data_complete=True,
    )
    generated = group.subgroup((next(iter(group.group_generators())),))

    intersection = group.intersection(determinant_one, generated)
    asked.clear()
    family = tuple(intersection.group_generators())

    assert tuple(asked) == ()
    assert intersection.has_selected_finite_group_generating_set() is True
    assert all(generator in determinant_one for generator in family)
    assert all(generator in generated for generator in family)


def test_an_integral_points_subgroup_states_the_arithmetic_words_its_constructor_gives() -> None:
    r"""$\mathrm{SL}_2(\mathbb Z)$ states the name of the group of points it is.

    $\mathrm{SL}_2(\mathbb Z)$ and $\mathrm{Sp}_2(\mathbb Z)$ are the groups of
    integral points of $\mathrm{SL}_2$ inside $\mathrm{GL}_2(\mathbb Q)$ and of
    $\mathrm{Sp}_2$ inside $\mathrm{GL}_4(\mathbb Q)$, so their constructions
    state the arithmetic name rather than leaving the subgroup the rendering a
    reader cannot tell apart from any other subgroup of the same ambient group.
    """
    special_linear = Groups.SL(2, ZZ)
    symplectic = Groups.Sp(2, ZZ)

    assert special_linear.description() == "SL_2(ZZ)"
    assert symplectic.description() == "Sp_2(ZZ)"
    assert special_linear.is_arithmetic_group() is True
    assert symplectic.is_arithmetic_group() is True
