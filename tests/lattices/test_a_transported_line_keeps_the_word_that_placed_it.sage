r"""A transported object keeps the word that placed it, and the composite carries its root there.

A row that transports a representative along its walk holds the element that
did it.  Retaining those elements makes a transporter between two transported
objects a composite of two words -- `g_right * b * ~g_left`, with `b` carrying
the left object's source to the right object's -- instead of an isometry search
whose cost is unrelated to the mathematics.  The composite is an isometry of the
lattice carrying the left object onto the right one, which is what a transporter
between two isotropic subobjects is, and it agrees with the searched ambient
witness about whether one exists.

A chain of two steps composes in the order its steps act: for
`root -- step --> current -- g --> subobject` the composite is `g * step`.  A
step recorded over an already transported object has exactly the shape the
incidence records -- the word carrying an ambient flag's line, then the word
carrying that line onto the flag's transported line -- so the two steps here
are recorded the way the rows record them.

The specimens are the smallest rows that have more than one line cusp:
`U + U(2) + <-2>` under `ker rho` and under `ker(rho, sn_RR)`, whose line rows
have three cusps each (no printed card states these rows; nothing here is
compared with a count from the lattice database).
"""

from sage_extensions.all import *  # noqa: F401,F403


def _u_u2_m2():
    r"""``U + U(2) + <-2>``: the kernel rows have three line cusps of their own."""
    return (
        Lattices(ZZ)("U")
        + Lattices(ZZ)(((0, 2), (2, 0)))
        + Lattices(ZZ)(((-2,),))
    )


def _kernel_rows():
    r"""``ker rho`` and ``ker(rho, sn_RR)`` of ``U + U(2) + <-2>``."""
    lattice = _u_u2_m2()
    stable = lattice.stable_orthogonal_group()
    return (stable, stable.intersection(lattice.O_plus()))


def _lies_in(inclusion, target) -> bool:
    r"""Whether the image of the subobject inclusion ``inclusion`` lies in that of ``target``."""
    domain = inclusion.domain()
    return all(
        target.is_in_image(inclusion(domain.module_generator(label)))
        for label in domain.module_generating_set()
    )


def _spans_agree(left, right) -> bool:
    r"""Whether two isotropic subobjects of one lattice span the same sublattice."""
    if left.inclusion().codomain() is not right.inclusion().codomain():
        return False
    return _lies_in(left.inclusion(), right.inclusion()) and _lies_in(
        right.inclusion(), left.inclusion()
    )


def _carries(isometry, source, target) -> bool:
    r"""Whether ``isometry`` carries the isotropic subobject ``source`` onto the span of ``target``.

    A question the library answers with no element at all -- no transporter
    exists, or the composite of the recorded words is not exhibited -- is no
    transporter, so ``None`` carries nothing.
    """
    if isometry is None:
        return False
    return _spans_agree(isometry.transport_isotropic_object(source), target)


def test_every_transported_line_of_a_kernel_row_keeps_its_word() -> None:
    r"""Each transported representative is carried from its chain's root by a recorded word."""
    for subgroup in _kernel_rows():
        quotient = subgroup.finite_character_quotient()
        row = tuple(subgroup.isotropic_orbit_representatives(1))
        assert subgroup.isotropic_orbit_representatives(1).cardinality() == cardinal(3)
        recorded = [
            (quotient.isotropic_transport_of(line) is not None, line) for line in row
        ]
        # The row's own source is its root: it records no word of its own, and
        # every other representative records one.
        assert sum(1 for has_word, _line in recorded if not has_word) == 1
        for has_word, line in recorded:
            if not has_word:
                continue
            root, transport = quotient.transported_from_root(line)
            assert _carries(transport, root, line)


