import sys
import random
from qiskit import QuantumCircuit
from functions import execute_circuit, plot_circuits, save_circuit_to_qasm


def apply_complex_obfuscation(circuit, qr):
    identity_sequences = [
        ["y", "s", "y"],
        ["h", "s", "h", "s", "h"],
        ["x", "h", "z", "h", "x"],
        ["h", "t", "t", "h", "t", "t", "h"],
        ["z", "h", "y", "h", "z"],
        ["s", "z", "sdg"],
        ["t", "s", "tdg"],
        ["swap", "x", "swap"],
        ["y", "x", "y", "x", "y"]
    ]

    for qubit in qr:
        random_sequences = random.sample(identity_sequences, k=len(identity_sequences))
        for sequence in random_sequences:
            for gate in sequence:
                if gate == "cx" or gate == "swap":
                    for i in range(0, len(qr) - 1, 2):
                        getattr(circuit, gate)(qr[i], qr[i + 1])
                else:
                    getattr(circuit, gate)(qubit)


def obfuscate_circuit(circuit, qr, obfuscate=False):
    if obfuscate:
        apply_complex_obfuscation(circuit, qr)
    return circuit


def insert_obfuscation(circuit: QuantumCircuit) -> QuantumCircuit:
    new_circuit = QuantumCircuit(*circuit.qregs, *circuit.cregs)
    qr = circuit.qubits
    measurement_instructions = []

    # Apply obfuscation before the original gates
    obfuscate_circuit(new_circuit, qr, obfuscate=True)

    for instr, qargs, cargs in circuit.data:
        if instr.name == 'measure':
            measurement_instructions.append((instr, qargs, cargs))
        else:
            new_circuit.append(instr, qargs, cargs)

    # Apply obfuscation after the original gates
    obfuscate_circuit(new_circuit, qr, obfuscate=True)

    for instr, qargs, cargs in measurement_instructions:
        new_circuit.append(instr, qargs, cargs)

    return new_circuit


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
        print(f"Result: {hidden_string}, Count: {value}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python DelayedGates.py input.qasm")
        sys.exit(1)

    input_qasm = sys.argv[1]
    output_qasm = 'DelayedGatesObf.qasm'

    original_circuit = QuantumCircuit.from_qasm_file(input_qasm)
    obfuscated_circuit = insert_obfuscation(original_circuit)

    print("\nOriginal Circuit:")
    print(original_circuit.draw(output='text'))

    print("\nObfuscated Circuit:")
    print(obfuscated_circuit.draw(output='text'))

    original_results, original_time = execute_circuit(original_circuit)
    obfuscated_results, obfuscated_time = execute_circuit(obfuscated_circuit)

    print("Original Results:")
    interpret_results(original_results)
    print("Obfuscated Results for Delayed Gates Obfuscation:")
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
