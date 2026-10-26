r"""Continuous cyclotomic and quadratic characters of absolute Galois groups."""

from math import gcd

from sage.groups.generic import discrete_log
from sage.misc.classcall_metaclass import ClasscallMetaclass
from sage.rings.integer_ring import ZZ

from sage_extensions.categories.group.profinite.absolute_galois_groups import (
    AbsoluteGaloisGroupsOfFiniteFields,
)
from sage_extensions.categories.group.profinite.galois_quotient import (
    FiniteGaloisExtension,
)
from sage_extensions.categories.rings.ring_foundation import (
    _engine_element,
    _engine_ring,
    _owned_engine_element,
    _owned_integers,
)


class RestrictedProfiniteCharacter(metaclass=ClasscallMetaclass):
    r"""The character restricted along its retained subgroup inclusion.

    The public class call selects this existing realization in the canonical
    continuous group Mor. Its private class-call hook is not inherited by
    the generated arrow type, whose initialization joins GroupMorphism.
    """

    @staticmethod
    def __classcall_private__(cls, character, subgroup):
        if subgroup.supergroup() is not character.domain():
            raise ValueError(
                f"cannot restrict {character} to {subgroup}: a restriction needs a subgroup "
                f"of the character's domain {character.domain()}, but {subgroup} is a "
                f"subgroup of {subgroup.supergroup()}"
            )
        parent = subgroup.Mor(character.codomain())
        return parent._from_realization_engine(cls, character, subgroup.inclusion())

    def __init__(self, parent, character, inclusion) -> None:
        self._character = character
        self._inclusion = inclusion
        super().__init__(parent, self._call_)

    def _call_(self, element):
        return self._character(self._inclusion(element))

    def is_continuous(self) -> bool:
        return True


class ProfiniteCharacter(metaclass=ClasscallMetaclass):
    r"""The retained finite-factor interface of a profinite character.

    The factor stage alone does not specify a unique character. Concrete
    realizations retain its defining map; the bare interface computes the
    uniform identity value and names the missing-map frontier elsewhere.
    """

    @staticmethod
    def __classcall_private__(cls, domain, codomain, extension: FiniteGaloisExtension):
        return domain.continuous_morphisms_to(codomain)._from_realization_engine(cls, extension)

    def __init__(self, parent, extension: FiniteGaloisExtension) -> None:
        self._factor_extension = extension
        super().__init__(parent, self._call_)

    def _call_(self, element):
        r"""Every character sends one to one; other values need its defining map."""
        match element == self.domain().one():
            case True:
                return self.codomain().one()
            case _:
                assert False, (
                    f"evaluating {self} away from a decided identity needs the defining "
                    f"character on its finite factor {self.factor_extension()}; "
                    "a finite factor alone does not supply that value computation"
                )

    def factor_extension(self) -> FiniteGaloisExtension:
        return self._factor_extension

    def extension(self) -> FiniteGaloisExtension:
        r"""Return the finite Galois extension through which this character factors."""
        return self.factor_extension()

    def factorization(self):
        return self.domain().restriction_map(self._factor_extension)

    def _root_generated_kernel(self):
        r"""The open kernel when the retained root generates the finite stage.

        CyclotomicCharacter and QuadraticCharacter select this supplier:
        their value is one exactly when the chosen stage-generating root is
        fixed. A general character merely factoring through that stage has
        the inherited group-map kernel, which need not equal this subgroup.
        """
        return self.domain().open_subgroup(self._factor_extension)

    def restrict(self, subgroup):
        return RestrictedProfiniteCharacter(self, subgroup)

    def is_continuous(self) -> bool:
        return True


def _finite_root_at_stage(root, stage):
    total_degree = ZZ(_engine_ring(stage.field()).degree())
    lifted = root.change_level(total_degree)
    field, value, embedding = lifted.as_finite_field_element()
    if field is not _engine_ring(stage.field()):
        raise ValueError(
            f"the finite field {stage.field()} does not contain the root of unity {root}, "
            f"which lies in {field}"
        )
    if embedding(value) != root:
        raise ValueError(
            f"the element {value} of {field} does not map to the chosen root {root} "
            f"of the algebraic closure"
        )
    return _owned_engine_element(stage.field(), value)


