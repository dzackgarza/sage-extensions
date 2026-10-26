r"""Signature pairs are pairs of cardinals, including infinite indices."""

from sage_extensions.all import *  # noqa: F401,F403


def test_finite_signature_pair_lives_in_the_signature_pair_category() -> None:
    signatures = signature_pairs()
    pair = signature_pair(3, 19)

    assert pair in signatures


def test_infinite_signature_pair_lives_in_the_signature_pair_category() -> None:
    signatures = signature_pairs()
    pair = signature_pair(aleph0, 0)

    assert pair in signatures


def test_signature_pairs_distinguish_positive_and_negative_indices() -> None:
    assert signature_pair(1, 0) != signature_pair(0, 1)
