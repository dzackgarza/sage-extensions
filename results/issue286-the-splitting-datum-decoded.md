# The splitting datum's two entries, decoded

The datum `isotropic_line_stabilizer_image` returns for one ambient line orbit
is one of

* `"NOSPLIT"`, or
* a pair `(class_points, sign_flip)` -- `([f1], False)` on the specimen of
  `results/issue286-three-lines-over-two-classes.md`.

Both are now read off the code, at `orthogonal_quotients.py:1630-1764`.

## `"NOSPLIT"` -- an exhibited reflection

Two paths return it, and both *exhibit* something rather than conclude from a
count.

* **One sign character** (`_has_discriminant` false and exactly one of the sign
  kernels set, `:1677-1699`): an integral reflection root `r` with `r` orthogonal
  to the line's generator, `r` in the subgroup, and `r` changing the character,
  proves `G = Gamma * Stab(line)` -- one double coset, hence one `Gamma`-orbit
  inside the ambient orbit.  The constructor checks integrality; orthogonality
  makes `r` fix the line pointwise.  Absence of such a root supplies no
  conclusion, which is why a missing witness falls through rather than
  answering.
* **The sign patterns spanning the sign space** (`:1736-1742`): the stabilizer's
  own exhibited elements present every sign coset that `ker rho` realizes
  (`line_stabilizer_sign_patterns` against `_sign_descent_rank`), so
  `chi(Stab(x))` is the whole preimage of the class stabilizer and the ambient
  orbit does not split.

## `(class_points, sign_flip)` -- the class pair, and whether signs are separate

`:1757-1764`: `class_points` is the engine set of the normalized divided classes
`{c, -c}` of the line's generator -- a *set*, because an unoriented line's
stabilizer may interchange `v` and `-v` -- and `sign_flip` is
`bool(sign_labels)`, true when the signature pattern space is the whole sign
image.  The split is then read as the `rho(Gamma)`-orbits on the `im rho`-orbit
of that class set (`splitting_isometries_from_line_class`, `:1766-1790`), one
lift per double coset, each checked against the character map.

So the second entry is not a second class and not a parity of the line: it is
**whether the sign characters are presented by the stabilizer**, and it is
`False` exactly where they are not.

## What this settles about the specimen

On `U + U(2) + <-2>` the two ambient orbits answer differently:

| ambient orbit | divided class | `|Stab_{O(q)}|` | datum | why |
| --- | --- | ---: | --- | --- |
| 0 | `[0] + 2*[2]` | 2 | `NOSPLIT` | a witness proved the ambient orbit does not split |
| 1 | `-[2]` | 1 | `([f1], False)` | no witness; the split is the orbit of the class pair, signs not separate |

which is `1 + 2 = 3`, the row's count.

## What remains

*Which* of the two `NOSPLIT` paths fired for orbit 0 is not recorded by the
return value -- both answer with the same string -- and that is worth splitting
in the return, since one is a reflection and the other a sign-space count and
they fail differently.  The "why no witness for the second line" is the
reflection's own norm-and-divisibility condition, which the code states
(`r` orthogonal to `v`, integral reflection vector, in the subgroup) and which
this turn does not evaluate at that line.
