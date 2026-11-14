r"""Free-word evaluation retains the selected finite basis and multiplication order."""

from sage_extensions.all import *


def test_a_finite_named_free_basis_keeps_its_word_images_and_inverses():
    labels = Sets()(('z', 'a', 'm'))
    source = Groups.Free(index_set=labels)
    z = source.free_generator('z')
    a = source.free_generator('a')
    m = source.free_generator('m')
    target_labels = Sets()(('p', 'q', 'r'))
    target = Groups.Free(index_set=target_labels)
    p = target.free_generator('p')
    q = target.free_generator('q')
    r = target.free_generator('r')
    morphism = source.Mor(target)({'z': q, 'a': ~p, 'm': r})
    word = z * a**2 * ~m * ~z
    assert source.free_basis() is labels
    assert morphism(word) == q * (~p)**2 * ~r * ~q
    assert morphism(~word) * morphism(word) == target.one()
    assert morphism(z * ~z) == target.one()
