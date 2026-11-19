# #279, acceptance item by item

Second revision, after a reviewer's findings.  The operation is
`src/sage_extensions/categories/lattices.py:10273`
(`Lattices.vectors_of_square_with_complement`); the tests are
`tests/lattices/test_vectors_of_square_with_complement.sage`.  Each line number
is that of the tree this record was written against, with its file named, and
every one of them was re-read at `7e4ff5a` and reads as stated there.

## 1. Primitive, the square, the isometric complement, and the certificate's index

The certificate is the isometry **from `T` to the overlattice**, carrying `delta`
to `L`'s generator of the `<d>` summand.  It is yielded as
`realizing.inverse()` at `lattices.py:10638`, from the `L -> T` map built at
`:10621`; the overlattice is built at `:10613` and its index asserted against
the glue's order at `:10615`.

Decided by `test_the_certificate_is_an_isometry_from_the_lattice_to_an_even_overlattice`
(`tests/...:91`) on the positive definite `A2`, square `2`, complement of a root:

| what | line |
| --- | --- |
| `index^2 = \|A_pair\| / \|A_T\|`, taken as a square | `:103`--`:108` |
| the square, primitivity and the complement's isometry | `:114`--`:118` |
| the certificate's domain is the lattice | `:120` |
| the overlattice is even, and `\|A_L\| * index^2 = \|A_pair\|` | `:121`--`:123` |
| the image of `delta` is primitive of the prescribed square in `L` | `:125`--`:127` |

The same assertions for the consumer specimen are at `:277`--`:289`.

## 2. Positive definite control agrees with the enumeration reduced modulo `O(T)`

The controls are the positive definite forms `Lattices(ZZ)(name).twist(-1)`
(`:30`), with square `2`, so the item's "positive-definite `T`" is met literally.
`_enumerated_orbit_count` (`:59`) partitions the **enumerated** fibre under the
actions it is given and the negation -- the simple reflections (`:37`), plus a
permutation of isometric summands where the lattice is reducible -- so each
expected count is computed from the enumeration, and no vector the operation
returned is a seed.

| specimen | test | operation's count against |
| --- | --- | --- |
| `A2`, card `0012`'s `O` row at norm two | `:130` | the card at `:143`, the enumeration at `:144` |
| `<2> perp <2>`, complement `<2>` | `:147` | the enumeration at `:174` |
| `A3`, complement of rank two | `:183` | the enumeration at `:197` |
| `D4`, complement of rank three | `:206` | the enumeration at `:220` |
| `A5`, complement with two glue classes | `:229` | the enumeration at `:243` |

The collapse the item exercises is `lattices.py:10382`--`:10396` (which group
applies), `:10541` (a rank-one complement's own negation), `:10553` (the image
of `O(C)`), `:10589` (the walk).

## 3. The consumer specimen: `T_En`, square `-2`, complement `T_Co`

Decided by `test_the_enriques_gluing_gives_a_vector_of_square_minus_two_with_complement_t_co`
(`tests/...:252`): the index at `:268`--`:272`, the count at `:275`, and each
returned vector's square, primitivity, complement, the certificate's domain, the
index relation and the image of `delta` at `:277`--`:289`.

The count is Namikawa's, not the operation's: *Periods of Enriques surfaces*,
Math. Ann. 270 (1985), 201--222, Theorem 2.13, as cited in
Alexeev--Engel--Garza--Schaffler, *Compact moduli of Enriques surfaces of degree
2*, Nagoya Math. J. 259 (2025), 581--624, section 2, gives a unique `(-2)`-vector
in `T_En = U + U(2) + E8(2)` modulo `Gamma_En = O(T_En)`.  The complement is
Dolgachev--Kondo, Izv. Math. 77:3 (2013), section 3 equation (3.6), printed
p. 513.  There is no card row for `T_Co`; a published count is the oracle the
acceptance allows for that, and a card row would replace it.

## 4. A regression test through the public route on both specimens

Both specimens are in the one file, both through
`Lattices.vectors_of_square_with_complement` (`lattices.py:10273`): `A2` at
`:91` and `:130`, `T_En` at `:252`.

## Runs

- Red, the certificate test alone (`-k certificate`) on the parent of `2f56fdf`:
  `1 failed, 6 deselected in 46.89s`, failing at that parent's `tests/...:113`
  on `isometry.domain() is lattice` -- the reverse direction the operation
  returned.  Probe evidence for the same fact: `.tmp/279g-probe-n.log`
  (`domain is lattice False`, operation returning one vector).
- Green, the whole file at `e4fe31b`:
  `7 passed in 20.63s`; the slowest call 5.09 s (the consumer), the certificate
  test 1.15 s.  The run's only gate line is `collection took 10.38 s` against a
  6 s ceiling, this host's load (`star import 0.49 s`); no test call is over its
  ceiling.

## Not covered, and why

The operation refuses a complement that is indefinite and not 2-elementary,
because there is then no known generating set of `O(C)` to compute the image to
collapse by (`lattices.py:10394`--`:10401`, the named gap).  Namikawa's Theorem
2.15 counts two `O(T_En)`-orbits of `(-4)`-vectors, one with complement
`<4> + U + E8(2)`, and that orbit is one the operation refuses.  It is outside
this issue's acceptance and closing it is the indefinite-generator question of
`sage_extensions#381`.
