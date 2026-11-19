r"""Every isometry of `K_I` congruent to the identity at the divisibility lifts.

**The lemma.**  Let `L` be an integral lattice over `ZZ`, `v` a primitive
isotropic vector of divisibility `d`, `J = v^perp`, `w` a partner with
`b(v,w) = d` (so `L = J + Z w`), and `J = Z v + K'` with `K'` the lifts
`kappa_i` of `K_I`'s frame -- an orthogonal decomposition, since `v` is
orthogonal to `J`.  For `tau` in `O(K_I)`, let `tau^sharp` act on `J` by
fixing `v` and by `tau` on `K'`.  If `tau` is congruent to the identity modulo
`d`, then

    g(v) = v,    g(kappa_i) = tau^sharp(kappa_i) + c_i v,
    g(w) = w,    c_i = b(w, kappa_i - tau^sharp(kappa_i)) / d

is an integral isometry of `L` with `g(v) = v` and `lambda(g) = tau`.

**Proof.**  `c_i` is an integer because `kappa_i - tau^sharp(kappa_i)` lies in
`d J` and `b(w, J)` lies in `ZZ`.  `g` is `ZZ`-linear on the basis
`(v, kappa_i, w)` of `L`, so it is integral; and it preserves the pairings of
that basis: `(v,v)`, `(v,kappa_i)` and `(v,w)` because `tau^sharp` fixes `v`
and `b(v, J) = 0`; `(kappa_i,kappa_j)` because `tau^sharp` is an isometry of
`J`; `(w,w)` because `w` is fixed; and

    b(g kappa_i, g w) = b(tau^sharp kappa_i, w) + c_i d = b(kappa_i, w)

by the definition of `c_i` and the symmetry of `b`.  So `g` is an isometry of
`L` acting as `tau` on `J / Z v`, and `Gamma_{K_I}(d)` lies in the Levi image.

No source is quoted: the proof is that computation on the basis.  What the
lemma buys is the index bound `[O(K_I) : M_I] <= |GL_r(ZZ/d)|`, hence a finite
coset graph, and a lift written down rather than searched for.

The specimens are Gram matrices, each asserted for the property that makes it
the specimen it is: `b(w, kappa_i)` vanishes on the divisibility-two lines
`U(2) + <2>` and `U(2) + <3>`, and equals one on the rank-five proper-image
lattice, whose `K_I` has rank three and discriminant eight -- the case where
the formula's correction term does not vanish.
"""

from sage_extensions.all import *  # noqa: F401,F403

DIVISIBILITY_TWO = [[0, 2, 0], [2, 0, 0], [0, 0, 2]]
ODD_DIVISIBILITY_TWO = [[0, 2, 0], [2, 0, 0], [0, 0, 3]]
RANK_FIVE = [
    [0, 2, 0, 0, 0],
    [2, 0, 1, 0, 0],
    [0, 1, 0, 2, 0],
    [0, 0, 2, 0, 0],
    [0, 0, 0, 0, -2],
]


def _coordinates_of(quotient, labels, isometry):
    r"""The coordinates of the images of `K_I`'s frame under ``isometry``, row by row."""
    rows = []
    for label in labels:
        coordinates = isometry(quotient.module_generator(label)).to_vector()
        rows.append([int(coordinates(other)) for other in labels])
    return rows


def _is_congruent(quotient, labels, isometry, modulus):
    r"""Whether ``isometry`` acts as the identity on the frame modulo ``modulus``."""
    return all(
        (entry - (1 if position == column else 0)) % modulus == 0
        for position, row in enumerate(_coordinates_of(quotient, labels, isometry))
        for column, entry in enumerate(row)
    )


def _assert_the_congruence_lifts(gram) -> None:
    r"""Congruent generators lift, and the lemma's own formula is an isometry there."""
    lattice = Lattices(ZZ)(gram)
    module_labels = tuple(lattice.module_generating_set())
    vector = lattice.module_generator(module_labels[0])
    partner = lattice.module_generator(module_labels[1])
    subobject = lattice.primitive_isotropic_subobject(vector)
    reduction = subobject.isotropic_reduction()
    quotient = reduction.quotient_lattice()
    labels = tuple(quotient.module_generating_set())
    frame = subobject.quotient_frame_lifts()
    kappas = tuple(frame[label] for label in labels)
    modulus = int(vector.div())
    rank = int(lattice.module_rank())

    assert vector.q() == ZZ(0)
    assert vector.is_primitive() is True
    assert lattice.b(vector, partner) == ZZ(modulus)
    assert lattice.b(vector, partner) == ZZ(modulus) * (lattice.b(vector, vector) + 1)

    congruent = tuple(
        generator
        for generator in tuple(quotient.O().group_generators())
        if _is_congruent(quotient, labels, generator, modulus)
    )
    assert congruent

    for generator in congruent:
        lift = reduction.pointwise_levi_lift(generator)
        assert lift(vector) == vector
        assert reduction.levi_action()(lift) == generator

        coordinates = _coordinates_of(quotient, labels, generator)
        images = []
        for position, label in enumerate(labels):
            combination = sum(
                (
                    lattice.scalar_multiple(
                        lattice.base_ring()(row[position]), kappa
                    )
                    for row, kappa in zip(coordinates, kappas, strict=True)
                    if row[position]
                ),
                lattice.zero(),
            )
            correction = int(lattice.b(partner, kappas[position] - combination))
            assert correction % modulus == 0
            images.append(
                combination
                + lattice.scalar_multiple(
                    lattice.base_ring()(correction // modulus), vector
                )
            )
        basis = (vector, *kappas, partner)
        formula = (vector, *images, partner)
        assert all(
            lattice.b(formula[left], formula[right]) == lattice.b(basis[left], basis[right])
            for left in range(rank)
            for right in range(rank)
        )


def test_the_divisibility_two_line_lifts_its_congruent_isometries() -> None:
    r"""`U(2) + <2>`: `O(K_I) = {+-1}`, and `-1` is congruent to the identity at two."""
    _assert_the_congruence_lifts(DIVISIBILITY_TWO)


def test_the_odd_divisibility_two_line_lifts_its_congruent_isometries() -> None:
    r"""`U(2) + <3>`: the same on an odd lattice of the same divisibility."""
    _assert_the_congruence_lifts(ODD_DIVISIBILITY_TWO)


def test_the_rank_five_lattice_lifts_its_congruent_isometries() -> None:
    r"""The proper-image lattice: the congruent generators lift and the others need not.

    Two of the three generators are congruent to the identity at two and both
    lift; the third is not congruent and does not, which is what `M_I` being a
    proper subgroup means there and is what the lemma leaves open.
    """
    _assert_the_congruence_lifts(RANK_FIVE)
