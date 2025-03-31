import ast
import random
import sys


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


def modularize_opaque_pred(sample_code_path, opaque_pred_code):
    random_function, imports, sample_code_body = extract_random_function_and_imports(sample_code_path)
    if random_function is None:
        wrapper = ast.FunctionDef(
            name="__wrapped_main__",
            args=ast.arguments(posonlyargs=[], args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None,
                               defaults=[]),
            body=sample_code_body.copy(),
            decorator_list=[]
        )
        random_function = ast.fix_missing_locations(wrapper)
        sample_code_body.clear()

    # Remove repeated imports from the sample code imports list
    unique_imports = {}
    for node in imports:
        for alias in node.names:
            unique_imports[alias.name] = node

    # Convert the selected function and imports back to code
    random_function_code = indent_function_body(ast.unparse(random_function))
    imports_code = "\n".join(ast.unparse(node) for node in unique_imports.values())
    try:
        sample_code_body.remove(random_function)
    except ValueError:
        pass
    sample_code = "\n".join(
        ast.unparse(node) for node in sample_code_body if not isinstance(node, (ast.Import, ast.ImportFrom)))

    # Integrate everything into the new obfuscated code
    new_code = f"""
{imports_code}

{opaque_pred_code}

num_pairs = 8
counts = entangler(num_pairs)

if sum(int(bit) for bit in max(counts, key=counts.get)) == num_pairs * 2:
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
    os.execv(sys.executable, ['python'] + sys.argv)
else:
    {random_function_code}

{sample_code}    
"""
    return new_code


def main():
    if len(sys.argv) != 2:
        print("Usage: python EntangleObf.py <sample_code_path>")
        sys.exit(1)

    sample_code_path = sys.argv[1]
    opaque_pred_code = """
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import circuit_drawer
import os, sys

def create_entangled_pairs(qc, qr):
    for i in range(0, qr.size, 2):
        qc.h(qr[i])
        qc.cx(qr[i], qr[i + 1])

def measure_all(qc, qr, cr):
    qc.measure(qr, cr)

def execute_circuit(qc, backend_name=AerSimulator(), shots=1024):
    backend = backend_name
    # Transpile the circuit for the backend
    transpiled_circuit = transpile(qc, backend)
    result = backend.run(transpiled_circuit, shots=shots).result()
    return result.get_counts()

def entangler(num_pairs):
    qr = QuantumRegister(num_pairs * 2)
    cr = ClassicalRegister(num_pairs * 2)
    qc = QuantumCircuit(qr, cr)
    create_entangled_pairs(qc, qr)
    measure_all(qc, qr, cr)
    counts = execute_circuit(qc)
    return counts

    print("Simulator result")
    for outcome, count in counts.items():
        print(f"{outcome} is observed {count} times")

    print(qc.draw(output='text'))
"""

    new_code = modularize_opaque_pred(sample_code_path, opaque_pred_code)

    output_file = 'ObfuscatedEntangleObf.py'
    with open(output_file, 'w') as file:
        file.write(new_code)

    print(f"Modularized code written to {output_file}")


if __name__ == "__main__":
    main()
