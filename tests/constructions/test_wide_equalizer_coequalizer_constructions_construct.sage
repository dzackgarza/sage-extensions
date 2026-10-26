r"""Wide equalizer and coequalizer constructions retain their universal maps on finite sets."""

from sage_extensions.all import *  # noqa: F401,F403


def test_wide_equalizer_construction_retains_the_common_inclusion() -> None:
    source = Sets.Δ[5]
    target = Sets.Δ[2]
    residue = Sets().Mor(source, target)(lambda n: target(int(n) % 3))
    zero = Sets().Mor(source, target)(lambda _n: target(0))
    construction = Sets().equalizer_of_family_construction((residue, zero))
    shape = construction.diagram().domain()
    inclusion = construction.structure_morphism(shape.source())

    assert construction.object().cardinality() == cardinal(2)
    assert {inclusion(point) for point in construction.object()} == {
        source(0),
        source(3),
    }


def test_wide_coequalizer_construction_retains_the_quotient_projection() -> None:
    source = Sets.Δ[1]
    target = Sets.Δ[3]
    initial = Sets().Mor(source, target)(lambda n: target(int(n)))
    successor = Sets().Mor(source, target)(lambda n: target(int(n) + 1))
    construction = Sets().coequalizer_of_family_construction(
        (initial, successor)
    )
    shape = construction.diagram().domain()
    projection = construction.costructure_morphism(shape.target())

    assert construction.object().cardinality() == cardinal(2)
    assert projection(target(0)) == projection(target(1)) == projection(target(2))
    assert projection(target(0)) != projection(target(3))
