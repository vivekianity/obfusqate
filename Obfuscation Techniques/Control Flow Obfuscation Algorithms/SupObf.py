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

    # Integrate everything into the new obfuscated code
    new_code = f"""
{imports_code}

{opaque_pred_code}


initial_circuit, qr, cr = create_initial_circuit()
counts = execute_circuit(initial_circuit)
selected_path = pather(counts)

if selected_path == '01':
    def prime_numbers(limit=25):
        print(f"Prime Numbers up to {{limit}}:")
        primes = []
        for num in range(2, limit + 1):
            is_prime = True
            for i in range(2, int(num ** 0.5) + 1):
                if num % i == 0:
                    is_prime = False
                    break
            if is_prime:
                primes.append(num)
        print(primes)
elif selected_path == '11':
    {random_function_code}
elif selected_path == '10':
    def fibonacci_sequence(n=20):
        print(f"Fibonacci Sequence up to {{n}} terms:")
        fib = [0, 1]
        while len(fib) < n:
            fib.append(fib[-1] + fib[-2])
        print(fib)
elif selected_path == '00':
    def factorial_calculator(n=10):
        print(f"Factorials up to {{n}}:")
        factorials = {{}}
        for i in range(1, n + 1):
            factorials[i] = 1 if i == 1 else i * factorials[i - 1]
        for key, value in factorials.items():
            print(f"{{key}}! = {{value}}")

{sample_code}            
"""
    return new_code


def main():
    if len(sys.argv) != 2:
        print("Usage: python SupObf.py <sample_code_path>")
        sys.exit(1)

    sample_code_path = sys.argv[1]
    opaque_pred_code = """
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
from qiskit_aer import AerSimulator

def create_initial_circuit():
    qr = QuantumRegister(5, 'q')
    cr = ClassicalRegister(5, 'c')
    circuit = QuantumCircuit(qr, cr)

    # Apply Hadamard gates to all qubits to create superposition
    circuit.h(qr)
    circuit.z(qr[4])
    circuit.cx(qr[0], qr[1])
    circuit.x(qr[1])
    circuit.cx(qr[1], qr[2])
    circuit.cx(qr[2], qr[4])
    circuit.cx(qr[2], qr[3])
    circuit.h(qr[0])
    circuit.cx(qr[3], qr[4])
    circuit.h(qr[2])
    circuit.h(qr[1])
    circuit.x(qr[1])
    circuit.y(qr[2])
    circuit.h(qr[1])
    circuit.s(qr[2])
    circuit.z(qr[1])
    circuit.y(qr[2])
    circuit.h(qr[1])
    circuit.x(qr[1])
    circuit.h(qr[3])
    circuit.measure(qr[:4], cr[:4])
    return circuit, qr, cr

def execute_circuit(circuit):
    backend = AerSimulator()
    # Transpile the circuit for the backend
    transpiled_circuit = transpile(circuit, backend)
    result = backend.run(transpiled_circuit, shots=1024).result()
    counts = result.get_counts()
    return counts

def pather(counts):
    selection = max(counts.items(), key=lambda item: item[1])[0][::-1]
    return selection[2:4]
"""

    new_code = modularize_opaque_pred(sample_code_path, opaque_pred_code)

    output_file = 'ObfuscatedSuperPosBranch.py'
    with open(output_file, 'w') as file:
        file.write(new_code)

    print(f"Modularized code written to {output_file}")


if __name__ == "__main__":
    main()
