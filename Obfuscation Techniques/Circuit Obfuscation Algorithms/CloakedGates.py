import sys
import random
from qiskit import QuantumCircuit
from functions import plot_circuits, execute_circuit, save_circuit_to_qasm


substitution_map = {
    'x': [
        ['h', 'z', 'h'],
        ['s', 'y', 's'],
        ['h', 'y', 'h'],
        ['z', 'h', 'z', 'h', 'z'],
        ['sdg', 'y', 's'],
    ],
    'z': [
        ['h', 'x', 'h'],
        ['s', 's'],
        ['t', 't', 't', 't'],
        ['x', 'h', 'x', 'h', 'x'],
    ],
    's': [
        ['t', 't'],
        ['x', 't', 'x', 't'],
        ['z', 't', 'z', 't'],
    ],
    'y': [
        ['x', 'z'],
        ['z', 'x'],
        ['s', 'x', 'sdg'],
        ['t', 'x', 'tdg'],
    ]
}


# Function to dynamically substitute gates with random strategies, skipping rotation gates
def substitute_gate(circuit, instr, qargs):
    gate_name = instr.name

    # Ignore rotation gates and keep them unchanged
    if gate_name in ['rz', 'rx', 'ry']:
        circuit.append(instr, qargs, [])  # Leave the rotation gates as-is
        return

    # Check if the gate has a substitution rule for non-rotation gates
    if gate_name in substitution_map:
        # Randomly select a substitution strategy for the gate
        substitute_sequence = random.choice(substitution_map[gate_name])
        # Apply the substitution sequence
        for gate in substitute_sequence:
            if gate == 'cx':  # Multi-qubit gates like CNOT
                circuit.cx(qargs[0], qargs[1])
            else:
                # Single qubit gates without parameters
                getattr(circuit, gate)(qargs[0])
    else:
        # Keep the gate unchanged if no substitution rule is found
        circuit.append(instr, qargs, [])

# Function to dynamically apply obfuscation
def apply_dynamic_obfuscation(circuit, qr):
    new_circuit = QuantumCircuit(*circuit.qregs, *circuit.cregs)

    for instr, qargs, cargs in circuit.data:
        # Dynamically substitute each gate, skipping rotation gates
        substitute_gate(new_circuit, instr, qargs)

    return new_circuit

# Wrapper to call the obfuscation on the entire circuit
def obfuscate_circuit(circuit, qr, obfuscate=False):
    if obfuscate:
        return apply_dynamic_obfuscation(circuit, qr)
    return circuit

# Function to insert obfuscation at both the beginning and end of the circuit
def insert_dynamic_obfuscation(circuit):
    new_circuit = QuantumCircuit(*circuit.qregs, *circuit.cregs)
    qr = circuit.qubits
    measurement_instructions = []

    # Apply obfuscation before the original gates
    new_circuit = apply_dynamic_obfuscation(new_circuit, qr)

    for instr, qargs, cargs in circuit.data:
        if instr.name == 'measure':
            measurement_instructions.append((instr, qargs, cargs))
        else:
            new_circuit.append(instr, qargs, cargs)

    # Apply obfuscation after the original gates
    new_circuit = apply_dynamic_obfuscation(new_circuit, qr)

    for instr, qargs, cargs in measurement_instructions:
        new_circuit.append(instr, qargs, cargs)

    return new_circuit

# Function to compare results of original and obfuscated circuits
def compare_results(original, obfuscated):
    keys = set(original.keys()).union(obfuscated.keys())
    total = sum(original.values())
    correct = 0
    for key in keys:
        original_count = original.get(key, 0)
        obfuscated_count = obfuscated.get(key, 0)
        correct += min(original_count, obfuscated_count)
    return 100 * correct / total if total > 0 else 0


# Function to interpret and print the results
def interpret_results(results):
    for key, value in results.items():
        hidden_string = key
        print(f"Result: {hidden_string}, Count: {value}")


# Main function to run the script
def main():
    if len(sys.argv) != 2:
        print("Usage: python DynamicObfuscation.py input.qasm")
        sys.exit(1)

    input_qasm = sys.argv[1]
    output_qasm = 'CloakedGatesObf.qasm'

    original_circuit = QuantumCircuit.from_qasm_file(input_qasm)
    obfuscated_circuit = insert_dynamic_obfuscation(original_circuit)

    print("\nOriginal Circuit:")
    print(original_circuit.draw(output='text'))

    print("\nObfuscated Circuit:")
    print(obfuscated_circuit.draw(output='text'))

    original_results, original_time = execute_circuit(original_circuit)
    obfuscated_results, obfuscated_time = execute_circuit(obfuscated_circuit)

    print("Original Results:")
    interpret_results(original_results)
    print("Obfuscated Results for Cloaked Gates Obfuscation:")
    interpret_results(obfuscated_results)

    semantic_accuracy = compare_results(original_results, obfuscated_results)
    print(f"Semantic accuracy: {semantic_accuracy:.2f}%")

    print(f"Original Circuit Execution Time: {original_time:.4f} seconds")
    print(f"Obfuscated Circuit Execution Time: {obfuscated_time:.4f} seconds")

    save_circuit_to_qasm(obfuscated_circuit, output_qasm)

    # Plot the circuits
    plot_circuits(original_circuit, obfuscated_circuit)

if __name__ == "__main__":
    main()
