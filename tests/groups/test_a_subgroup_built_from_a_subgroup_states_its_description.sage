r"""A subgroup built from a subgroup names that subgroup by its own description.

A construction that builds one subgroup out of another states the words a
timing record prints for the result: the conjugate ``g H g^-1``, the normalizer
``N_G(H)``, the preimage ``rho_L^{-1}(H)``, the discriminant image of a
character kernel.  Those words describe the input, so ``CONTRIBUTING.md``
ENV-03 ("What a name is") takes them from the owner's own public words and
never from a rendering.

The subgroup such a construction operates on has words of its own: the
description its own construction stated
(``Subgroups.ParentMethods.description``).  Its rendering is a different
sentence, ``Subgroup of ...``, which names the pair and says nothing about which
subgroup it is -- two conjugates in one ambient group render alike.  So each
test below writes the expected name out of the operand's own public
description, and the equality is the assertion: the name identifies the
subgroup, and the sentence that renders the operand does not.

The specimens are subgroups of $S_4$, whose constructions state the condition
that cuts each one out, and the discriminant data of
$L = U \oplus U \oplus \langle -2 \rangle$, whose $A_L = Z/2$: the preimage of a
subgroup of $O(A_L)$ and the images of the character quotient.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _symmetric_group_of_four():
    r"""$S_4$: a four-cycle and the subgroups it conjugates."""
    return Groups.S(4)


def _small_lattice():
    r"""$L = U \oplus U \oplus \langle -2 \rangle$: rank five, $A_L = Z/2$."""
    return Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[-2]])


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


def test_a_discriminant_image_names_the_subgroup_it_is_the_image_of_by_its_description() -> None:
    r"""$\rho(\widetilde O(L))$ is named by $\widetilde O(L)$'s description.

    $\widetilde O(L)$ is the full preimage, so its discriminant image is
    $O(A_L)$ itself; the assertions are the name and the subgroup of $O(A_L)$
    the image is one of.
    """
    lattice = _small_lattice()
    stable = lattice.stable_orthogonal_group()
    discriminant_group = lattice.discriminant_group().orthogonal_group()
    image = stable.discriminant_image()

    assert image.description() == (
        "the joint discriminant image of "
        + stable.description()
        + f" in {discriminant_group}"
    )
    assert image.supergroup() is discriminant_group
    assert image.order() == discriminant_group.order()


def test_a_projected_discriminant_image_names_the_intersection_it_projects_by_its_description() -> None:
    r"""A subgroup retaining both sign kernels has its image by projection.

    The intersection of $\widetilde O(L)$, $SO(L)$ and $O^+(L)$ retains the
    discriminant preimage and both sign kernels, so its image is the projection
    of the joint product model rather than the one meet the joint route forms.
    The name is that construction's sentence, formed from the intersection's own
    description, and the image is a subgroup of $O(A_L)$.
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
