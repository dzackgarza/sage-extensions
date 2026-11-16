# Issue to file: `tests/rings/test_completion_maps.sage` is red, four of its five tests, before any #527 change

Not filed by a push: this project's GitHub connection reads issues and pushes
but cannot create them, so the orchestrator posts this body.  The connection
has no issue search, so no "is this already filed" check was made here.

## Title

Four of the five tests in `tests/rings/test_completion_maps.sage` fail, on the ideal comparison of a quotient ring, on the Artin placement of `QQ[x]/(x^3)`, and on the evaluation of an induced map of completions

## Body

`#527`'s reviewer named one of these -- the `NotImplementedError` on ideal
comparison raised inside `_adic_completion_from_owned_data`.  The file is
worse than that, and none of it is caused by `#527`: the same four FAILED ids,
and the same one pass, are produced on the tree before that round
(`ac4ff63`) and on `bbb0dd6` (main at the time of writing).

The one the review named, in both tests that complete a quotient of `QQ[e]`:

```
commutative_algebra.py:5399: in _adic_completion_from_owned_data
    defining_is_unit = defining == unit_ideal
commutative_ideals.py:329: in __eq__
    return bool(self._engine_ideal() == other._engine_ideal())
...
/sage/rings/ideal.py:360: in _richcmp_
    raise NotImplementedError(f'ideal comparison in {self.ring()} is not implemented')
NotImplementedError: ideal comparison in Univariate Quotient Polynomial Ring in ebar over Rational Field with modulus e^2 is not implemented
```

The other three:

```
tests/rings/test_completion_maps.sage:57: in test_artin_name_requires_finite_length
    assert line_completion.adic_artin_truncation(3) in ArtinianRings()
ValueError: Free module on Coproduct of the family over NN = {0, 1, 2, ...} over Fraction Field
of Integer Ring / Ideal (x^3) of ... is not known to be Artinian, so it has not been shown to
have finite length

tests/rings/test_completion_maps.sage:78: in test_a_ring_map_carrying_the_ideal_into_the_ideal_induces_a_map_of_completions
    assert induced(1 - x_hat) * completion.completion_map()(1 + x**2) == completion.one() - x_hat**4
commutative_algebra.py:3344: in image
    raise AssertionError(
AssertionError: cannot evaluate the induced map of completions at element of Ring over Fraction
Field of Integer Ring: it is not known as the image of an element of Free module on Coproduct of
the family over NN = {0, 1, 2, ...} over Fraction Field of Integer Ring
```

The test that passes is `test_nonmaximal_adic_completion_is_complete_but_not_declared_local`.

## Evidence

```
/sage/.venv/bin/python -m pytest -p qc_sage_session -o addopts="" -q --tb=short \
  tests/rings/test_completion_maps.sage
```

| tree | result |
| --- | --- |
| `ac4ff63` (before #527's repair) | 4 failed, 1 passed in 17.42 s |
| `bbb0dd6` (main) | 4 failed, 1 passed in 12.94 s |

The same four FAILED ids and the same pass in both runs; no other failure.
Logs `.scratch/probe527/base-completion-maps.log`,
`.scratch/probe527/main-current-completion-maps.log`.

## Acceptance

Each failure is decided at its owner, and the file is green at its five tests:

- an ideal of a quotient polynomial ring supports `==` -- `commutative_ideals
  .__eq__` reads the engine ideals, and the engine declines to compare ideals
  of a quotient; the comparison that decides `defining == unit_ideal` and
  `defining == zero_ideal` needs a route that answers there, or the
  construction needs to ask a question the quotient answers;
- `QQ[x]/(x^3)` is placed `Artinian` from its chosen presentation, or
  `adic_artin_truncation` states why it cannot place it;
- the induced map of completions evaluates at an element the completion holds
  without a source expression: the test reaches one as `1 - x_hat`, and the
  completion element written from an exact integer literal keeps no source
  expression (`(1 - x_hat).exact_source_expression()` is `None`, while
  `(completion.one() - x_hat).exact_source_expression()` is `-x + 1`).

The literal-subtraction specimen that loses the source expression is
`.scratch/probe527/check13.log`: `1 - x_hat` and `x_hat - 1` answer `None`,
`completion.one() - x_hat` answers `-x + 1`, and the induced map evaluates at
the latter.
