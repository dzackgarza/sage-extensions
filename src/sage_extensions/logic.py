r"""Predicates whose truth can be asked without coercing uncertainty to false.

The preamble uses ordinary booleans when a proposition is already decided.
When a mathematical relation is not decided at construction time, it returns
a :class:`Predicate`.  ``ask(P)`` evaluates the predicate; if the available
exact/certified procedures still do not decide it, the answer is Sage's
``Unknown``.

A predicate here is a closed proposition ``R(x)``: the value
``chi_R(x)`` of the characteristic morphism ``chi_R : X -> Delta[1]`` of a
relation ``R`` on a set ``X`` at a point ``x``, whose computation is deferred.
``ask`` is the knowledge question about that value, so its codomain is
``True | False | Unknown`` (`DEF-06`).
"""

from sage.misc.abstract_method import abstract_method
from sage.misc.unknown import Unknown, UnknownClass
from sage.structure.element import parent as element_parent

from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.owned_category import _object_of


class _PropositionElement:
    r"""Private element realization for a represented closed proposition."""

    def __init__(self, parent=None) -> None:
        super().__init__(Propositions if parent is None else parent)

    @abstract_method
    def _ask_(self, *, max_prec: int = 4096) -> bool | UnknownClass:
        r"""Evaluate ``self`` as far as the predicate's algorithms permit.

        Protected contract (`OWN-05`).  Owner: :class:`Predicate`.  Implemented
        by each concrete proposition, which owns its decision algorithm; called
        only through the dispatcher :func:`ask`.  Returns ``True`` or
        ``False`` when the proposition is decided within the precision budget
        ``max_prec`` and ``Unknown`` otherwise; it never answers ``False`` for
        an undecided proposition.
        """
        ...

    def __bool__(self):
        raise TypeError(f"the proposition {self} has no Python truth value, because it may be undecided; call ask(...) on it to get True, False or Unknown")


class _PropositionSetEngine:
    r"""Private realization of the set of represented closed propositions."""

    def __init__(self, **rest) -> None:
        super().__init__(**rest)

    def __contains__(self, statement) -> bool:
        return element_parent(statement) is self

    is_parent_of = __contains__

    def _element_constructor_(self, statement):
        if element_parent(statement) is self:
            return statement
        raise TypeError(f"{statement!r} cannot be converted into a proposition: a proposition is constructed from its defining relation")

    def _repr_(self) -> str:
        return "Set of represented closed propositions"


Propositions = _object_of(
    Sets(),
    _engine=(Sets(), _PropositionSetEngine, _PropositionElement),
)
Predicate = Propositions.element_class


class AtomicProposition(Predicate):
    r"""The closed atomic proposition \(R(x_1, \dots, x_n)\) that no procedure decides.

    An exact predicate decides every case that its data decides and returns
    ``True`` or ``False``.  On the remaining cases it returns this
    proposition: the relation \(R\), named by ``relation``, at the points
    ``x_i``.  The predicate that constructs it has already run each procedure
    that applies, so ``ask`` of it is ``Unknown`` (`DEF-06`).
    """

    def __init__(self, relation: str, *points) -> None:
        self._relation = relation
        self._points = points
        super().__init__()

    def relation(self) -> str:
        return self._relation

    def points(self):
        return self._points

    def _ask_(self, *, max_prec: int = 4096) -> UnknownClass:
        return Unknown

    def _repr_(self) -> str:
        return f"{self._relation}({', '.join(repr(point) for point in self._points)})"


class Negation(Predicate):
    r"""The proposition \(\neg P\) of an undecided proposition \(P\)."""

    def __init__(self, statement: Predicate) -> None:
        self._statement = statement
        super().__init__()

    def negated(self) -> Predicate:
        return self._statement

    def _ask_(self, *, max_prec: int = 4096) -> bool | UnknownClass:
        answer = ask(self._statement, max_prec=max_prec)
        return answer if answer is Unknown else not answer

    def _repr_(self) -> str:
        return f"not {self._statement!r}"


class Conjunction(Predicate):
    r"""The proposition \(P_1 \wedge \dots \wedge P_n\) of undecided propositions."""

    def __init__(self, statements) -> None:
        self._statements = statements
        super().__init__()

    def conjuncts(self):
        return self._statements

    def _ask_(self, *, max_prec: int = 4096) -> bool | UnknownClass:
        answers = tuple(ask(statement, max_prec=max_prec) for statement in self._statements)
        if any(answer is False for answer in answers):
            return False
        if any(answer is Unknown for answer in answers):
            return Unknown
        return True

    def _repr_(self) -> str:
        return " and ".join(repr(statement) for statement in self._statements)


def negation(statement: bool | Predicate) -> bool | Predicate:
    r"""The negation of a proposition, decided when ``statement`` is decided."""
    match statement:
        case _ if statement is True or statement is False:
            return not statement
        case Predicate():
            return Negation(statement)
        case _:
            raise TypeError(f"negation(...) takes True, False or a proposition, but was given {statement!r}")


def conjunction(statements) -> bool | Predicate:
    r"""The conjunction of propositions.

    ``False`` when one conjunct is ``False``, ``True`` when every conjunct is
    ``True``, and otherwise the conjunction of the undecided conjuncts.
    """
    undecided = []
    for statement in statements:
        match statement:
            case _ if statement is False:
                return False
            case _ if statement is True:
                pass
            case Predicate():
                undecided.append(statement)
            case _:
                raise TypeError(f"conjunction(...) takes True, False or propositions, but was given {statement!r}")
    match undecided:
        case []:
            return True
        case [single]:
            return single
        case _:
            return Conjunction(tuple(undecided))


def ask(
    statement: bool | UnknownClass | Predicate,
    *,
    max_prec: int = 4096,
) -> bool | UnknownClass:
    r"""Return the truth value of ``statement``, or ``Unknown`` if undecided.

    ``True`` and ``False`` pass through unchanged.  Predicates own their
    evaluation algorithms.  ``Unknown`` also passes through, so callers can
    compose this with existing Sage three-valued predicates.
    """
    match statement:
        case _ if statement is True or statement is False or statement is Unknown:
            return statement
        case Predicate():
            answer = statement._ask_(max_prec=max_prec)
            assert answer is True or answer is False or answer is Unknown, f"deciding the proposition {statement} returned {answer!r}, which is not True, False or Unknown"
            return answer
        case _:
            raise TypeError(f"ask(...) decides True, False, Unknown or a proposition, but was given {statement!r}")


__all__ = [
    "AtomicProposition",
    "Conjunction",
    "Negation",
    "Predicate",
    "Propositions",
    "Unknown",
    "ask",
    "conjunction",
    "negation",
]
