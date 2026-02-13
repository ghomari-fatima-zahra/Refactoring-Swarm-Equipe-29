import re
import sys, os
sys.path.insert(0, os.path.abspath('.'))
from src.agents.judge import JudgeAgent
j=JudgeAgent()
ok, err = j.validate_with_error('sandbox')
print('OK:', ok)
print('ERR:')
print(err)
m = re.search(r"cannot import name ['\"](\w+)['\"]", err)
print('match', bool(m))
print('group', m.group(1) if m else None)
