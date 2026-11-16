r"""A subgroup built from a subgroup names that subgroup by its own description.

A construction that builds one subgroup out of another -- the conjugate
``g H g^-1``, the image of a subgroup under a morphism, the discriminant image of
a character kernel -- states the words a timing record prints for the result.
Those words describe the input, so ``CONTRIBUTING.md`` ENV-03 ("What a name is")
takes them from the owner's own public words and never from a rendering.

The subgroup such a construction operates on has words of its own: the
description its own construction stated (``Subgroups.ParentMethods.description``).
Its rendering is a different sentence, ``Subgroup of ...``, which names the pair
and says nothing about which subgroup it is.  The containing *whole* group has no
description of that kind -- it is not a subgroup of anything -- so it keeps its
rendering.

The name is also formed where it is read and not where it is written: the
construction retains a function, and asking for the description is what renders
the groups the sentence names (``AGENTS.md``, "Construction is instant").

The first specimens are subgroups of $S_4$: the centralizer of a transposition,
which states the condition cutting it out, and a subgroup given by one
transposition, which states only that.  Neither is normal, so each has a
conjugate that is a different subgroup and a name is formed for it.  The others are the two discriminant images of
$\widetilde O(L)$ for $L = U \oplus U \oplus \langle -2 \rangle$, whose
$A_L = Z/2$: the joint image $\rho(\widetilde O(L)) = O(A_L)$, and the projected
image of the intersection of the discriminant and spinor kernels.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _symmetric_group_of_four():
    r"""$S_4$: a four-cycle and the transposition it conjugates."""
    return Groups.S(4)


def _small_lattice():
    r"""$L = U \oplus U \oplus \langle -2 \rangle$: rank five, $A_L = Z/2$."""
    return Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[-2]])


def test_a_conjugate_names_the_subgroup_it_conjugates_by_that_subgroups_description() -> None:
    r"""$g C_{S_4}((1\,2)) g^{-1}$ is named after the condition cutting it out.

    The centralizer of a transposition states its own description, ``the
    subgroup where g commutes with (1 2)``, and it is not normal: its conjugate
    by a four-cycle is a different subgroup of the same order.  The name is the
    assertion -- the sentence continues with the operand's own description, and
    ``Subgroup of ...``, the rendering the defect printed instead, does not
    appear.
    """
    group = _symmetric_group_of_four()
    centralizer = group.centralizer(group((1, 2)))
    cycle = group((1, 2, 3, 4))
    conjugate = group.conjugate_subgroup(cycle, centralizer)

    assert centralizer.description() == "the subgroup where g commutes with (1 2)"
    assert conjugate.description().startswith(
        "the conjugate of " + centralizer.description() + " by "
    )
    assert "Subgroup of" not in conjugate.description()
    assert conjugate != centralizer
    assert conjugate.order() == centralizer.order()


def test_a_conjugate_of_a_generated_subgroup_names_the_generators_it_was_built_from() -> None:
    r"""The name reads the operand's description whatever that description says.

    A subgroup given by its own generators states that and nothing more, so the
    conjugate of the transposition subgroup $\langle (1\,2)\rangle$ is named
    after it; the conjugate is a different subgroup of order two, the subgroup
    $\langle (2\,3)\rangle$.
    """
    group = _symmetric_group_of_four()
    transposition = group.subgroup((group((1, 2)),))
    cycle = group((1, 2, 3, 4))
    conjugate = group.conjugate_subgroup(cycle, transposition)

    assert transposition.description() == "a subgroup given by its own generators"
    assert conjugate.description().startswith(
        "the conjugate of " + transposition.description() + " by "
    )
    assert "Subgroup of" not in conjugate.description()
    assert conjugate != transposition
    assert conjugate.order() == transposition.order()


def test_a_discriminant_image_names_the_subgroup_it_is_the_image_of_by_its_description() -> None:
    r"""$\rho(\widetilde O(L))$ is named by $\widetilde O(L)$'s description.

    $\widetilde O(L) = \rho_L^{-1}(O(A_L))$ is the full preimage, so its
    discriminant image is $O(A_L)$ itself; the assertions are the name and the
    subgroup of $O(A_L)$ the image is one of.
    """
    lattice = _small_lattice()
    stable = lattice.stable_orthogonal_group()
    discriminant_group = lattice.discriminant_group().O()
    image = stable.discriminant_image()

    assert image.description().startswith(
        "the joint discriminant image of " + stable.description()
    )
    assert image.supergroup() is discriminant_group


def test_a_discriminant_image_of_an_intersection_names_the_intersection_by_its_description() -> None:
    r"""$\rho(\widetilde O(L) \cap O^+(L))$ is named by the intersection that cuts it out.

    An intersection states its own description from its operands' descriptions
    (:meth:`IntersectionSubgroups.ParentMethods.description`), and it is the
    subgroup the image construction operates on: its name is read the same way a
    preimage's is.  This one retains the discriminant preimage and the spinor
    kernel, and the projected construction is the one for a subgroup that
    retains *both* sign kernels, so the joint sentence is what this call states.
    """
    lattice = _small_lattice()
    stable = lattice.stable_orthogonal_group()
    positive = stable.intersection(lattice.O_plus())
    discriminant_group = lattice.discriminant_group().O()
    image = positive.discriminant_image()

    assert positive.description().startswith("the intersection of ")
    assert image.description().startswith(
        "the joint discriminant image of " + positive.description()
    )
    assert image.supergroup() is discriminant_group
