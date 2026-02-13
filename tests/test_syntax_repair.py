from src.agents.fixer import FixerAgent


def test_syntax_repair_on_messy_code():
    fixer = FixerAgent()
    with open('sandbox/messy_code.py', 'r', encoding='utf-8') as f:
        original = f.read()

    fixed = fixer._apply_syntax_fixes(original)
    assert fixed is not None, "Syntax fixer should return a non-None result"

    # The fixed code should parse as python
    import ast
    ast.parse(fixed)

    # And it should contain at least one def or class
    assert 'def ' in fixed or 'class ' in fixed
