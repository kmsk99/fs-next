"""Compare source-level API inventory against an unpacked upstream fs package.

Usage: python scripts/check_upstream_api.py path/to/fs-2.4.16/fs fs
This checks names/signatures, not equivalence of every possible runtime behavior.
"""

import argparse
import ast
import json
from pathlib import Path


def inventory(root):
    symbols = {}
    assignments = set()

    def visit(nodes, prefix):
        for node in nodes:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                name = prefix + "." + node.name
                if not node.name.startswith("_") or node.name in (
                    "__init__",
                    "__enter__",
                    "__exit__",
                ):
                    symbols[name] = node.args if hasattr(node, "args") else None
                if isinstance(node, ast.ClassDef):
                    visit(node.body, name)
            elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = (
                    node.targets if isinstance(node, ast.Assign) else [node.target]
                )
                for target in targets:
                    if isinstance(target, ast.Name) and not target.id.startswith("_"):
                        assignments.add(prefix + "." + target.id)
            elif isinstance(node, (ast.If, ast.Try)):
                visit(node.body, prefix)
                visit(node.orelse, prefix)
                if isinstance(node, ast.Try):
                    visit(node.finalbody, prefix)
                    for handler in node.handlers:
                        visit(handler.body, prefix)

    modules = {str(p.relative_to(root)) for p in root.rglob("*.py")}
    for module in sorted(modules):
        visit(ast.parse((root / module).read_text(encoding="utf-8")).body, module)
    return modules, symbols, assignments


def compatible(old, new):
    if old is None or new is None:
        return old is new

    # Existing positional arguments must keep their order, names and defaults.
    def positional(args):
        names = [arg.arg for arg in args.posonlyargs + args.args]
        defaults = [None] * (len(names) - len(args.defaults)) + [
            ast.dump(value) for value in args.defaults
        ]
        return list(zip(names, defaults))

    before, after = positional(old), positional(new)
    if after[: len(before)] != before or any(
        d is None for _, d in after[len(before) :]
    ):
        return False
    if len(old.posonlyargs) != len(new.posonlyargs):
        return False
    for field in ("vararg", "kwarg"):
        a, b = getattr(old, field), getattr(new, field)
        if (a.arg if a else None) != (b.arg if b else None):
            return False
    return ast.dump(
        ast.arguments(
            posonlyargs=[],
            args=[],
            kwonlyargs=old.kwonlyargs,
            kw_defaults=old.kw_defaults,
            defaults=[],
        )
    ) == ast.dump(
        ast.arguments(
            posonlyargs=[],
            args=[],
            kwonlyargs=new.kwonlyargs,
            kw_defaults=new.kw_defaults,
            defaults=[],
        )
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    modules, symbols, assignments = inventory(args.baseline)
    current_modules, current, current_assignments = inventory(args.candidate)
    if not modules or not symbols:
        raise SystemExit("Baseline contains no Python API")
    report = {
        "baseline_modules": len(modules),
        "candidate_modules": len(current_modules),
        "baseline_definitions": len(symbols),
        "candidate_definitions": len(current),
        "missing_modules": sorted(modules - current_modules),
        "missing_definitions": sorted(symbols.keys() - current.keys()),
        "missing_assignments": sorted(assignments - current_assignments),
        "incompatible_signatures": sorted(
            name
            for name in symbols.keys() & current.keys()
            if not compatible(symbols[name], current[name])
        ),
        "extended_signatures": sorted(
            name
            for name in symbols.keys() & current.keys()
            if symbols[name] is not None
            and current[name] is not None
            and compatible(symbols[name], current[name])
            and ast.dump(symbols[name]) != ast.dump(current[name])
        ),
    }
    print(json.dumps(report, indent=2))
    if any(
        report[key]
        for key in (
            "missing_modules",
            "missing_definitions",
            "missing_assignments",
            "incompatible_signatures",
        )
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
