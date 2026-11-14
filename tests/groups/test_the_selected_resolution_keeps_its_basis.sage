r"""A selected group resolution keeps the basis its epimorphism was built on.

``_group_generating_epimorphism`` forms the free group ``F(S)`` on a generator
label set ``S`` and the epimorphism ``F(S) ->> G`` induced by a map ``S -> G``.
The free-group constructor refuses a source whose basis is a *different* set
from the supplied labels, so the identification of ``S`` with the free basis is
construction data, not a convention: a resolution that retained a copy of the
label set, or rebuilt ``F(S)`` on one, would no longer be the resolution its
augmentation was built for.  Issue #1 records the failure that produced:
``_group_generating_epimorphism`` handed the chosen-generator map to a
constructor that rejected its source as distinct from the selected free basis,
and every coset consumer died there.

So these tests read the identity, not merely the images: the retained generator
set *is* the free basis of the augmentation's source, the retained generator map
*is* the map the augmentation evaluates, and the augmentation's image is the
whole target.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_a_named_group_resolution_keeps_its_generator_basis():
    group = Groups.S(3)
    resolution = group.selected_group_resolution()
    labels = resolution.generating_set()
    augmentation = resolution.augmentation()
    generator_morphism = resolution.generator_morphism()

    assert resolution.level(0) is augmentation.domain()
    assert augmentation.domain().free_basis() is labels
    assert generator_morphism.domain() is labels
    assert generator_morphism.codomain() is group
    assert augmentation.generator_morphism() is generator_morphism
    for label in labels:
        assert augmentation(augmentation.domain().free_generator(label)) == generator_morphism(label)
    assert augmentation.codomain() is group
    assert augmentation.image().cardinality() == group.cardinality()


def test_a_generated_subgroup_resolution_keeps_the_generators_it_was_given():
    group = Groups.S(3)
    transposition = group((1, 2))
    subgroup = group.subgroup((transposition,))
    resolution = subgroup.selected_group_resolution()
    labels = resolution.generating_set()
    augmentation = resolution.augmentation()
    generator_morphism = resolution.generator_morphism()

    assert augmentation.domain().free_basis() is labels
    assert generator_morphism.domain() is labels
    assert generator_morphism.codomain() is subgroup
    assert augmentation.generator_morphism() is generator_morphism
    for label in labels:
        assert augmentation(augmentation.domain().free_generator(label)) == subgroup(label)
    assert augmentation.image().cardinality() == subgroup.cardinality()
