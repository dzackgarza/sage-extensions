r"""A lattice displays without inventing an ordering; `signature_pair` still needs one.

Research issue 614's display clause: displaying a lattice over a field that is
not the rational field raised ``AssertionError: the signature pair (p, q) needs
a chosen ordering``, because the display computed the signature before deciding
whether it would show it.  The display now shows the invariants it does have --
rank, discriminant, and the Gram matrix -- and leaves the signature to a caller
that has chosen an ordering.

The rational display is unchanged, and ``signature_pair()`` on a lattice whose
fraction field is not represented as ordered still raises.
"""

from sage.all import latex

from sage_extensions.all import GF, Lattices, ZZ


def _finite_field_plane():
    return Lattices(GF(5))([[1, 0], [0, 1]])


def test_a_lattice_over_an_unordered_field_displays_its_available_data() -> None:
    plane = _finite_field_plane()

    text = latex(plane)
    assert "rk}(L) = 2" in text
    assert "disc}(L)" in text
    assert "sig}(L)" not in text
    assert "G_L" in text
    assert repr(plane)


def test_the_signature_pair_still_requires_a_chosen_ordering() -> None:
    plane = _finite_field_plane()

    try:
        plane.signature_pair()
    except AssertionError as error:
        assert "chosen ordering" in str(error)
    else:
        raise AssertionError("signature_pair answered without a chosen ordering")


def test_the_rational_display_keeps_its_signature() -> None:
    plane = Lattices(ZZ)([[0, 1], [1, 0]])

    text = latex(plane)
    assert "sig}(L) = (1, 1)" in text
    assert "disc}(L)" in text
    assert plane.signature_pair() is not None
