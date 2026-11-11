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
* the returned family's translations fall short of that target, so
  `unipotent_radical_index()` returns `aleph0`: the returned unipotent generators do
  **not** generate the radical at $P_2$, and neither do the generators of
  `parabolic_stabilizer_generators()` that lie in it.

So `is_parabolic_complete()` stays `False` at $P_2$, now on the radical factor itself and
not only on the absence of a citation.  The plane-action factor (index $1$ by the
$\\Gamma(2)$ certificate) and the quotient factor (index $1$ by computed orders) are
decided; the radical is the factor that fails.
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


def test_the_returned_family_has_infinite_index_in_the_radical() -> None:
    r"""The translations fall short of the target, so no finite index exists at $P_2$.

    The index is not refused for want of a citation any more: it is infinite.  The
    obstruction the parabolic reports is a sentence, so what is asserted here is the
    object behind it --- the family's translation rank, the radical's rank, the
    infinite index, and that the parabolic is not complete --- and the sentence is
    only required to exist.
    """
    plane = _second_representative(NamedLattices.TEn)
    translation, target = plane.unipotent_translation_rank()

    assert cardinal(translation) < cardinal(target)
    assert cardinal(target) == cardinal(plane.unipotent_radical_rank() - plane.unipotent_translation_kernel_rank())
    assert plane.unipotent_radical_index() == aleph0
    assert plane.is_parabolic_complete() is False
    assert bool(plane.parabolic_obstruction()) is True
