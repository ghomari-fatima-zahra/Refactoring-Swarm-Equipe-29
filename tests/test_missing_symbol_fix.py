from src.agents.fixer import FixerAgent


def test_missing_symbol_fix_appends_stub():
    fixer = FixerAgent()
    issue = {'issue_type': 'MISSING_SYMBOL', 'description': "Missing symbol 'foo'"}
    original = "def a():\n    return 1\n"

    fixed = fixer._apply_predefined_fix(issue, original)
    assert fixed is not None
    assert "def foo" in fixed
    assert "return None" in fixed
