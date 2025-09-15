"""Remove all @dataclass decorators from AST file"""

# Read the file
with open('synapse_lang/synapse_ast_enhanced.py', 'r') as f:
    lines = f.readlines()

# Process lines
output_lines = []
skip_next = False
for i, line in enumerate(lines):
    if skip_next:
        skip_next = False
        continue
    if line.strip() == '@dataclass':
        skip_next = False  # Don't skip the next line, just skip this one
        continue
    output_lines.append(line)

# Write back
with open('synapse_lang/synapse_ast_enhanced.py', 'w') as f:
    f.writelines(output_lines)

print("Removed all @dataclass decorators")