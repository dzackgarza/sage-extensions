r"""``O(q)`` of the discriminant form of the Coble lattice, and ``rho_{T_Co}``.

``T_Co = <2> + E8(-2) + U(2)`` (D. Dolgachev and S. Kondo, *Enriques surfaces
II*, Izv. Math. 77:3 (2013), §3, equation (3.6), printed p. 513) is the Coble
lattice of rank 11, and ``L.discriminant_representation()`` needs the orthogonal
group of its discriminant form `A = T_Co^*/T_Co`.  On the tree that filed #323,
reading that group's generating set entered Sage's brute-force isometry search
(``sage.groups.fqf_orthogonal._isom_fqf`` -> ``orbits``) and did not return in
180 s (``.tmp/qc-evidence/issue295-O-q-B2-engine-wall.log``).

The form is not the case that search is written for.  `A` is elementary of rank
11 and `q` takes the half-integer value `1/2` on one Smith generator, so
`\delta = q \bmod \ZZ` is a nonzero linear functional on `A`, and the polar form
`B(x,y) = 2b(x,y)` is a symmetric `\FF_2`-form with `B(x,x) = \delta(x)`.  An
alternating form has even rank, so the polar form of an odd-rank `A` is not
alternating and no GF(2) quadratic matrix carries it.  That is the
characteristic-two odd-rank case of P. J. Cameron, *Classical Groups*, Chapter 6,
§6.2, Theorem 6.1 (printed p. 69), whose proof reads the isometry group off a
symplectic group; the quadratic forms polarising to one symplectic form are its
translates by the linear functionals (pp. 70-71).  The owner
``_engine_two_primary_odd_orthogonal_generators`` splits off the half-integral
direction, hands the integral complement -- an ordinary quadratic space over
`\FF_2` in 10 dimensions, whose polar form is alternating -- to GAP's classical
orthogonal group, and transports its generators back to `A`.  Its docstring
states the reduction and the citations.

Every expected number here is lattice card ``6JRR``'s, read by tag from
``tests/cards/lattice-database-enriques.json``, which
``tests/cards/refresh_lattice_database_enriques.py`` generates from
``dzackgarza/lattice-database`` at database commit
``587d56febe5856d54c6bc9fc023fa5a425f76bfb``.  The card's
``integral.discriminant_form`` block states the order of `O(A, q)`, the number of
isotropic classes and the number of `O(A, q)`-orbits among them, and the card
certifies that block
(``0be391409303d25f25d126795ee881040661b4883ad7473272b34b60b8c414da``).

The research record ``computations/reports/coble_isotropic_orbits.py``
(``dzackgarza/research``, run of 2026-11-05) states the order as
`2^{21} 3^5 5^2 7 17 31` and reports the orbit sizes `[1, 1, 496, 496, 527,
527]` with the two isotropic ones of sizes 1 and 527; the record is the
comparison behind the card, not a second oracle, so nothing here asserts a
number that is not the card's.
"""

from sage_extensions.all import *

CARD_TAG = "6JRR"

