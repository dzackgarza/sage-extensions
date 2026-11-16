r"""A transported line keeps the word that placed it, and the composite is its transporter.

A row that transports a representative along its walk holds the element that
did it.  Retaining those elements makes a transporter between two transported
objects a composite of two words -- `g_right * b * ~g_left`, with `b` carrying
the left object's source to the right object's -- instead of an isometry search
whose cost is unrelated to the mathematics.  The composite is an isometry of the
lattice carrying the left line onto the right one, which is what a transporter
between two lines is, and it agrees with the searched ambient witness about
whether one exists.

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


def _generator(line):
    r"""The line's own generator, read in the ambient lattice."""
    domain = line.inclusion().domain()
    return line.inclusion()(domain.module_generator(next(iter(domain.module_generating_set()))))


def _carries(isometry, source, target) -> bool:
    r"""Whether ``isometry`` carries the line ``source`` onto the line ``target``.

    A primitive isotropic line is a rank-one span, so its image is the target
    line exactly when the image of one generator is one of the target's two
    primitive generators.
    """
    image = isometry(_generator(source))
    return image == _generator(target) or image == -_generator(target)


def test_every_transported_line_of_a_kernel_row_keeps_its_word() -> None:
    r"""Each transported representative records an element carrying it there from its source."""
    for subgroup in _kernel_rows():
        quotient = subgroup.finite_character_quotient()
        row = tuple(subgroup.isotropic_orbit_representatives(1))
        assert subgroup.isotropic_orbit_representatives(1).cardinality() == cardinal(3)
        registered = [
            (quotient.isotropic_transport_of(line), line) for line in row
        ]
        # The row's own source is its root: it records no word of its own, and
        # every other representative records one.
        assert sum(1 for record, _line in registered if record is None) == 1
        for record, line in registered:
            if record is None:
                continue
            source, transport = record
            assert _carries(transport, source, line)


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


def test_the_exact_stabilizer_family_is_one_datum_per_span() -> None:
    r"""The retained stabilizer family is the computed one, element for element."""
    for subgroup in _kernel_rows():
        quotient = subgroup.finite_character_quotient()
        representative = next(iter(subgroup.isotropic_orbit_representatives(1)))
        family = quotient.exact_isotropic_stabilizer_family(representative)
        assert tuple(family) == tuple(
            quotient.exact_isotropic_stabilizer_generators(representative)
        )
        assert family
        for generator in family:
            assert _carries(generator, representative, representative)
