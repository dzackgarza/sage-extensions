# #279, acceptance item by item

`Lattices.vectors_of_square_with_complement` is `src/sage_extensions/categories/lattices.py:10273`.
Every line below is a line of the tree at `fe5bfba`, where this record was
written; the test file is `tests/lattices/test_vectors_of_square_with_complement.sage`.

## 1. Primitive, the square, the isometric complement, and the certificate's index

The operation's certificate is built at `lattices.py:10613` (`pair.overlattice`),
its index is asserted against the glue's order at `:10615`, and the pair
`(delta, isometry)` is yielded at `:10636`.

Decided by `test_the_certificate_is_an_isometry_of_an_even_overlattice_of_the_prescribed_index`
(`tests/...:38`) on `A2`, square `-2`, complement of a root:

| what | line |
| --- | --- |
| `delta.q() == -2` | `:58` |
| `lattice.subobject_on([delta]).is_primitive()` | `:59` |
| the complement is isometric to the given one | `:60` |
| the isometry's codomain is the lattice | `:63` |
| the overlattice is even | `:64` |
| `\|A_L\| * index^2 == \|A_<d> perp A_C\|`, with `index^2 = \|A_pair\| / \|A_T\|` | `:49`, `:51`, `:65` |
| the preimage of `delta` is primitive of the prescribed square | `:69`, `:70` |

and for the consumer specimen at `:322`--`:329` of the same file.

## 2. Definite control agrees with the enumeration reduced modulo `O(T)`

Five definite specimens, each comparing the operation's answer with the
enumerated fibre carried by the lattice's own simple reflections:

| specimen | test | count | fibre comparison |
| --- | --- | --- | --- |
| `A2`, card `0012`'s `O` row at norm two | `:73` | `:87` | `:111` |
| `<-2> perp <-2>`, complement `<-2>` | `:116` | `:131` | `:145` |
| `A3`, complement of rank two | `:150` | `:171` | `:195` |
| `D4`, complement of rank three | `:200` | `:219` | `:243` |
| `A5`, complement with two glue classes | `:248` | `:267` | `:291` |

The expected counts come from card `0012` for `A2` (read by tag through
`card("primitive_orbit_series", "0012")`, never typed) and from the
enumeration reduced modulo `O(T)` for the rest, which is the item's own
criterion. The collapse the item exercises is at
`lattices.py:10382`--`:10396` (which group applies), `:10541` (a rank-one
complement's own negation), `:10553` (the image of `O(C)`), `:10589` (the walk).

## 3. The consumer specimen: `T_En`, square `-2`, complement `T_Co`

Decided by `test_the_enriques_gluing_gives_a_vector_of_square_minus_two_with_complement_t_co`
(`tests/...:296`): the index is `:314`--`:315`, exactly one vector is returned
at `:319`, and each returned vector's square, primitivity, complement, `L`'s
signature, the index relation and the certificate's preimage are `:322`--`:329`.

The expected count is not the operation's own. Namikawa, *Periods of Enriques
surfaces*, Math. Ann. 270 (1985), 201--222, Theorem 2.13, as cited by
Alexeev--Engel--Gritsenko--Sankaran, *Compact moduli of Enriques surfaces of
degree 2*, section 2, gives a unique `(-2)`-vector in `T_En` modulo
`Gamma_En = O(T_En)`, with `T_En = U + U(2) + E8(2)` there and
`NamedLattices.TEn` here; the complement is Dolgachev--Kondo, Izv. Math. 77:3
(2013), section 3 equation (3.6), printed p. 513.

## 4. A regression test through the public route on both specimens

Both specimens are in the one file and both go through
`Lattices.vectors_of_square_with_complement` (`lattices.py:10273`): the `A2`
specimen at `:38` and `:73`, the `T_En` specimen at `:296`. The measured runs of
the whole file are in the commit bodies of the commits that added each test; the
last full-file run was `5 passed in 4.57 s` at `cccf2c6`.

## Not covered, and why

The operation refuses a complement that is indefinite and not 2-elementary,
because there is then no known generating set of `O(C)` to compute the image to
collapse by (`lattices.py:10394`--`:10401`, the named gap). Namikawa's Theorem
2.15 counts two `O(T_En)`-orbits of `(-4)`-vectors, one with complement
`<4> + U + E8(2)`, and that orbit is one the operation refuses. It is outside
this issue's acceptance and closing it is the indefinite-generator question of
`sage_extensions#381`.
