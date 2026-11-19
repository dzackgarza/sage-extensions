# The key is exact on every lattice a test can afford, and equivocal only at `T_Co`

`issue381-the-refusal-has-no-cheaper-route.md` left two options: carry the
stabilizer's image so the divided-class read can separate a fibre, or accept the
refusal.  This note prices the first one's *testability*: whether the ambiguity
the repair would address can be exhibited anywhere the suite can run.

## Measured

`probe-key-ambiguity.py` (`key-ambiguity.log`), both kernel rows of every lattice
the driver's `--lattice` names besides `Tco`:

| lattice | row | line cusps | distinct keys | keys naming >1 cusp |
| --- | --- | ---: | ---: | ---: |
| `6JRS = U + U + <-2>` | `Otilde`, `Otilde+` | 1 | 1 | **0** |
| `U + U(2) + <-2>` | `Otilde`, `Otilde+` | 3 | 3 | **0** |
| `U + U(2) + <-4>` | `Otilde`, `Otilde+` | 4 | 4 | **0** |
| `U + U + <-4>` | `Otilde`, `Otilde+` | 1 | 1 | **0** |
| `T_Co` | `Otilde`, `Otilde+` | **527** | **444** | **24** |

The key is injective on every row of every affordable lattice -- the four
specimens the gate file and the driver run -- and equivocal only at `T_Co`, where
83 cusps share a key and the buckets reach fifteen.

## What that means for the repair

A finer invariant would change `_isotropic_line_image_key` or what the read
asks; the behaviour it changes is only visible where the key is equivocal, and
no test lattice is.  **There is therefore no red test to write** for such a
change: on `6JRS`, `U+U(2)+<-2>`, `U+U(2)+<-4>` and `U+U+<-4>` the old key and
any refinement of it answer the same, so a test would pass before and after.  The
only witness the change would have is the `T_Co` row itself, which costs 35
minutes and a quiet host and which has been killed twice by other tenants.

That is worth stating plainly rather than working around: by this tree's own
rule, an inert branch that cannot have a red test is said so and never given a
manufactured one.  Here the inertness is not in a branch but in the **whole
class of affordable specimens**, which is stronger: a refinement cannot be
distinguished from the current key by any test the suite can afford.

## What follows for `#381`

The option "carry the stabilizer's image" is a change whose correctness would
rest on the `T_Co` measurement alone, with no test behind it -- and the other
option is to accept the refusal, whose witness is that same row and which needs
no change at all.  Both rest on the same run.  Until it lands on a quiet host,
`#381`'s kernel rows have one measured blocker (24 ambiguous keys) and one
unmeasured question (`Otilde`'s own first record), and neither is a code question
the suite can decide.

No object is introduced: the key is the library's, its fibres are the double
cosets of Dutour Sikiric--Hulek, arXiv:2302.01679v2, Lemma 3.6, printed p. 22,
and every count above is a datum the library printed.
