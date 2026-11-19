# #279, acceptance item by item

Third revision, after a second reviewer's finding.  The operation is
`src/sage_extensions/categories/lattices.py:10223`
(`Lattices.vectors_of_square_with_complement`); the test file is
`tests/lattices/test_vectors_of_square_with_complement.sage`.  Each line number
is that of the tree this record is committed with, and every one of them was
re-read there.

What this revision changes: the certificate test's count used to be a typed `1`,
so its expected number was the operation's own answer and not an oracle.  The
test now reads card `0012` by tag (`tests/...:110`), ties that card's lattice to
the specimen through `is_isometric_to` (`:111`), and takes the expected count
from the card's `O` row at norm two (`:112`), compared at `:122`.

## 1. Primitive, the square, the isometric complement, and the certificate's index

The certificate is the isometry **from `T` to the overlattice**, carrying `delta`
to `L`'s generator of the `<d>` summand.  It is yielded as
`realizing.inverse()` at `lattices.py:10588`, from the `L -> T` map built at
`:10571`; the overlattice is built at `:10563` and its index asserted against
the glue's order at `:10565`.

Decided by `test_the_certificate_is_an_isometry_from_the_lattice_to_an_even_overlattice`
(`tests/...:91`) on the positive definite `A2`, square `2`, complement of a root:

| what | line |
| --- | --- |
| the expected count, from card `0012`'s `O` row at norm two, its lattice tied to the specimen | `:110`--`:112` |
| the operation's count against that card row | `:122` |
| `index^2 = \|A_pair\| / \|A_T\|`, taken as a square | `:114`--`:119` |
| the square, primitivity and the complement's isometry | `:125`--`:127` |
| the certificate's domain is the lattice | `:131` |
| the overlattice is even, and `\|A_L\| * index^2 = \|A_pair\|` | `:133`--`:134` |
| the image of `delta` is primitive of the prescribed square in `L` | `:136`--`:138` |

`C` is not the operation's own answer either: the test builds it at `:109` from
`_definite_control` (`:30`--`:34`) as the orthogonal complement of `A2`'s first
module generator, and compares the returned vector's complement with that.
The same assertions for the consumer specimen are at `:288`--`:300`.

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
| `A2`, card `0012`'s `O` row at norm two | `:141` | the card at `:154`, the enumeration at `:155` |
| `<2> perp <2>`, complement `<2>` | `:158` | the enumeration at `:185` |
| `A3`, complement of rank two | `:194` | the enumeration at `:208` |
| `D4`, complement of rank three | `:217` | the enumeration at `:231` |
| `A5`, complement with two glue classes | `:240` | the enumeration at `:254` |

The collapse the item exercises is `lattices.py:10334`--`:10350` (which group
applies), `:10491`--`:10496` (a rank-one complement's own negation), `:10497`
(the image of `O(C)`), `:10525`--`:10539` (the walk).

## 3. The consumer specimen: `T_En`, square `-2`, complement `T_Co`

Decided by `test_the_enriques_gluing_gives_a_vector_of_square_minus_two_with_complement_t_co`
(`tests/...:263`): the specimens are `NamedLattices.TEn` and `NamedLattices.Tco`
(`:277`--`:278`, built at `catalogue.py:230` and `:204`), the index at
`:279`--`:283`, the count at `:286`, and each returned vector's square,
primitivity, complement, the certificate's domain, the overlattice's signature,
the index relation and the image of `delta` at `:288`--`:300`.

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
`Lattices.vectors_of_square_with_complement` (`lattices.py:10223`): `A2` at
`:121` and `:153`, `T_En` at `:285`.

## Runs

- Green, the certificate test alone (`-k certificate`) at the tree this record is
  committed with: `1 passed, 6 deselected in 7.47s`, the test call 1.10 s.  The
  run's only gate line is `collection took 6.12 s; the measured ceiling is 6 s`,
  at host load 8.9 -- this host, not the change; CI runs that gate.
- Probe (`probe279_item1.py`, log `.tmp/279r2-probe-base.log`) on the parent
  `e1e8313`, the same specimen the certificate test uses: card `0012`'s `O` row
  is `{'constant': 0, 'w': [0, 0, 0, 0], 'z': [0, 1, 0, 0]}`, the operation's
  count is 1, `delta` has square 2 and is primitive, the complement is isometric,
  the certificate's domain is the lattice, the overlattice is even,
  `|A_L| * index^2 == pair_order`, and the image of `delta` is primitive of
  square 2 in the overlattice.  Peak tree RSS 497 MiB.
- No red test, and why: on `A2` the operation's answer already equals the card's
  row at the parent, so no library answer is wrong to exhibit -- the defect this
  round repairs is where the expected number came from, and a red for it would
  need the card to disagree with the operation.  Said here rather than
  manufactured with a mutated tree or a guard.
- The red recorded by the second revision is that round's, at its own parent: the
  certificate test failing on `isometry.domain() is lattice` (the reverse
  direction the operation then returned), reproduced in `.tmp/279g-probe-n.log`.
  That direction is repaired in the operation at `lattices.py:10588` and is not
  this round's subject.

## Not covered, and why

The operation refuses a complement that is indefinite and not 2-elementary,
because there is then no known generating set of `O(C)` to compute the image to
collapse by (`lattices.py:10344`--`:10351`, the named gap).  Namikawa's Theorem
2.15 counts two `O(T_En)`-orbits of `(-4)`-vectors, one with complement
`<4> + U + E8(2)`, and that orbit is one the operation refuses.  It is outside
this issue's acceptance and closing it is the indefinite-generator question of
`sage_extensions#381`.
