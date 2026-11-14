# #337 — which of the plane's Eichler transvections lie in the unipotent radical

The parabolic at a primitive isotropic plane $I$ is $P_I = \mathrm{Stab}_{O(L)}(I)$, and
its unipotent radical is the common kernel

$$U_I = \ker\big(P_I \to \mathrm{GL}(I) \times O(I^\perp/I)\big).$$

An element lies in $U_I$ exactly when $g(p) = p$ for $p \in I$ and
$(g-1)(I^\perp) \subseteq I$.  `unipotent_radical_generators` returned the plane's
Eichler transvections

$$t(p,x)(y) = y - b(x,y)\,p + b(p,y)\,x - \tfrac12 q(x)\,b(p,y)\,p,
\qquad p \in I,\ x \in p^\perp,$$

(Gritsenko--Hulek--Sankaran, arXiv:0810.1614, section 3.1, equations (4)--(5); Dawes,
section 2 equation (7)) under the radical's name, and they are not all in it.  On the
plane,

$$t(p,x)(p') = p' + b(p',x)\,p,$$

so $t(p,x)$ moves $I$ unless $b(p',x) = 0$ for both generators $p'$ of a basis of $I$.  It
does act trivially on $I^\perp/I$, which is why the family is inside the parabolic at all.

## Measured

```
                     returned   fix I pointwise   trivial on I^perp/I   in the radical
  P1 (splits)            20            18                20                18
  P2 (does not split)    21            14                21                14
```

So at $P_2$ seven of the returned transvections are in the parabolic and not in its
radical, and at $P_1$ two are.

## Repair

* `parabolic_transvection_generators()` — the plane's Eichler transvections, named for
  what they are, with the derivation above and the citation in the docstring.  Every one
  carries the plane onto itself, so every one is an element of the parabolic.
* `unipotent_radical_generators()` — the subfamily that passes both conditions of the
  definition, checked element by element, so the name is now what the method returns.
* `parabolic_stabilizer_generators()` — takes the whole transvection family, which is
  what it took before (its first factor was this family all along).  So the family, its
  size (122 at $P_2$, 164 at $P_1$), the plane-action index ($1$ at $P_2$, $3$ at $P_1$,
  #331) and the exact discriminant image are unchanged; what changed is that the radical
  and the parabolic part are now two named things instead of one misnamed one.
* The cross references in the half-vector and parabolic docstrings point at the right
  method.

Not claimed: that the returned elements *generate* $U_I$.  By the block form the radical
is a lattice of rank $2\,\mathrm{rank}(K) + 1 = 17$ at a plane of $T_{\mathrm{En}}$, and
that rank statement is still open (#331).

## Evidence

```
/sage/.venv/bin/python -m pytest -o addopts= -p qc_sage_session \
  -p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint \
  --no-time-gates tests/lattices/test_the_unipotent_radical_of_a_plane.sage \
  tests/lattices/test_the_parabolic_completeness_of_an_enriques_plane.sage \
  tests/lattices/test_the_enriques_plane_discriminant_image_bound.sage \
  tests/lattices/test_the_plane_block_lift_coset.sage
11 passed in 174.66s (0:02:54)      # at the pushed commit, after the rebase onto 4b0a59c
  (the same run before the rebase: 11 passed in 141.97s)

red, before the repair, at 5c9bc979 on the test module only:
1 failed, 1 passed in 2.27s
  test_every_unipotent_radical_generator_fixes_the_plane_pointwise:
  assert element(vector) == vector
  assert -4*e_e - 4*e_...*e_a1 - 2*e_a2 == e_ep
```

