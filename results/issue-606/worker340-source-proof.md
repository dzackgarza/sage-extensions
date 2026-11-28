# #606 — smooth-function defining data and the full local construction

The mathematical domain is the full algebra of smooth real-valued functions.
The implementation's admission criterion is a **representation of a declared
smooth function**, not a decidable test of the smoothness of a point map.
A general map is represented by evaluation data. A smooth map has local
smooth formulas or the derivatives of every finite order, including order
zero, on its actual domains. The defining hypothesis is that these are the
derivatives of a smooth map and that the data agree under coordinate changes.
No hypothesis of convergence of its Taylor series is imposed.

## The effective boundary

Let an alleged uniform differentiation procedure accept arbitrary
evaluation-only smooth functions on R and output f'(0) to error less than 1/3.
Run it on the zero function. Its finite set of nonzero queries is disjoint from
some interval (-epsilon,epsilon). Take a smooth bump chi equal to one near 0
and supported in that interval (Lee, Introduction to Smooth Manifolds,
2nd ed., Proposition 2.25, p. 44). Then f(x)=x chi(x) has the same values at
all the queried points, including 0, but derivative 1 at 0. The transcript
cannot distinguish these two functions. The impossibility is not confined
to oracle access: for a machine e, let f_e(x)=0 if e never halts and let
f_e(x)=x chi(2^T x) if e halts at time T, with chi supported in [-1,1]
and identically one near zero. Evaluation to error 2^-n is uniform: simulate
e for n+2 steps; if it has not halted, any later nonzero f_e has uniform norm
at most 2^(-n-2). Nevertheless f_e'(0) is 0 or 1 exactly according as e
does not halt or halts. Uniform differentiation would decide halting.

Thus even a point-map program that happens to be constant cannot be
admitted solely because it is a callable. The same constant point map is
admitted in the general map owner; its represented smooth constant and its
all-order local derivative presentation are admitted in C^infinity.
Every mathematical smooth function has all-order local derivative data,
and nonanalytic functions are included. This changes representation
admission, not the mathematical acceptance criterion.

## The owner-level construction

Lee, Proposition 8.15, p. 181: for a smooth manifold M,
Der_R(C^infinity(M),C^infinity(M)) is the module of smooth vector fields.
D(1)=0 by Leibniz. If f vanishes near p, choose b supported in that
neighborhood and equal to one near p by Proposition 2.25. Then bf=0 and
D(bf)(p)=Df(p), proving locality. Choose a coordinate neighborhood and
smaller neighborhood with fixed cutoff. On the latter the Hadamard
decomposition gives
f(x)-f(p)=sum_i (x_i-x_i(p)) g_i(x),
g_i(p)=partial_i f(p).
Extend the local factors by a cutoff. Locality and Leibniz yield
Df(p)=sum_i D(extended x_i)(p) partial_i f(p).
The coefficients are smooth there, and coordinate changes transform
them by the tangent transition Jacobian by the chain rule. These local
fields glue on arbitrary overlaps. Conversely a field defines the
derivation by the same formula, proving both inverse laws. No finite
atlas, compactness, polynomial algebra presentation, or global finite
family of bumps is required.

For order k, store coefficients partial^alpha f(p)/alpha! for |alpha|<=k
in R[t_1,...,t_n]/(t)^(k+1). Taylor's theorem with remainder and the
product and chain rules give the exact addition, multiplication and
composition laws in this quotient, with the inner jet centered by its
constant term. If the constant term is a nonzero, reciprocal is
a^-1 sum_{j=0}^k q^j with q=1-f/a nilpotent. Partial differentiation
drops the order by one; a vector field applies the local derivative
formula by computing the next jet order. The construction does not
evaluate an infinite Taylor series.

A smooth local transition specified by all-order coefficient functions
gives the coordinate jet by the same composition law. On an actual
overlap, restriction edges have identity coordinate jets. The fibre
transition of TM is the derivative of the coordinate transition,
obtained from the next jet order, not the differential of a pullback map.

For an independently indexed open cover, retain its actual family of
local charts and coefficient functions together with a pointwise choice
of a cover member. Coverage, overlap agreement and smoothness are the
declared construction hypotheses; a selector is computational access to
the cover rather than a finite-cover assumption. A local open-locus
restriction can be represented by smooth nonvanishing guards and a
positive rational radius of a closed coordinate ball inside that actual
open set. For each point such a radius exists by openness, and the
chosen radius supplies the local cutoff construction. It is not obtained
from sampling. Explicit smooth transition functions and their inverses
on actual overlap charts retain non-symbolic coordinate changes.

## Pullback and frame laws

For f:N->M and E->M, the transition matrix G of E on a target overlap
becomes G(f(q)) in f*E. A local section coefficient a is a smooth map
on the actual source piece. On overlap it transforms by G(f(q))a(q).
The pullback of a section has coefficients a(f(q)); arbitrary sections
of the pullback have their own compatible coefficients. These laws are
preserved by composition and restriction. For the tangent bundle
G is a coordinate-transition Jacobian, not df.

For a global rank-r frame, express all frame columns and the given
section locally in a common fibre frame. The resulting square matrix B
is pointwise invertible by the frame hypothesis. The inverse coordinate
functions B^-1 V are smooth by the adjugate formula since det(B) never
vanishes; changes of fibre frame replace (B,V) by (GB,GV), leaving
B^-1V unchanged. The coefficient functions glue over any common
refinement and give the inverse of the A-linear map
(a_1,...,a_r) -> sum_i a_i E_i. No equality of the original covers is
required. For the smooth shear (x,y)->(x,y+g(x)), where g is flat at 0
but not analytic, the test reads the V-coordinate field in U as
(1,-g'(x)); its derivative of y+g(x) is zero. This distinguishes the
actual transition Jacobian from an identity or a symbolic-only route.

## Ring regressions

The unital ring maps from the algebraic closure of Q into an ordered
field are empty: the image of a square root of -1 would square to -1,
contradicting positivity of squares. The underlying set of the p-adic
completion of Z at a maximal ideal (p) is the set of p-adic digit
sequences by uniqueness of successive residue digits, hence has
cardinality continuum. A finite-precision engine is not a finite
underlying completion. A matrix ring is associative and unital by
composition, with the identity matrix as unit. Its center is the
canonical center submodule over the base field, so the rank is read
from that actual submodule, not a guessed rank or Sage compatibility
method. These repairs retain the original mathematical assertions.
