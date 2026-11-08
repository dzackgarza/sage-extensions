r"""Free-word evaluation retains the selected finite basis and multiplication order."""

from sage_extensions.all import *


def test_a_nonlexicographic_free_basis_keeps_its_word_images_and_inverses():
    labels = finite_ordered_set(('z', 'a', 'm'))
    source = Groups.Free(index_set=labels)
    z, a, m = (source.free_generator(label) for label in labels)
    target_labels = finite_ordered_set(('p', 'q', 'r'))
    target = Groups.Free(index_set=target_labels)
    p, q, r = (target.free_generator(label) for label in target_labels)
    morphism = source.Mor(target)({'z': q, 'a': ~p, 'm': r})
    word = z * a**2 * ~m * ~z
    assert source.free_basis() is labels
    assert morphism(word) == q * (~p)**2 * ~r * ~q
    assert morphism(~word) * morphism(word) == target.one()
    assert morphism(z * ~z) == target.one()
