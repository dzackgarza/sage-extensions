"""#370 probe 7b: one linear map carrying Sterk's II_(18,2) roots to their T_En images?"""
from sage.all import QQ, matrix

from sage_extensions.all import NamedLattices, Sterk

TdP = NamedLattices.TdP
TEn = NamedLattices.TEn
diagrams = Sterk.sterk_roots()
transcribed = Sterk.sterks_in_TEn()

pairs = []
for name, roots in transcribed.items():
    for source, target in zip(tuple(diagrams[name]), tuple(roots)):
        pairs.append((
            [int(entry) for entry in source.to_vector()],
            [int(entry) for entry in target.to_vector()],
        ))
rank_source = int(TdP.module_rank())
rank_target = int(TEn.module_rank())
print("pairs", len(pairs), "source rank", rank_source, "target rank", rank_target)

sources = matrix(QQ, [pair[0] for pair in pairs])
print("rank of the source vectors:", sources.rank())

rows_of_phi = []
consistent = True
for row in range(rank_target):
    rhs = matrix(QQ, [[pair[1][row]] for pair in pairs])
    try:
        solution = sources.solve_right(rhs)
    except Exception as error:  # noqa: BLE001
        print("row", row, "does not solve:", type(error).__name__)
        consistent = False
        break
    residual = sources * solution - rhs
    if any(entry != 0 for entry in residual.list()):
        print("row", row, "has a nonzero residual")
        consistent = False
        break
    rows_of_phi.append(solution)
print("one linear map for every row:", consistent, "rows solved:", len(rows_of_phi))
if consistent:
    phi = matrix(QQ, [[rows_of_phi[row][column, 0] for column in range(rank_source)]
                      for row in range(rank_target)])
    failures = 0
    for name, roots in transcribed.items():
        for source, target in zip(tuple(diagrams[name]), tuple(roots)):
            image = phi * matrix(QQ, rank_source, 1, [int(entry) for entry in source.to_vector()])
            if [image[row, 0] for row in range(rank_target)] != [int(entry) for entry in target.to_vector()]:
                failures += 1
    print("reproduction failures:", failures)
    print("phi is integral:", all(entry.denominator() == 1 for entry in phi.list()))
    for name in ("Sterk_4", "Sterk_5"):
        squares = []
        integral = 0
        for root in tuple(diagrams[name]):
            image = phi * matrix(QQ, rank_source, 1, [int(entry) for entry in root.to_vector()])
            coordinates = [image[row, 0] for row in range(rank_target)]
            if all(entry.denominator() == 1 for entry in coordinates):
                integral += 1
                squares.append(int(TEn.q(TEn([int(entry) for entry in coordinates]))))
        print(name, "integral images", integral, "of", len(tuple(diagrams[name])), "squares", squares)
