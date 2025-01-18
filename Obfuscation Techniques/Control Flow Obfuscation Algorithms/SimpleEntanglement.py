import ast
import random
import sys
from constants import imports, execute_circuit, measure_all

# This Obfuscation is meant to work on code that contains only one function definition
def extract_random_function_and_imports(file_path):
    with open(file_path, 'r') as file:
        tree = ast.parse(file.read())

    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
    imports = [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))]
    return random.choice(functions) if functions else None, imports, tree.body


def indent_function_body(function_code):
    lines = function_code.split('\n')
    indented_lines = [lines[0]] + ['    ' + line if line else line for line in lines[1:]]
    return '\n'.join(indented_lines)


def modularize_simple_entanglement(sample_code_path, simple_entanglement_code):
    random_function, imports, sample_code_body = extract_random_function_and_imports(sample_code_path)
    if random_function is None:
        raise ValueError("No function found in the sample code")

    # Remove repeated imports from the sample code imports list
    unique_imports = {}
    for node in imports:
        for alias in node.names:
            unique_imports[alias.name] = node

    # Convert the selected function and imports back to code
    random_function_code = indent_function_body(ast.unparse(random_function))
    imports_code = "\n".join(ast.unparse(node) for node in unique_imports.values())
    sample_code_body.remove(random_function)
    sample_code = "\n".join(
        ast.unparse(node) for node in sample_code_body if not isinstance(node, (ast.Import, ast.ImportFrom)))

    # Integrate the obfuscated functions with the code, ensuring they are not adjacent
    new_code = f"""
{imports_code}

{simple_entanglement_code}

# Obfuscated quantum execution
qr = QuantumRegister(2)
cr = ClassicalRegister(2)
qc = QuantumCircuit(qr, cr)

create_entangled_pair(qc, qr)
measure_all(qc, qr, cr)
result = list(execute_circuit(qc).keys())[0]


if result == '00' or result == '11':
    {random_function_code}

elif result == '01':
    def run_bell_state():
        # You may change this function to do something else entirely
        qr = QuantumRegister(2)
        cr = ClassicalRegister(2)
        qc = QuantumCircuit(qr, cr)
        qc.h(qr[0])
        qc.cx(qr[0], qr[1])
        measure_all(qc, qr, cr)
        print("Bell State Algorithm result")
        print(qc.draw(output='text'))
        circuit_drawer(qc, output='mpl', style='clifford')

elif result == '10':
    # You may add another function here        
    def fibonacci_sequence(n=20):
        print(f"Fibonacci Sequence up to {{n}} terms:")
        fib = [0, 1]
        while len(fib) < n:
            fib.append(fib[-1] + fib[-2])
        print(fib)
{sample_code} 
"""
    return new_code


def main():
    if len(sys.argv) != 2:
        print("Usage: python SimpleEntanglement.py <sample_code_path>")
        sys.exit(1)

    sample_code_path = sys.argv[1]
    
    simple_entanglement_code = f'''
{imports}

from qiskit.visualization import circuit_drawer

def create_entangled_pair(qc, qr):
    qc.h(qr[0])
    qc.cx(qr[0], qr[1])

{measure_all}
{execute_circuit}
'''

    new_code = modularize_simple_entanglement(sample_code_path, simple_entanglement_code)

    output_file = 'ObfuscatedSimpleEntanglement.py'
    with open(output_file, 'w') as file:
        file.write(new_code)

    print(f"Obfuscated code written to {output_file}")


if __name__ == "__main__":
    main()
