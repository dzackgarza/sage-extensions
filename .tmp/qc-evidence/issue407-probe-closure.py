from sage.all import Zmod, GF
from sage.rings.algebraic_closure_finite_field import AlgebraicClosureFiniteField
Z, F = Zmod(3), GF(3)
print("Zmod(3) is GF(3):", Z is F, "equal:", Z == F, "type:", type(Z).__name__)
print("Zmod is_prime_field:", Z.is_prime_field(), "GF is_prime_field:", F.is_prime_field())
for label, base in (("Zmod", Z), ("GF", F)):
    try:
        C = AlgebraicClosureFiniteField(base, "z3")
        print(f"{label}: OK {C} degree {C.degree()} base {C.base_ring()!r}")
    except Exception as error:
        print(f"{label}: {type(error).__name__}: {error}")
