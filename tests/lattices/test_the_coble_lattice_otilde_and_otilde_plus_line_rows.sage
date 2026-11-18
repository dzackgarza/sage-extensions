r"""The two kernel line rows on the Coble lattice, through the double-coset route.

`T_Co` is built from the cited formula, Dolgachev--Kondo, Izv. Math. 77:3 (2013),
section 3, eq. (3.6), printed p. 513: ``N = <2> + E(2)`` with ``E = U + E8(-1)``.
The two rows exercised here are the kernel rows of that lattice,

* ``Otilde(T_Co) = ker rho``, the call
  ``Tco.stable_orthogonal_group().isotropic_orbit_representatives(1)``;
* ``Otilde+(T_Co) = ker(rho, sn)``, the call
  ``Tco.stable_orthogonal_group().intersection(Tco.O_plus()).isotropic_orbit_representatives(1)``.

Both are the double-coset route of Dutour Sikirić--Hulek,
arXiv:2302.01679v2, lemma 3.6, printed p. 22: the ``Gamma``-orbits inside the one
``O(T_Co)``-orbit of primitive isotropic vectors are the double cosets of the
images of ``O(T_Co)`` and of ``Stab(v)`` under ``rho`` and ``(rho, sn)``, and
the split-signature witness supplies the stabilizer image, so neither row falls
through to the exact integral route.

The count is compared with a quantity computed from the lattice and from the
group containment, not with a page number.  Each representative is a primitive
isotropic line of ``T_Co``; the ``Otilde+`` row has at least as many lines as
``Otilde``, since ``Otilde+ = ker(rho, sn)`` is contained in
``Otilde = ker rho``; and each row's count is the number of nonzero isotropic
classes of ``A_{T_Co}``, counted here on the discriminant form.  That equality
is the ``index 1 over every class'' statement: the subgroup's orbits inside the
single ``O(T_Co)``-orbit are the double cosets of the finite class stabilizer
(Dutour Sikiri\'c--Hulek, Lemma 3.6, printed p. 22), their number is the sum of
the indices over the classes, and every index is a positive integer.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _coble_lattice():
    r"""``T_Co = <2> + (U + E8(-1))(2)``: Dolgachev--Kondo (3.6), p. 513."""
    return NamedLattices.Tco


def _nonzero_isotropic_classes(lattice):
    r"""The nonzero isotropic classes of ``A_{T_Co}``, counted on the discriminant form."""
    form = lattice.discriminant_group()
    zero = form.zero()
    zero_value = form.q(zero)
    nonzero = 0
    for candidate in form.elements():
        if form.q(candidate) == zero_value and candidate != zero:
            nonzero += 1
    return nonzero


def _is_primitive_isotropic_line(lattice, subobject) -> bool:
    r"""Whether ``subobject`` is a rank-one primitive totally isotropic subobject of ``lattice``."""
    if subobject.module_rank() != cardinal(1):
        return False
    if subobject.is_primitive() is not True:
        return False
    for label in subobject.module_generating_set():
        vector = subobject.inclusion()(subobject.module_generator(label))
        if lattice.q(vector) != lattice.base_ring().zero():
            return False
        if lattice.b(vector, vector) != lattice.base_ring().zero():
            return False
    return True


def test_the_coble_lattice_otilde_and_otilde_plus_line_rows() -> None:
    r"""Both kernel rows return primitive isotropic lines, and the Otilde+ row is at least as large."""
    lattice = _coble_lattice()
    ot = tuple(lattice.stable_orthogonal_group().isotropic_orbit_representatives(1))
    otplus = tuple(
        lattice.stable_orthogonal_group()
        .intersection(lattice.O_plus())
        .isotropic_orbit_representatives(1)
    )
    classes = _nonzero_isotropic_classes(lattice)
    assert all(_is_primitive_isotropic_line(lattice, subobject) for subobject in ot)
    assert all(_is_primitive_isotropic_line(lattice, subobject) for subobject in otplus)
    assert sum(1 for _ in otplus) >= sum(1 for _ in ot)
    assert sum(1 for _ in ot) == classes
    assert sum(1 for _ in otplus) == classes
