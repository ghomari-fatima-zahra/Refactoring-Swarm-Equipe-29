import re
from src.agents.fixer import FixerAgent


def test_apply_predefined_fix_filenotfound():
    fixer = FixerAgent()
    issue = {'issue_type': 'FileNotFoundError', 'description': 'FileNotFoundError when opening file'}
    original_code = "def read_file(path):\n    f = open(path, 'r')\n    return f.read()\n"

    fixed = fixer._apply_predefined_fix(issue, original_code)
    assert fixed is not None
    assert 'try:' in fixed
    assert 'except FileNotFoundError' in fixed


def test_apply_predefined_fix_attribute_none():
    fixer = FixerAgent()
    issue = {'issue_type': 'AttributeError', 'description': 'AttributeError: NoneType has no attribute strip'}
    original_code = "def clean(x):\n    return x.strip()\n"

    fixed = fixer._apply_predefined_fix(issue, original_code)
    assert fixed is not None
    # Ensure we added an is None guard
    assert 'if x is None' in fixed


def test_apply_predefined_fix_zero_division_existing():
    fixer = FixerAgent()
    issue = {'issue_type': 'ZeroDivisionError', 'description': 'ZeroDivisionError in division operation'}
    original_code = "def div(a, b):\n    return a / b\n"

    fixed = fixer._apply_predefined_fix(issue, original_code)
    assert fixed is not None
    assert 'if b == 0' in fixed or 'if b == 0:' in fixed
