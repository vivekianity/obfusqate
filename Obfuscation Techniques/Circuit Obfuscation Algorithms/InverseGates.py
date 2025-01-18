import sys
import random
from qiskit import QuantumCircuit
from functions import execute_circuit, plot_circuits, save_circuit_to_qasm

def apply_dynamic_obfuscation(circuit, qr):
    gates = [
        ('h', 'h'), ('x', 'x'), ('z', 'z'), ('s', 'sdg'),
        ('t', 'tdg'), ('cx', 'cx'), ('cz', 'cz'), ('cy', 'cy'), ('ccx', 'ccx')
    ]

    for q in qr:
        for gate_pair in random.sample(gates, k=len(gates)):
            apply_gate_pair(circuit, q, gate_pair)

def apply_gate_pair(circuit, q, gate_pair):
    gate1, gate2 = gate_pair
    num_qubits = len(circuit.qubits)
    if gate1 in ['cx', 'cz', 'cy', 'ccx']:
        if gate1 == 'ccx' and num_qubits >= 3:
            target_qubits = random.sample(circuit.qubits, k=3)
            circuit.ccx(target_qubits[0], target_qubits[1], target_qubits[2])
            circuit.ccx(target_qubits[0], target_qubits[1], target_qubits[2])
        elif num_qubits >= 2:
            target_qubits = random.sample(circuit.qubits, k=2)
            if gate1 == 'cx':
                circuit.cx(target_qubits[0], target_qubits[1])
                circuit.cx(target_qubits[0], target_qubits[1])
            elif gate1 == 'cz':
                circuit.cz(target_qubits[0], target_qubits[1])
                circuit.cz(target_qubits[0], target_qubits[1])
            elif gate1 == 'cy':
                circuit.cy(target_qubits[0], target_qubits[1])
                circuit.cy(target_qubits[0], target_qubits[1])
    else:
        getattr(circuit, gate1)(q)
        getattr(circuit, gate2)(q)

def obfuscate_circuit(circuit, obfuscate=False):
    if obfuscate:
        qr = circuit.qubits
        cr = circuit.clbits
        obfuscated_circuit = QuantumCircuit(len(qr), len(cr))

        segment_length = max(1, len(circuit.data) // 3)  # Split the circuit into approximately 3 segments
        measurement_instructions = []

        for i, (instr, qargs, cargs) in enumerate(circuit.data):
            if instr.name == "measure":
                measurement_instructions.append((instr, qargs, cargs))
            else:
                if i % segment_length == 0 and i != 0:
                    apply_dynamic_obfuscation(obfuscated_circuit, qr)
                obfuscated_circuit.append(instr, qargs, cargs)
                if i % segment_length == segment_length - 1:
                    apply_dynamic_obfuscation(obfuscated_circuit, qr)

        for instr, qargs, cargs in measurement_instructions:
            obfuscated_circuit.append(instr, qargs, cargs)

        return obfuscated_circuit
    return circuit


def compare_results(original, obfuscated):
    keys = set(original.keys()).union(obfuscated.keys())
    total = sum(original.values())
    correct = 0
    for key in keys:
        original_count = original.get(key, 0)
        obfuscated_count = obfuscated.get(key, 0)
        correct += min(original_count, obfuscated_count)
    return 100 * correct / total if total > 0 else 0

def interpret_results(results):
    for key, value in results.items():
        hidden_string = key
        print(f"Hidden string: {hidden_string}, Count: {value}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python InverseGates.py input.qasm")
        sys.exit(1)

    input_qasm = sys.argv[1]
    output_qasm = 'InverseGatesObf.qasm'

    original_circuit = QuantumCircuit.from_qasm_file(input_qasm)
    obfuscated_circuit = original_circuit.copy()
    obfuscated_circuit = obfuscate_circuit(obfuscated_circuit, obfuscate=True)

    print("\nOriginal Circuit:")
    print(original_circuit.draw(output='text'))

    print("\nObfuscated Circuit:")
    print(obfuscated_circuit.draw(output='text'))

    original_results, original_time = execute_circuit(original_circuit)
    obfuscated_results, obfuscated_time = execute_circuit(obfuscated_circuit)

    print("Original Results:")
    interpret_results(original_results)
    print("Obfuscated Results for Inverse Gates Obfuscation:")
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
