import ast
import random
import sys

# This Obfuscation is meant to work on code that contains only one function definition
def extract_random_function_and_imports(code_content):
    tree = ast.parse(code_content)
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
result = execute_circuit(qc)


if result == [0, 0]:
    {random_function_code}

elif result == [1, 1]:
    {random_function_code}

elif result == [0, 1]:
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
        
elif result == [1, 0]:
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


def seop_obfuscate_and_execute(code_content):
    simple_entanglement_code = """
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import circuit_drawer

def create_entangled_pair(qc, qr):
    qc.h(qr[0])
    qc.cx(qr[0], qr[1])

def measure_all(qc, qr, cr):
    qc.measure(qr, cr)

def execute_circuit(qc, backend_name=AerSimulator(), shots=1024):
    backend = backend_name
    # Transpile the circuit for the backend
    transpiled_circuit = transpile(qc, backend)
    result = backend.run(transpiled_circuit, shots=shots).result()
    counts = result.get_counts(qc)
    # Directly read the result from the counts
    measured_result = list(counts.keys())[0]
    return [int(bit) for bit in measured_result]
"""

    obfuscated_code = modularize_simple_entanglement(code_content, simple_entanglement_code)

    return {
        'original_code': code_content,
        'obfuscated_code': obfuscated_code,
    }