#: `T_Co = <2> + E8(-2) + U(2)`, in the basis of Dolgachev--Kondo (3.6): the
#: generator of `<2>`, then the hyperbolic pair with `b(e_1,f_1) = 2`, then the
#: simple roots of `E8(-2)`.
GRAM = (
    (2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    (0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0),
    (0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    (0, 0, 0, -4, 0, 2, 0, 0, 0, 0, 0),
    (0, 0, 0, 0, -4, 0, 2, 0, 0, 0, 0),
    (0, 0, 0, 2, 0, -4, 2, 0, 0, 0, 0),
    (0, 0, 0, 0, 2, 2, -4, 2, 0, 0, 0),
    (0, 0, 0, 0, 0, 0, 2, -4, 2, 0, 0),
    (0, 0, 0, 0, 0, 0, 0, 2, -4, 2, 0),
    (0, 0, 0, 0, 0, 0, 0, 0, 2, -4, 2),
    (0, 0, 0, 0, 0, 0, 0, 0, 0, 2, -4),
)


def _coble_lattice():
    r"""`T_Co` from Dolgachev--Kondo (3.6)."""
    return Lattices(ZZ)([list(row) for row in GRAM])


def _discriminant_form():
    r"""`A_{T_Co} = T_Co^*/T_Co` with its quadratic form."""
    return _coble_lattice().discriminant_quadratic_form()


def _isometry_probes():
    r"""The form, and classes on which its quadratic values determine the whole form.

    `q(x+y) = q(x)+q(y)+2b(x,y)`, so `q` on a basis together with `q` on the
    pairwise sums of basis vectors gives `q` everywhere: it gives `q` on the
    basis and the polar form of every pair.  This is the probe set
    ``TorsionFormIsometry.validate_form_preservation`` uses, and it is a
    complete check rather than a sample.
    """
    form = _discriminant_form()
    basis = tuple(form.module_generator(label) for label in form.module_generating_set())
    return form, basis + tuple(
        left + right
        for index, left in enumerate(basis)
        for right in basis[index + 1 :]
    )


def test_the_lattice_is_the_published_formula_and_its_discriminant_form_is_the_cards() -> None:
    r"""Rank 11, signature `(2,9)`, even, and `|A| = |det|`, as card 6JRR states."""
    record = card("discriminant_forms", CARD_TAG)
    lattice = _coble_lattice()
    form = lattice.discriminant_quadratic_form()
    signature = lattice.signature_pair()

    assert lattice.module_rank() == cardinal(record["rank"])
    assert signature.first() == cardinal(record["signature"][0])
    assert signature.second() == cardinal(record["signature"][1])
    assert lattice.is_even() is True
    assert lattice.determinant() == record["determinant"]
    assert form.cardinality() == cardinal(abs(int(record["determinant"])))
    assert all(invariant == cardinal(2) for invariant in form.invariants())


def test_the_form_is_the_half_integral_odd_rank_case_the_owner_serves() -> None:
    r"""The branch condition, read off the form: one Smith generator has `q = 1/2`.

    An alternating form has even rank, so a rank 11 form whose `q` is not integer
    valued has a non-alternating polar form; that is the case
    ``_engine_two_primary_odd_orthogonal_generators`` serves, and the case the
    integral GF(2) quadratic matrix of the neighbouring branch cannot express.
    """
    record = card("discriminant_forms", CARD_TAG)
    form = _discriminant_form()
    half = form.value_module()(QQ(1) / 2)
    values = tuple(
        form.q(form.module_generator(label)) for label in form.module_generating_set()
    )

    assert form.cardinality() == cardinal(abs(int(record["determinant"])))
    assert all(invariant == cardinal(2) for invariant in form.invariants())
    assert cardinal(sum(1 for value in values if value == half)) > cardinal(0)
    assert cardinal(sum(1 for value in values if value != half)) > cardinal(0)


def test_the_generating_set_of_the_orthogonal_group_states_isometries() -> None:
    r"""Every stated generator preserves `q`, and the stated set generates the group.

    Non-vacuity first: the group has to be bigger than the identity for the
    preservation check to say anything, and a generator has to move a class.
    """
    form, probes = _isometry_probes()
    group = form.orthogonal_group()
    statements = tuple(group.group_generators())

    assert group.cardinality() > cardinal(1)
    assert cardinal(group.subgroup_on(statements).cardinality()) == group.cardinality()
    assert all(
        form.q(statement.forward()(point)) == form.q(point)
        for statement in statements
        for point in probes
    )
    assert any(
        statement.forward()(point) != point
        for statement in statements
        for point in probes
    )


def test_the_order_of_the_orthogonal_group_is_the_cards() -> None:
    r"""``O(A_{T_Co}, q)`` has the order card 6JRR's discriminant-form block states."""
    record = card("discriminant_forms", CARD_TAG)

    assert _discriminant_form().orthogonal_group().cardinality() == cardinal(
        record["orthogonal_group_order"]
    )


def test_the_rank_one_half_integral_form_has_the_trivial_orthogonal_group() -> None:
    r"""`<2>`'s discriminant form is `ZZ/2` with `q(1/2) = 1/2`: only the identity.

    This is the `n = 1` boundary of the owner's branch.  `q` vanishes only at
    zero, so a form-preserving linear map fixes the nonzero class, and the group
    is trivial -- unlike the integral rank-one case, where `q` vanishing on a
    nonzero class leaves room for the sign change.
    """
    form = Lattices(ZZ)([[2]]).discriminant_quadratic_form()
    half = form.value_module()(QQ(1) / 2)

    assert tuple(form.invariants()) == (cardinal(2),)
    assert form.q(form.module_generator(form.module_generating_set()[0])) == half
    assert form.orthogonal_group().cardinality() == cardinal(1)


def test_a_half_integral_two_part_with_isotropic_dual_keeps_the_general_route() -> None:
    r"""`diag(6,6)`'s 2-primary part has `delta(B^-1 delta) = 0`, which is not this branch.

    There `q = 3/2` on both Smith generators and `B = 2b` is the identity, so the
    `B`-dual of `delta = (1,1)` is `(1,1)` itself: it is isotropic, `ker delta`
    is its own orthogonal complement, and `B` restricted to `ker delta` is
    degenerate.  The odd-rank split does not apply, the owner must keep Sage's
    general route for that part, and that route's answer has to stay a genuine
    isometry group -- this is the regression the branch's second precondition
    exists for.
    """
    form = Lattices(ZZ)([[6, 0], [0, 6]]).discriminant_quadratic_form()
    group = form.orthogonal_group()
    statements = tuple(group.group_generators())
    basis = tuple(form.module_generator(label) for label in form.module_generating_set())
    probes = basis + tuple(
        left + right for index, left in enumerate(basis) for right in basis[index + 1 :]
    )

    assert group.cardinality() > cardinal(1)
    assert all(
        form.q(statement.forward()(point)) == form.q(point)
        for statement in statements
        for point in probes
    )


def test_discriminant_representation_of_the_coble_lattice_returns_on_an_isometry() -> None:
    r"""`rho_{T_Co}` returns its morphism, and a real isometry of `T_Co` lands in `O(q)`."""
    record = card("discriminant_forms", CARD_TAG)
    lattice = _coble_lattice()
    rho = lattice.discriminant_representation()
    target = rho.codomain()
    labels = tuple(lattice.module_generating_set())
    negation = lattice.Aut()(
        {label: -lattice.module_generator(label) for label in labels}
    )

    assert target.invariant_form() is lattice.discriminant_quadratic_form()
    assert target.cardinality() == cardinal(record["orthogonal_group_order"])
    assert rho(lattice.Aut().one()) == target.one()
    assert rho(negation) in target
