import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

try:
    from messy_code import divide
except Exception as e:
    def test_import_failed():
        assert False, f'Import failed: {str(e)}'
else:
    def test_divide():
        try:
            result = divide(1, 2)
            assert result is not None
        except Exception as e:
            assert False, f'Function failed: {str(e)}'
