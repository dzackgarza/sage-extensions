default:
    @just --list

# Detect coordinate conventions written outside the tensor package (OWN-24).
# AST provenance, not identical source-line text, exempts the typed Mor
# transpose. Encoding Smith coordinates as ordinal indices is not a pairing.
# The scan is necessary but not sufficient: semantic ownership needs review.
# scope=staged is an optional focused check; scope=all is the CI diagnostic.
tensor-boundary scope="all":
    #!/usr/bin/env bash
    set -uo pipefail
    case "{{scope}}" in
        all) files=$(git ls-files 'src/sage_extensions/*.py' \
            | grep -v '^src/sage_extensions/tensors/') || exit 1 ;;
        staged) files=$(git diff --cached --name-only --diff-filter=ACMR -- 'src/sage_extensions/*.py' \
            | grep -v '^src/sage_extensions/tensors/')
            if [ -z "$files" ]; then
                echo "tensor-boundary: no staged sage_extensions Python files."
                exit 0
            fi ;;
        *) echo "tensor-boundary scope must be all or staged, not {{scope}}" >&2; exit 2 ;;
    esac
    total=0
    for pattern in '$X.transpose()' '$X.T' '$X.matrix_action_right($$$A)' '$X.matrix_action_left($$$A)' '$X.einsum($$$A)' 'einsum($$$A)' '$X.matmul($$$A)' 'matmul($$$A)' '$X.dot($$$A)' '$X @ $Y'; do
        matches=$(ast-grep run --lang python --pattern "$pattern" --json $files)
        status=$?
        # ast-grep returns 1 for a valid query with zero matches.
        if [ "$status" -gt 1 ]; then
            echo "tensor-boundary scanner failed (status $status) for $pattern" >&2
            exit "$status"
        fi
        if ! findings=$(printf '%s\n' "$matches" | python3 -c '
    import ast, json, pathlib, sys
    for hit in json.load(sys.stdin):
        path = hit["file"]
        line = hit["range"]["start"]["line"] + 1
        source = pathlib.Path(path).read_text()
        tree = ast.parse(source, filename=path)

        # The owned MatrixSpaces.ElementMethods implementation makes product
        # by composing two elements of the module Mor. Its transpose is a Mor
        # element with reversed endpoints, not a Sage-matrix convention.
        if (path == "src/sage_extensions/categories/modules/pure/modules.py"
                and hit["text"] == "product.transpose()"):
            owned_transpose = False
            for method in ast.walk(tree):
                if not isinstance(method, ast.FunctionDef) or method.name != "symmetrized_right_multiplication":
                    continue
                has_mor = any(isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "parameters" for t in n.targets)
                    and ast.unparse(n.value) == "modules.Mor(self.codomain(), self.domain())"
                    for n in method.body)
                for image in method.body:
                    if not isinstance(image, ast.FunctionDef) or image.name != "image":
                        continue
                    has_composition = any(isinstance(n, ast.Assign)
                        and any(isinstance(t, ast.Name) and t.id == "product" for t in n.targets)
                        and ast.unparse(n.value) == "parameters.module_generator(label) * self"
                        for n in image.body)
                    has_call = any(isinstance(n, ast.Call) and n.lineno == line
                        and isinstance(n.func, ast.Attribute) and n.func.attr == "transpose"
                        and isinstance(n.func.value, ast.Name) and n.func.value.id == "product"
                        for n in ast.walk(image))
                    if has_mor and has_composition and has_call:
                        owned_transpose = True
                        break
                if owned_transpose:
                    break
            if owned_transpose:
                continue

        # The three existing @ strides calls encode finite tuples as their
        # mixed-radix ordinal: this is indexing, not a bilinear contraction.
        if (path == "src/sage_extensions/categories/modules/framed/formed/discriminant_modules.py"
                and hit["metaVariables"]["single"].get("Y", {}).get("text") == "strides"):
            ordinal_index = False
            for method in ast.walk(tree):
                if not isinstance(method, ast.FunctionDef) or method.name != "_isotropic_subgroups":
                    continue
                has_strides = any(isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "strides" for t in n.targets)
                    and isinstance(n.value, ast.Call) and ast.unparse(n.value.func) == "numpy.array"
                    for n in method.body)
                if has_strides and method.lineno <= line <= method.end_lineno:
                    ordinal_index = True
                    break
            if ordinal_index:
                continue

        print("{}:{}: {}".format(path, line, hit["lines"].strip()))
    '); then
            echo "tensor-boundary could not classify $pattern" >&2
            exit 1
        fi
        n=$(printf '%s\n' "$findings" | grep -c . || true)
        total=$((total + n))
        printf '%4d  %s\n' "$n" "$pattern"
        if [ "$n" -gt 0 ]; then
            printf '%s\n' "$findings" | head -40
        fi
    done
    if [ "$total" -gt 0 ]; then
        echo "$total suspected coordinate operations outside sage_extensions/tensors/: state the owned pullback, contraction, composition, inverse or application instead."
        exit 1
    fi
    echo "No prohibited syntax detected; categorical ownership still requires source review."

