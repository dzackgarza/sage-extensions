r"""The unipotent radical at Sterk's $P_2$ of $T_{\\mathrm{En}}$: its rank, and the index (#353).

The radical of the setwise stabilizer is
$U_I = \\ker(P_I \\to \\GL(I) \\times O(I^\\perp/I))$, the kernel of the plane stabilizer's
action on the plane and on $P^\\perp/P$.  This file pins what the public calls now decide
there, by comparing computed values:

* every generator returned by `unipotent_radical_generators()` fixes the plane pointwise
  and acts trivially on $P_2^\\perp/P_2$, so it lies in the radical --- computed here on
  the plane's own basis, not taken from the method that selected them (#337 asked whether
  they lie outside it; at $P_2$ they do not), and the kernel's own membership agrees;
* `unipotent_radical_rank()` is $2\\operatorname{rank}(K_I) + 1$ at $P_2$, one dimension of
  it is fixed by the translation map and the other $2\\operatorname{rank}(K_I)$ are
  translations.  That is the block form of #353 written down and computed rather than
  quoted: Dutour Sikirić--Hulek, arXiv:2302.01679v2, Theorem 4.9
  (`theorem_isotropic_k_planes`), printed p. 22, gives the basis $(U \\mid P \\mid K)$;
* the returned family's translations do reach that target, because the family includes
  the block generators of #365 (`unipotent_radical_block_generators()`, one over each
  vector of the parameter lattice `unipotent_parameter_lattice()` and one over the
  centre), so `unipotent_radical_index()` is $1$ and the returned family generates the
  radical.  The fourteen transvections alone do **not**: their translations span $12$ of
  $16$, which is the measurement #353 reported and this file's third test still pins.

So `is_parabolic_complete()` stays `False` at $P_2$, but no longer on the radical
factor: the reason is the Levi pairing, which `parabolic_obstruction()` names.  The
plane-action factor (index $1$ by the $\\Gamma(2)$ certificate) and the quotient factor
(index $1$ by computed orders) are decided, and the radical is now decided too.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _second_representative(lattice):
    r"""Sterk's $P_2$: the plane that does not split off $T_{\\mathrm{En}}$."""
    basis_elements = list(lattice.module_generators())
    first, second, third = basis_elements[0], basis_elements[1], basis_elements[2]
    w = basis_elements[4] + basis_elements[5]
    return lattice.primitive_isotropic_subobject(2 * first + 2 * second + w, third)


def test_every_returned_unipotent_generator_lies_in_the_radical() -> None:
    r"""Each one fixes the plane pointwise and acts trivially on $P_2^\perp/P_2$."""
    lattice = NamedLattices.TEn
    plane = _second_representative(lattice)
    basis = tuple(
        plane.inclusion()(plane.module_generator(label))
        for label in plane.module_generating_set()
    )

    def fixes_pointwise(automorphism):
        return all(automorphism(vector) == vector for vector in basis)

    returned = tuple(plane.unipotent_radical_generators())
    radical = plane.unipotent_radical()
    total = cardinal(sum(1 for _ in returned))

    assert cardinal(sum(1 for generator in returned if fixes_pointwise(generator))) == total
    assert (
        cardinal(
            sum(
                1
                for generator in returned
                if plane.acts_trivially_on_isotropic_reduction(generator)
            )
        )
        == total
    )
    assert cardinal(sum(1 for generator in returned if generator in radical)) == total


def test_the_radical_has_rank_two_rank_k_plus_one() -> None:
    r"""The block form of #353, computed: $17 = 2 \cdot 8 + 1$ at $P_2$, one central dimension.

    `unipotent_radical_rank()` is the dimension of the linear system the block
    conditions define, and `unipotent_translation_kernel_rank()` the same system
    with $N(K) = 0$.  Their difference is the rank of the radical's translation
    image, which the quotient $I^\perp/I$ independently says is
    $2\operatorname{rank}(K_I)$; the third assertion is that agreement rather than
    a restatement of the first.
    """
    plane = _second_representative(NamedLattices.TEn)
    kernel_rank = int(plane.isotropic_reduction().module_rank())

    rank = plane.unipotent_radical_rank()
    centre = plane.unipotent_translation_kernel_rank()

    assert cardinal(rank) == cardinal(2 * kernel_rank + 1)
    assert cardinal(centre) == cardinal(1)
    assert cardinal(rank - centre) == cardinal(2 * kernel_rank)
    assert cardinal(kernel_rank) > cardinal(1)


def test_the_returned_family_reaches_the_radical_translation_rank() -> None:
    r"""The family's translations reach the target, so the radical is generated, and the index is one.

    Two facts are asserted, and they are different: the family's translations span the
    rank the radical's own translation image has
    (`unipotent_translation_rank`, whose target is computed from $I^\perp/I$), and
    `unipotent_radical_index()` is one, which additionally requires the family to meet
    the centre in a generator.  What #353 measured is still true of the transvections
    alone and is asserted as well: their translations fall short, so they alone would
    generate a subgroup of infinite index.
    """
    plane = _second_representative(NamedLattices.TEn)
    translation, target = plane.unipotent_translation_rank()
    basis = tuple(
        plane.inclusion()(plane.module_generator(label))
        for label in plane.module_generating_set()
    )
    transvections = tuple(
        transvection
        for transvection in plane.parabolic_transvection_generators()
        if all(transvection(vector) == vector for vector in basis)
        and plane.acts_trivially_on_isotropic_reduction(transvection)
    )

    assert cardinal(translation) == cardinal(target)
    assert cardinal(target) == cardinal(plane.unipotent_radical_rank() - plane.unipotent_translation_kernel_rank())
    assert cardinal(plane.unipotent_translation_rank(transvections)[0]) < cardinal(target)
    assert plane.unipotent_radical_index() == cardinal(1)
    assert plane.is_parabolic_complete() is False
    assert bool(plane.parabolic_obstruction()) is True