def _cyclotomic_stage(domain, n):
    r"""Private computation adapter: the stage ``K(zeta_n)`` and the chosen ``zeta_n``.

    Declared under ``OWN-06``. Caller: ``CyclotomicCharacter`` only, after
    the operation is selected by the placement of ``domain``. It selects
    Sage's ``zeta(n)`` in the engine closure, and over ``QQ`` the cyclotomic
    field ``QQ[x]/(Phi_n)`` with its embedding ``x -> zeta_n``; over ``F_q``
    the unique subfield of degree ``ord_n(q)``. It returns owned values: the
    root in ``Kbar``, the root in the stage field, and the stage.
    """
    from sage_extensions.categories.rings.number_fields import OwnedNumberFields
    from sage_extensions.categories.rings.ring_foundation import PrimeFields

    closure = _engine_ring(domain.algebraic_closure())
    root = closure.zeta(int(n))
    owned_root = _owned_engine_element(domain.algebraic_closure(), root)
    base_field = domain.base_field()
    match domain:
        case _ if domain in AbsoluteGaloisGroupsOfFiniteFields():
            integers = _owned_integers()
            residues = integers.quotient_ring(integers.ideal(integers(n)))
            q = residues.unit_group()(residues(int(domain.base_field_order())))
            stage = domain.finite_extension(q.multiplicative_order())
            return owned_root, _finite_root_at_stage(root, stage), stage
        case _ if base_field in OwnedNumberFields() and base_field in PrimeFields() and n == 2:
            return owned_root, base_field(-1), domain.extension_data(base_field)
        case _ if base_field in OwnedNumberFields() and base_field in PrimeFields():
            # Phi_n is irreducible over QQ (Gauss), so QQ[x]/(Phi_n) is the
            # field QQ(zeta_n), embedded by x -> zeta_n.  The embedding and
            # the generator are built on the owned field's own realization.
            from sage_extensions.categories.rings.number_fields import CyclotomicField

            owned_field = CyclotomicField(int(n), f"zeta_{n}")
            field = _engine_ring(owned_field)
            embedding = owned_field.Mor(domain.algebraic_closure())._from_engine_morphism(field.hom([root], closure))
            stage = domain.extension_data(owned_field, embedding=embedding)
            return owned_root, _owned_engine_element(owned_field, field.gen()), stage
        case _:
            assert False, (
                f"the cyclotomic character chi_{n} of {domain} is constructed only when "
                f"the base field is finite or QQ, but it is {base_field}"
            )


def _root_of_unity_exponent(closure, value, root, n):
    r"""Private computation adapter: the exponent ``a mod n`` with ``value = root^a`` in ``mu_n``.

    Declared under ``OWN-06``. Caller: ``CyclotomicCharacter._call_`` only,
    with ``root`` a primitive ``n``-th root of unity in the owned closure and
    ``value`` an ``n``-th root of unity there. It lowers both to the engine
    closure and calls Sage's generic ``discrete_log`` in the cyclic group of
    order ``n`` generated by ``root``; it returns the owned integer exponent.
    """
    exponent = discrete_log(
        _engine_element(closure, value),
        _engine_element(closure, root),
        ord=int(n),
    )
    return _owned_engine_element(ZZ, ZZ(exponent))


