# The last gap in the nowhere-vanishing decision: measured, and why the cheap reading adds nothing

Status: no repair landed.  The gap is real, the cheap readings are ruled out with an
argument and a measurement, and the repair that would close it is named with what it
costs.

## The case, measured on `67fc45a`

    P = x^4 - 2 x^2 y^2 + 2 y^4 + 1
    P(1,1) = 2, P(1,0) = 2, P(0,1) = 3, and  P = 2(t - 1/2)^2 + 3/2  in  t = y^2/x^2
    _decided_no_real_zero(P, (x, y))  ->  None          (undecided)

So a frame whose determinant is `P` is refused although `P` is bounded below by `3/2`:
the decision answers "undecided", and the frame's rank, basis and trivialization are
unavailable for it.

## The certificate that exists

    (x^2, y^2)  [ 1 -1 ; -1 2 ]  (x^2, y^2)^T  + 1  =  P

and the Gram matrix has leading minors `1` and `1`, so it is positive definite and
`P >= 1`.  The matrix is a Gram matrix *in the monomials* `x^2` and `y^2`, not in the
variables, and finding it is the Gram-matrix (sum-of-squares) method: a polynomial of
degree `2d` is a sum of squares of polynomials of degree `d` exactly when some positive
semidefinite matrix `G` satisfies `P = u^T G u` with `u` the monomials of degree at most
`d`, and an *oracle* choice of `G` is what the method searches for (Lasserre, *Moments,
Positive Polynomials and Their Applications*, Ch. 2-3).

## Why the canonical reading adds nothing

The tree's monomial rule already reads a polynomial whose exponents are all even, whose
coefficients have one sign and whose constant term is nonzero.  The obvious extension --
write an even-degree polynomial as a form in the monomials of half degree, using the
balanced split `e = floor(e/2) + ceil(e/2)` -- gives a **diagonal** Gram matrix, because
an even-exponent monomial is a perfect square: `x^4 = (x^2)^2`, `y^4 = (y^2)^2`,
`x^2 y^2 = (xy)^2`.  A diagonal matrix is positive semidefinite exactly when its entries
are non-negative, which is the monomial rule again, with the same coefficients.  So that
extension decides nothing new, and the case above stays undecided under it: the Gram
matrix that certifies `P` puts `x^2 y^2` in the off-diagonal entry `G[x^2][y^2]`, not on
the diagonal.

An odd-exponent monomial cannot be used as a Gram variable either: it has no sign, so a
form in odd monomials says nothing about `P >= 0`.

## What would close it

The Gram-matrix search, for each chart expression: enumerate the monomials of degree at
most `d`, and decide whether **some** symmetric `G` with `P = u^T G u` is positive
semidefinite.  For small cases that is a linear system plus a principal-minor decision,
which the tree can do exactly over the rationals; in general it is a semidefinite program,
and over the rationals exact SDP is a project rather than a turn.  The scope to keep it
exact and bounded: degree at most four, and the chart's own cutting conditions divided out
first, as the other certificates of `_sum_certificate_covers` already do.