def test_a_chain_of_two_recorded_words_composes_in_the_order_its_steps_act() -> None:
    r"""A step recorded over a transported object composes after it, not before it.

    A row records each cusp it transports with the word carrying that cusp from
    the row's root, and a step recorded over such an object is the second step
    of one chain -- the shape the incidence's registrations have when the word
    carrying an ambient flag's line is followed by the word carrying that line
    onto the flag's transported line.  Reading the chain at the far end
    multiplies the second step by the first, in that order: the first step
    acts first, on the root, and the second step acts on its image.  Both
    words here carry one cusp onto a different one, so both act, and only
    their product in the order they act carries the chain's root onto the
    endpoint.
    """
    for subgroup in _kernel_rows():
        quotient = subgroup.finite_character_quotient()
        row = tuple(subgroup.isotropic_orbit_representatives(1))
        words = [
            (left, right, quotient.isotropic_transport_between(left, right))
            for position, left in enumerate(row)
            for right in row[position + 1:]
        ]
        # Two cusps of one ambient O(L) orbit: the words' own composite exists
        # there, and no other pair of this row's cusps is joined by one.
        first, second, step = next(
            (left, right, word)
            for left, right, word in words
            if _carries(word, left, right)
        )
        # The second step starts where the first one ends: another line of that
        # orbit, the image of the second cusp under an element of the subgroup
        # that fixes the first -- the same shape as the incidence's second
        # registration, a word recorded over an already transported object.
        third = next(
            image
            for image in (
                element.transport_isotropic_object(second)
                for element in quotient.exact_isotropic_stabilizer_generators(first)
            )
            if not _spans_agree(image, second) and not _spans_agree(image, first)
        )
        onward = quotient.isotropic_transport_between(second, third)
        assert _carries(onward, second, third)
        quotient.register_isotropic_transport(second, first, step)
        quotient.register_isotropic_transport(third, second, onward)
        chain_root, composite = quotient.transported_from_root(third)
        assert _spans_agree(chain_root, first)
        assert _carries(composite, first, third)


def test_the_composite_of_two_words_is_a_transporter() -> None:
    r"""The words' composite exists exactly where an ambient transporter does, and is one."""
    for subgroup in _kernel_rows():
        quotient = subgroup.finite_character_quotient()
        row = tuple(subgroup.isotropic_orbit_representatives(1))
        for position, left in enumerate(row):
            for right in row[position + 1:]:
                composite = quotient.isotropic_transport_between(left, right)
                # Two lines of different O(L)-orbits have no transporter at all,
                # and no composite of words invents one.
                ambient = subgroup.supergroup().isotropic_equivalence_witness(left, right)
                assert (composite is None) == (ambient is None)
                if composite is None:
                    continue
                assert _carries(composite, left, right)


def test_the_exact_stabilizer_is_one_datum_for_each_span() -> None:
    r"""The stabilizer family is read by span: one datum per span, and each span its own.

    The family depends on the representative through the span of its terms, so
    an equal-but-distinct copy of a representative reads the datum already
    computed for its span, while a second span is a different datum: the family
    returned for it stabilizes *it*.  A family retained without its span would
    be returned for the second span too and would move it, which is what the
    stabilizer assertion below refuses.  A kernel row of this lattice has three
    line cusps, so two of them are two spans of one quotient.
    """
    for subgroup in _kernel_rows():
        quotient = subgroup.finite_character_quotient()
        row = tuple(subgroup.isotropic_orbit_representatives(1))
        first, second = row[0], row[1]
        family = quotient.exact_isotropic_stabilizer_generators(first)
        assert family
        for generator in family:
            assert _carries(generator, first, first)
        # The same span, from a second construction of it.
        copy = subgroup.supergroup().one().transport_isotropic_object(first)
        assert _spans_agree(copy, first)
        assert quotient.exact_isotropic_stabilizer_generators(copy) is family
        other = quotient.exact_isotropic_stabilizer_generators(second)
        assert other is not family
        for generator in other:
            assert _carries(generator, second, second)


def test_transported_line_stabilizer_is_the_exact_conjugate() -> None:
    r"""A split line's complete stabilizer family is transported from its root."""
    for subgroup in _kernel_rows():
        quotient = subgroup.finite_character_quotient()
        row = tuple(subgroup.isotropic_orbit_representatives(1))
        transported = [line for line in row
                       if quotient.isotropic_transport_of(line) is not None]
        assert transported
        for line in transported:
            root, move = quotient.transported_from_root(line)
            assert not _spans_agree(root, line)
            root_family = quotient.exact_isotropic_stabilizer_generators(root)
            family = quotient.exact_isotropic_stabilizer_generators(line)
            assert tuple(move * g * ~move for g in root_family) == family
            assert all(_carries(g, line, line) for g in family)
