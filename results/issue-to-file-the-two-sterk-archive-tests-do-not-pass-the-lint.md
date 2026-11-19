# Issue to file under #255: the two Sterk archive tests do not pass the test lint

Not filed by a push: this project's GitHub connection reads issues and pushes commits but cannot
create them, so this body is for the orchestrator to post, as its own issue rather than under #255 —
the two files predate #255's work and their counting idiom is their own.  No repair is made here.

## Title

The two Sterk archive tests carry ten test-lint findings, so the lint is red on files that read
`Sterk`'s roots

## Body

`python -m sage_extensions.testing.test_lint` on the two files says:

```
tests/lattices/test_sterk_elliptic_population_archive.sage:12: TL01 from collections import ...: take every name from the session
tests/lattices/test_sterk_elliptic_population_archive.sage:13: TL01 from fractions import ...: take every name from the session
tests/lattices/test_sterk_elliptic_population_archive.sage:156: TL10 len(): ask for a cardinality
tests/lattices/test_sterk_elliptic_population_archive.sage:158: TL10 len(): ask for a cardinality
tests/lattices/test_sterk_maximal_elliptic_subdiagrams.sage:13: TL01 from collections import ...: take every name from the session
tests/lattices/test_sterk_maximal_elliptic_subdiagrams.sage:15: TL01 import the complete session with from sage_extensions.all import *
tests/lattices/test_sterk_maximal_elliptic_subdiagrams.sage:36: TL10 len(): ask for a cardinality
tests/lattices/test_sterk_maximal_elliptic_subdiagrams.sage:37: TL10 len(): ask for a cardinality
tests/lattices/test_sterk_maximal_elliptic_subdiagrams.sage:39: TL10 len(): ask for a cardinality
tests/lattices/test_sterk_maximal_elliptic_subdiagrams.sage:93: TL10 len(): ask for a cardinality
2 files, 10 findings (TL01, TL10)
```

Under the lint plugin in a pytest run these become seven ERRORS at setup, one per test of the two
files, so the run over the Sterk files reports `2 passed, 7 errors` — the two passes being
`test_the_sterk4_projection_ranks.sage`.

**Why it is not an import fix.**  `Counter` is the expected rank multiset of every one of the five
diagrams (`test_sterk_maximal_elliptic_subdiagrams.sage:20`–`:24`) and the accumulator of the
observed one (`:37`, `test_sterk_elliptic_population_archive.sage:187`, `:193`), and `Fraction` is the
exact scale key (`:182`, `:194`); every rank in both files is an `len()` of an `index_set`
(`:36`–`:39`, `:93`, `:156`, `:158`, `:37`).  Replacing the imports alone leaves the `len()` findings;
removing both means rewriting each count as a cardinality and each `Counter` as a dict keyed the same
way, with the expected multisets unchanged.

**What would close it.**  Both files lint-clean, with their assertions unchanged: the five
`_MAXIMAL_RANKS` multisets, the `(8, 9)` rank counts per diagram, and the archived type counts of
the connected populations, all still equal to the same numbers.

**Verified, and not.**  The lint output above is current at this head.  The two files' *tests* were
not run to completion: under `--no-test-lint` five of the seven had passed when the run was stopped,
and the remaining two are slow, so their outcome is unknown and is not claimed.
