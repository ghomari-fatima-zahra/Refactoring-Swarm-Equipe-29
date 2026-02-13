import re
s=open('sandbox/messy_code.py','r',encoding='utf-8').read()
lines=s.split('\n')
fixed_lines=lines.copy()
# 1) Add missing colon
for i,line in enumerate(fixed_lines):
    stripped=line.strip()
    if (stripped.startswith('def ') or stripped.startswith('class ')) and not stripped.endswith(':'):
        fixed_lines[i]=line+':'
# 2) indent body
for i,line in enumerate(fixed_lines[:-1]):
    if line.strip().startswith(('def ','class ')):
        next_line=fixed_lines[i+1]
        if next_line.strip() and not next_line.startswith((' ','\t')):
            fixed_lines[i+1]='    '+next_line
# 3) close parentheses
for i,line in enumerate(fixed_lines):
    if line.count('(')>line.count(')'):
        fixed_lines[i]=line + ')'*(line.count('(')-line.count(')'))
# 4) close quotes but skip triple-quote lines
for i,line in enumerate(fixed_lines):
    if '"""' in line or "'''" in line:
        continue
    for quote in ('"', "'"):
        if line.count(quote)%2==1:
            fixed_lines[i]=line+quote
# 5) commas in lists

def fix_list_commas(s):
    def repl(m):
        return m.group(1)+', '+m.group(2)
    return re.sub(r'(\d)\s+(\d)', repl, s)

joined='\n'.join(fixed_lines)
joined=re.sub(r"\[([^\]]+)\]", lambda m: '['+fix_list_commas(m.group(1))+']', joined)
# handle triple quote counts
if joined.count('"""')%2==1:
    joined=joined+'\n"""'
if joined.count("'''")%2==1:
    joined=joined+"\n'''"
print('----JOINED----')
print(joined)
import ast
try:
    ast.parse(joined)
    print('PARSES OK')
except Exception as e:
    print('PARSE ERR:', e)
