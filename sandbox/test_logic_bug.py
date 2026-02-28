from logic_bug import count_down
import io
import sys

def test_count_down():
    capturedOutput = io.StringIO() 
    sys.stdout = capturedOutput 
    count_down(5)
    sys.stdout = sys.__stdout__ 
    assert capturedOutput.getvalue() != ""