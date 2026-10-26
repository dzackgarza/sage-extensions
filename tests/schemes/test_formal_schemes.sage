r"""The formal completion of the affine line at the origin."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_formal_completion_of_a1_at_the_origin_has_functions_qq_power_series_in_t() -> None:
    r"""``Spf QQ[[t]] = colim Spec QQ[t]/(t^n)``: its ``n``-th thickening has length ``n``,
    and ``1 - t`` is a unit of ``QQ[[t]]`` with inverse ``sum t^k`` though not a unit of ``QQ[t]``.

    Derivation: ``QQ[t]/(t^n)`` has ``QQ``-basis ``1, t, ..., t^{n-1}``;
    ``(1 - t)(1 + t + ... + t^{n-1}) = 1 - t^n``.
    """
    R = QQ['t']
    t = R.gen()
    formal = R.formal_spectrum(R.ideal(t))
    functions = formal.global_sections()
    u = functions(1 - t)

    for n in (1, 2, 5):
        assert formal.thickening(n).coordinate_ring().length() == n
    assert u.is_unit()
    assert not (1 - t).is_unit()
    assert (u * functions(1 + t + t**2 + t**3)).truncation(4) == functions.one().truncation(4)
    assert functions.krull_dimension() == 1
    assert functions.is_local()
