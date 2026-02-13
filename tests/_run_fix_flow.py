import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from src.agents.auditor import AuditorAgent
from src.agents.fixer import FixerAgent
import json

aud = AuditorAgent()
audits = aud.analyze('sandbox')
print('AUDIT RESPONSE:', audits)
issues = json.loads(audits)
fixer = FixerAgent()
fixer.fix('sandbox', audits)
print('\n=== AFTER FIX CONTENT ===')
print(open('sandbox/messy_code.py', 'r', encoding='utf-8').read())
