from messy_code import check_grade

def test_check_grade():
    assert check_grade(0) == "Invalid"
    assert check_grade(25) == "Fail"
    assert check_grade(50) == "Pass"
    assert check_grade(75) == "Excellent"
    assert check_grade(100) == "Excellent"
    assert check_grade(-10) == "Invalid"