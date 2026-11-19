"""Turns pytest's report.xml into the table on the Actions run page.

Used by .github/workflows/tests.yml:
    python .github/test_summary.py report.xml >> $GITHUB_STEP_SUMMARY
"""
import ast
import sys
import xml.etree.ElementTree as ET


def checks(path, name):
    """The assert lines of one test, as written in the test file."""
    try:
        src = open(path).read()
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.FunctionDef) and node.name == name:
                lines = [ast.get_source_segment(src, n) for n in ast.walk(node)
                         if isinstance(n, ast.Assert)]
                return "<br>".join(f"`{l}`" for l in lines[:3]) + (
                    " ..." if len(lines) > 3 else "")
    except (OSError, SyntaxError):
        pass
    return ""


rows = []
for case in ET.parse(sys.argv[1]).iter("testcase"):
    path = case.get("classname", "").replace(".", "/") + ".py"
    name = case.get("name")
    bad = case.find("failure")
    if bad is None:
        bad = case.find("error")
    msg = "" if bad is None else (bad.get("message") or "").splitlines()[0]
    msg = msg.replace("|", "\\|")[:120]
    rows.append((bad is not None, path, name, msg))

failed = [r for r in rows if r[0]]
passed = [r for r in rows if not r[0]]
print(f"## Unit tests: {len(passed)} passed, {len(failed)} failed\n")
if failed:
    print("| test | what it checks | what happened |\n|---|---|---|")
    for _, path, name, msg in failed:
        print(f"| ✗ `{name}` | {checks(path, name)} | {msg} |")
print(f"\n<details><summary>{len(passed)} passed</summary>\n")
for _, path, name, _ in passed:
    print(f"- ✓ `{path.split('/')[-1]}` `{name}`")
print("\n</details>")
