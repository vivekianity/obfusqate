import ast
import sys
import random

# This Obfuscation is meant to work on code that contains at least 2 function declarations that contain no operations
def ssop_obfuscate_and_execute(code_content):
    # Read the input fil

    # Parse the code into an AST
    parsed_code = ast.parse(code_content)

    # Extract import statements and functions
    imports = []
    other_nodes = []
    function_defs = []

    for node in parsed_code.body:
        if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            imports.append(node)
        elif isinstance(node, ast.FunctionDef):
            function_defs.append(node)
        else:
            other_nodes.append(node)

    # Select two random functions from the parsed code
    if len(function_defs) < 2:
        raise ValueError("The input code must contain at least two functions.")

    selected_functions = random.sample(function_defs, 2)

    # Remove the selected functions from other_nodes
    other_functions = [node for node in function_defs if node not in selected_functions]

    # Convert AST nodes back to code
    def ast_to_code(nodes):
        return "\n".join([ast.unparse(node) for node in nodes])

    # Create the code for the selected functions
    function_1_code = ast_to_code([selected_functions[0]])
    function_2_code = ast_to_code([selected_functions[1]])
    other_functions_code = ast_to_code(other_functions)
    other_code = ast_to_code(other_nodes)
    imports_code = ast_to_code(imports)

    # Ensure the function codes are properly formatted
    function_1_code = "\n    ".join(function_1_code.split("\n"))
    function_2_code = "\n    ".join(function_2_code.split("\n"))
    other_functions_code = "\n".join(other_functions_code.split("\n"))
    other_code = "\n".join(other_code.split("\n"))

    # Create the obfuscated code
    obfuscated_code = f"""
{imports_code}
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

# Create a quantum circuit with one qubit
qc = QuantumCircuit(1)
qc.h(0)  # Put the qubit in superposition using a Hadamard gate
qc.save_statevector()

# Use Aer's statevector_simulator
simulator = AerSimulator(method="statevector")

# Transpile the circuit for the simulator
transpiled_qc = transpile(qc, simulator)

# Execute the transpiled circuit on the statevector simulator
result = simulator.run(transpiled_qc).result()

# Grab results from the job
statevector = result.get_statevector()

# Decision based on quantum statevector measurement
if abs(statevector[0]) > 0:
    # This branch shall always execute
    {function_1_code}
if abs(statevector[1]) > 0:
    # This branch shall never execute
    # The statevector for [1] is always 0
    {function_2_code}

{other_functions_code}
{other_code}
"""

    return {
        'original_code': code_content,
        'obfuscated_code': obfuscated_code,
    }



