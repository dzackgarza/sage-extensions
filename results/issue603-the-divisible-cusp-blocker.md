# #603: the divisibility-2 cusp — the degenerate blocker is gone, the construction is not written

Status: **the construction named in the last report is still not delivered.** What
changed is the blocker: the last note said the degenerate lattice `J = v^\perp`
"needs its own class model". It does not, and this is the check.

Every measurement is on the adopted runtime in a worktree of `main = f6c4f9c`
(tree bound at `/repos/sage-extensions`, the port at `/work`).

## J splits, and the split is nondegenerate

For a primitive isotropic `v` with `d = div(v)`: `J = v^\perp` has rank `n-1` and
radical `Zv`, `K_I = J/Zv`, and `J -> K_I` splits *as lattices*: a section
`s: K_I -> J` gives `K~ = s(K_I)` with `b(s(x), s(y)) = b_{K_I}(x, y)` because the
radical `Zv` is orthogonal to all of `J`.  Pick `w` with `b(v, w) = d` (integer
solve of the pairing row against `d`), and

    L_0 = <v, w> + K~

is a **nondegenerate** sublattice of `L` of finite index.  Verified on both cusps:

| lattice, vector | `d` | `K~` isometric to `K_I` | rank of `(v, w, K~)` | `det L_0` |
| --- | --- | --- | --- | --- |
| card `0125` = `U(2) + E8(-2)` at `2e_1` | 2 | yes, all 64 pairings | 10 / 10 | `-1024` |
| card `026E` = `U + D4(-1) + A1(-1)` at `e_1` | 1 | yes, all 25 pairings | 7 / 7 | `8` |

So the Smith-form class model the non-isotropic construction already uses — which
inverts `L_0`'s Gram matrix — applies verbatim at an isotropic vector.  The
`A_{L_0}` classes, the gluing subgroup `H = L/L_0`, and the orbit of `H` under
`O(K~)` are all computed exactly as they are for a non-isotropic vector.

## What the construction still needs

`Stab(v) = {sigma in O(K~) : (1_{<v,w>} + sigma)(H) = H}`, i.e. the *same*
construction with a **rank-two fixed part** (currently rank one) whose Gram is
nondegenerate but has nonzero off-diagonal `b(v, w) = d`.  Concretely: the
projection of a vector onto `<v, w> ⊗ Q` in
`_nonisotropic_pointed_stabilizer_generators` is `c = b(x,v)/b(v,v)`, which needs
`b(v,v) != 0`; for a rank-two fixed part it is `x_H = b(x, -) G_H^{-1}` on the
`2 x 2` Gram `G_H`, and the rest of the code — the classes, the orbit, the
Schreier family, the extension formula, the integrality check — is unchanged.

That is one generalization, not a new class model, and it is the repair: it makes
`0125`'s two hyperbolic cusps and `029J`'s `L_2` answer from the construction
instead of the port, and with them the card's discriminating index 527.

Not written here: the generalization needs its own validation cycle, and each
probe of the current path costs 72 s on `0125` and did not return on `029J`'s
`L_2` in 400 s.  Nothing was changed to make a number look better.
