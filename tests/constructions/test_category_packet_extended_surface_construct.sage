r"""A category packet retains the coordinated mono, epi, iso, and automorphism families."""

from sage_extensions.all import *  # noqa: F401,F403


def test_sets_category_packet_reuses_the_public_mor_families() -> None:
    packet = Sets().category_packet()

    assert packet.Monos() is Sets().MonoCategory()
    assert packet.Epis() is Sets().EpiCategory()
    assert packet.Isos() is Sets().IsoCategory()
    assert packet.Auts() is Sets().AutCategory()


def test_discrete_category_super_packets_are_exactly_declared_packet_supercategories() -> None:
    category = DiscreteCategory(Sets()(("*",)))
    packet = category.category_packet()
    super_packets = packet.super_packets()

    assert all(
        super_packet.category() in category.super_categories()
        for super_packet in super_packets
    )
    assert all(
        super_packet.category().category_packet() is super_packet
        for super_packet in super_packets
    )