class CyclotomicCharacter(ProfiniteCharacter):
    r"""The continuous character (\chi_n:G_K\to(\mathbb Z/n)^{\times}).

    ``chi_n(sigma)`` is the unit ``a`` with ``sigma(zeta) = zeta^a`` for every
    ``n``-th root of unity ``zeta`` (Mathlib ``modularCyclotomicCharacter``,
    ``Mathlib/NumberTheory/Cyclotomic/CyclotomicCharacter.lean``). Its codomain
    is ``(ZZ/n)^x``, the unit group of the owned ring ``ZZ/(n)``.
    """

    @staticmethod
    def __classcall_private__(cls, domain, n):
        n = ZZ(n)
        if n < 2:
            raise ValueError(
                f"the cyclotomic character chi_n needs n >= 2, but n = {n}"
            )
        characteristic = ZZ(int(domain.characteristic()))
        if characteristic and gcd(int(n), int(characteristic)) != 1:
            raise ValueError(
                f"the cyclotomic character chi_{n} of {domain} needs n prime to the "
                f"characteristic, but the base field has characteristic {characteristic}"
            )
        integers = _owned_integers()
        residues = integers.quotient_ring(integers.ideal(integers(n)))
        target = residues.unit_group()
        owned_root, root_at_stage, stage = _cyclotomic_stage(domain, n)
        return domain.continuous_morphisms_to(target)._from_realization_engine(
            cls, n, residues, owned_root, root_at_stage, stage
        )

    def __init__(self, parent, modulus, residues, root, root_at_stage, extension) -> None:
        self._modulus = modulus
        self._residues = residues
        self._root = root
        self._root_at_stage = root_at_stage
        super().__init__(parent, extension)

    kernel = ProfiniteCharacter._root_generated_kernel

    def modulus(self):
        return self._modulus

    def primitive_root(self):
        return self._root

    def _call_(self, element):
        r"""``chi_n(sigma)``: the unit ``a`` with ``sigma(zeta) = zeta^a`` for the chosen root ``zeta``.

        Routed by the placement of ``G_K``. Over ``F_q`` an element given as a
        power ``Frob^e`` of the ``q``-Frobenius, which raises
        roots of unity to the ``q``-th power, so the value is the residue of
        ``q^e``. Otherwise ``sigma(zeta)`` is read on the stage ``K(zeta_n)``
        and ``a`` is its discrete logarithm to the base ``zeta`` in ``mu_n``.
        """
        element = self.domain()(element)
        units = self.codomain()
        match self.domain():
            case domain if (
                domain in AbsoluteGaloisGroupsOfFiniteFields()
                and element.frobenius_exponent() is not None
            ):
                q = self._residues(int(domain.base_field_order()))
                return units(q ** int(element.frobenius_exponent()))
            case _:
                coordinate = element.restriction_coordinate(self.factor_extension())
                if coordinate is not None:
                    image = self.factor_extension().embedding()(coordinate(self._root_at_stage))
                else:
                    image = element(self._root)
                residue = _root_of_unity_exponent(
                    self.domain().algebraic_closure(), image, self._root, self._modulus
                )
                return units(self._residues(int(residue)))

    def value_at_frobenius_class(self, frobenius_class):
        r"""``chi_n`` on the Frobenius class at a prime ``p`` of ``K`` with ``|O_K/p| = q`` prime to ``n``.

        A Frobenius at a prime above ``p`` sends every ``n``-th root of unity
        ``zeta`` to ``zeta^q`` when ``n`` is prime to ``p`` (Mathlib
        ``AlgHom.IsArithFrobAt.apply_of_pow_eq_one``,
        ``Mathlib/RingTheory/Frobenius.lean:107-110``), so by
        ``modularCyclotomicCharacter.toFun_unique``
        (``Mathlib/NumberTheory/Cyclotomic/CyclotomicCharacter.lean``) the
        value is the residue of ``q``, the same at every prolongation.
        """
        assert frobenius_class.supergroup() is self.domain(), (
            f"{frobenius_class} is a class of {frobenius_class.supergroup()}, not of "
            f"the domain {self.domain()} of {self}"
        )
        q = ZZ(int(frobenius_class.residue_field_cardinality()))
        assert gcd(int(q), int(self._modulus)) == 1, (
            f"the value of {self} on {frobenius_class} is the residue of q = {q} only "
            f"when q is prime to {self._modulus}"
        )
        return self.codomain()(self._residues(int(q)))

    def _repr_(self) -> str:
        return f"Cyclotomic character chi_{self._modulus}: {self.domain()} -> {self.codomain()}"


