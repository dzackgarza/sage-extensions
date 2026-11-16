r"""A cokernel whose invariants are torsion carries the torsion forms on it.

Membership in ``Modules(R).FinitelyPresented().Torsion()`` is a placement claim
(``CAT-04``), and a cokernel of a presentation is built before it computes, so
it makes no such claim: the question "is this module torsion" is asked of the
predicate ``is_torsion()``, which reads the invariant factors.  A torsion form's
placement is claimed by the construction that knows torsion -- the discriminant
form, the twist functor, the primary part, the orthogonal quotient -- so the
twists, the primary parts and the orthogonal quotients of a discriminant form
exist and stay in the refinement they were claimed in.

Over $Z$, $\langle 3 \rangle$ has discriminant group $Z/3$ with $b = 1/3$, and
$A_1$ has $q = 1/2 \bmod 1$ on $Z/2$.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_one_third_form_on_z3_twists_by_a_negative_unit() -> None:
    r"""Twisting $b(x,x) = 1/3$ by $-1$ gives $-1/3$, on a module that is torsion."""
    form = Lattices(ZZ)([[3]]).discriminant_bilinear_form()
    generator = form.module_generator(0)

    twisted = form.twist(-1)

    assert form.is_torsion()
    assert twisted.b(twisted.module_generator(0), twisted.module_generator(0)) == -(
        form.b(generator, generator)
    )
    assert twisted in FormModules(ZZ).FinitelyPresented().Torsion()


def test_the_half_form_on_z2_has_its_two_primary_part() -> None:
    r"""$q = 1/2 \bmod 1$ on $Z/2$ is the whole of its $2$-primary part."""
    form = Lattices(ZZ)("A1").discriminant_quadratic_form()

    part = form.primary_part(ZZ(2))

    assert part.is_torsion()
    assert part.cardinality() == form.cardinality()
    assert part in FormModules(ZZ).FinitelyPresented().Torsion()


def test_the_orthogonal_quotient_of_a_discriminant_form_is_a_torsion_form() -> None:
    r"""$A_1^{\oplus 4}$'s diagonal subgroup is isotropic, and its orthogonal quotient is formed."""
    discriminant = (Lattices(ZZ)("A1") + Lattices(ZZ)("A1") + Lattices(ZZ)("A1") + Lattices(ZZ)("A1")).discriminant_quadratic_form()
    diagonal = sum(discriminant.smith_form_module_generators(), discriminant.zero())

    quotient = discriminant.orthogonal_quotient(discriminant.subgroup_on((diagonal,)))

    assert quotient.is_torsion()
    assert quotient.cardinality() == ZZ(4)
    assert quotient in FormModules(ZZ).FinitelyPresented().Torsion()
