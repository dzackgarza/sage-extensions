# Record for `dzackgarza/research#621` (comment to post)

Posting a comment needs issue-write, which this project's GitHub connection does
not provide; this file is the record to paste.  It answers comment
`6514779365` ("Inverse-map reuse regression coverage").

## Canonical source revision

The delta that comment describes lived only in research's vendored fork of the
library (`5cf90d9b`, `src/dzack_research/preamble/categories/...`).  It is now at
the canonical owner, `dzackgarza/sage-extensions`:

| revision | content |
| --- | --- |
| `297bf696a2bb68cf5b64b4723a9c22cc5ae1e50d` | the ported delta (`lattice_centralizers.py`, `torsion_form_modules.py`) |
| `80cbb71781f75b3f69de1769e4f4288e8035a759` | its regression test and the corrected measurements |
| `56fd308` | the isometry equality/hash evidence that the port relies on |

`_coinvariant_discriminant_from_invariant` is byte-identical to the fork modulo
line wrapping.  Public contracts unchanged: the transported automorphism stays in
`O(A_{L^-})`, its forward/inverse arrows keep the module Mor parent, and
`transported.inverse()` equals the independently transported inverse while
reusing its maps by object identity.

## Transport acceptance

`tests/lattices/test_discriminant_transport_inverse_reuse.sage` (4 tests, green on
the revisions above): the stored-pair identity assertions, the glue data built
once, and a count of `_presented_module_from_morphism` proving that a conversion
after the first constructs **no** presented module — the same test fails at
`7b222e8` with twelve constructions for the second conversion.

Steady per-conversion cost (one untimed conversion first, own process, idle VM):

| case | form order / generators | before (`7b222e8`) | after (`297bf69`) |
| --- | --- | --- | --- |
| `U + U` specimen | 4 / 2 | 0.211 s, 13.0 constructions | 0.014 s, 0 |
| `I_En` on the K3 lattice | 1024 / 12 | 11.7-26.3 s, 30.7 constructions | 0.193 s, 0 |

The first conversion on a form pays a one-off 25-38 s at order 1024 (glue
inverses, the module's presentation, the finite engine), amortized over the
consumer's 19 conversions.  Cost follows the coinvariant form's generator count,
not the group order: 0.193 s at 12 generators against 0.014 s at 2, with the
order 256 times apart.

## Remaining full-consumer image block, distinct from the transport

The frozen `O(L^f)`-generator route for `I_En` — `LatticeIsom.an_element` through
`sage_indefinite_port.indefinite.marked_lattices` — still aborts in this image:
`sage.graphs.bliss` crashes (exit 139) inside the automorphism search, and under
the image's embedded port checkout it also hits that checkout's pre-move
`dzack_research` imports.  The transport acceptance above therefore prices the
conversions on `O(A_{L^f})`, which is finite data; the invariant form, coinvariant
form and glue are the frozen order-1024 ones, and the conversion's cost depends on
those, not on which automorphism is fed in.  Nothing about the transport itself is
blocked.