class QuadraticCharacter(ProfiniteCharacter):
    r"""The character attached to (K(\sqrt a)/K) in characteristic not two."""

    @staticmethod
    def __classcall_private__(cls, domain, a):
        characteristic = ZZ(int(domain.characteristic()))
        if characteristic == 2:
            raise ValueError(
                f"the quadratic character of K(sqrt({a}))/K for {domain} needs "
                f"characteristic different from 2, but the base field has characteristic 2"
            )
        base_field = domain.base_field()
        base = _engine_ring(base_field)
        owned_a = base_field(a)
        backend_a = base(_engine_element(base_field, owned_a))
        if not backend_a:
            raise ValueError(
                f"the quadratic character of K(sqrt(a))/K needs a nonzero a in {base_field}, "
                f"but a = {owned_a}"
            )
        closure = _engine_ring(domain.algebraic_closure())
        embedded_a = domain.base_embedding()(owned_a)
        root = _engine_element(domain.algebraic_closure(), embedded_a).sqrt()
        owned_root = _owned_engine_element(domain.algebraic_closure(), closure(root))

        if backend_a.is_square():
            stage = domain.extension_data(domain.base_field())
            root_at_stage = _owned_engine_element(domain.base_field(), backend_a.sqrt())
            # Retain the exact image of the selected stage root: independent
            # square-root choices in K and its closure can differ by a sign.
            owned_root = domain.base_embedding()(root_at_stage)
        elif domain in AbsoluteGaloisGroupsOfFiniteFields():
            stage = domain.finite_extension(2)
            root_at_stage = _finite_root_at_stage(root, stage)
        else:
            # K(sqrt a) = K[t]/(t^2 - a), a not a square in K; the embedding
            # and the generator are built on its own realization.
            polynomial_ring = base_field.polynomial_ring("t")
            t = polynomial_ring.algebra_generator("t")
            owned_field = (t**2 - polynomial_ring(owned_a)).number_field("sqrt_a")
            field = _engine_ring(owned_field)
            backend = field.hom([root], closure)
            embedding = owned_field.Mor(domain.algebraic_closure())._from_engine_morphism(backend)
            stage = domain.extension_data(owned_field, embedding=embedding)
            root_at_stage = _owned_engine_element(owned_field, field.gen())

        integers = _owned_integers()
        return domain.continuous_morphisms_to(integers.unit_group())._from_realization_engine(
            cls, owned_a, owned_root, root_at_stage, stage
        )

    def __init__(self, parent, square_class, root, root_at_stage, extension) -> None:
        self._square_class = square_class
        self._root = root
        self._root_at_stage = root_at_stage
        self._integers = _owned_integers()
        super().__init__(parent, extension)

    kernel = ProfiniteCharacter._root_generated_kernel

    def square_class(self):
        return self._square_class

    def square_root(self):
        return self._root

    def _call_(self, element):
        r"""The sign ``e`` in ``ZZ^x`` with ``sigma(sqrt(a)) = e sqrt(a)``."""
        element = self.domain()(element)
        coordinate = element.restriction_coordinate(self.factor_extension())
        if coordinate is not None:
            image = self.factor_extension().embedding()(coordinate(self._root_at_stage))
        else:
            image = element(self._root)
        match image == self._root, image == -self._root:
            case True, _:
                return self.codomain()(self._integers(1))
            case _, True:
                return self.codomain()(self._integers(-1))
            case False, False:
                raise ValueError(
                    f"{element} sends sqrt({self._square_class}) = {self._root} to {image}, which is "
                    f"neither sqrt({self._square_class}) nor its negative, so {element} does not "
                    f"preserve the quadratic extension"
                )
            case _:
                assert False, (
                    f"evaluating {self} at {element} needs a decision whether its image "
                    f"{image} equals the retained root {self._root} or its negative; "
                    "the available equality computations leave the sign undecided"
                )

    def _repr_(self) -> str:
        return f"Quadratic character for {self._square_class}: {self.domain()} -> {self.codomain()}"


__all__ = [
    "CyclotomicCharacter",
    "ProfiniteCharacter",
    "QuadraticCharacter",
    "RestrictedProfiniteCharacter",
]
