# The no-split answer now names which proof gave it

`isotropic_line_stabilizer_image` answered `"NOSPLIT"` from three different
arguments and could not say which.  It now answers with a value that still
compares equal to `"NOSPLIT"` -- so every consumer reads it unchanged -- and
carries the witness:

| site | witness | what it exhibits |
| --- | --- | --- |
| `orthogonal_quotients.py:1700` | `NO_SPLIT_BY_REFLECTION` | one integral reflection root orthogonal to the line's generator, in the subgroup, changing the character |
| `:1736` | `NO_SPLIT_BY_ZERO_CLASS` | the divided class is `0`, where the double cosets are one coset |
| `:1742` | `NO_SPLIT_BY_SIGN_PATTERNS` | the stabilizer's patterns span the sign space `ker rho` realizes |

`_NoSplit` is a `str` subclass whose value is `"NOSPLIT"` and whose `reason`
attribute is one of the three module constants (now in `__all__`).  Its
constructor refuses any other reason, so the three arguments cannot be collapsed
again by accident.

## Measured on the specimen

`.scratch/w286-probes/probe-reason2.log`, one process:

```
  ambient orbit 0: 'NOSPLIT'
    is the plain answer: True, reason: the line's divided class is the zero class
  ambient orbit 1: ([ f1 ], False)
    is the plain answer: False, reason: None
```

So `U + U(2) + <-2>`'s `1 + 2 = 3` is now *named* at both ends: the first ambient
orbit's line has divided class `0` -- one double coset, one orbit -- and the
second's is a class pair with the signs not separate, which splits in two.  The
earlier note could only say "a witness proved it"; this says which one.

## The test this needs, and what blocks it

The natural test asks the answer's `reason` against the library's own constant,
never a typed literal (the test lint forbids a string literal in an assertion).
That needs the four names to be **session names**, and
`src/sage_extensions/categories/orthogonal_quotients.py` is not one of the
modules `src/sage_extensions/all.py` star-imports (`all.py:35-60`), so its
`__all__` reaches nothing.  Publishing them means adding one star-import line to
`all.py` and taking four names into the session preamble -- a decision about the
public surface that is not mine to take in a turn's tail, and the reason this
change lands with a probe rather than a test.

What the change does not disturb: the three consumers compare by equality
(`orthogonal_quotients.py:4674`, `lattice_morphisms.py:5046`,
`tests/lattices/the_enriques_pointed_stabilizer_row.py:59`) and the probe prints
`is the plain answer: True`, so their branch is taken exactly as before.
