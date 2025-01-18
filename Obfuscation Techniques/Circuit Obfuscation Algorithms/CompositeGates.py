import sys
import random
from qiskit import QuantumCircuit
from functions import execute_circuit, plot_circuits, save_circuit_to_qasm


def auxiliary_gate():
    sub_circuit = QuantumCircuit(1, name='auxiliary')
    sub_circuit.h(0)
    sub_circuit.h(0)
    sub_circuit.z(0)
    sub_circuit.x(0)
    sub_circuit.z(0)
    sub_circuit.x(0)
    auxiliary = sub_circuit.to_gate()
    auxiliary.name = 'auxiliary'
    return auxiliary


def restore_gate():
    sub_circuit = QuantumCircuit(1, name='restore')
    sub_circuit.x(0)
    sub_circuit.z(0)
    sub_circuit.x(0)
    sub_circuit.z(0)
    sub_circuit.h(0)
    sub_circuit.h(0)
    restore = sub_circuit.to_gate()
    restore.name = 'restore'
    return restore


def encapsulate_original_gate(gate, num_qubits):
    sub_circuit = QuantumCircuit(num_qubits, name='encapsulated')
    sub_circuit.append(gate, list(range(num_qubits)))
    encapsulated = sub_circuit.to_gate()
    encapsulated.name = 'FourierTransform'
    return encapsulated


def apply_auxiliary_gates(circuit, qr):
    for qubit in qr:
        circuit.append(auxiliary_gate(), [qubit])


def apply_restore_gates(circuit, qr):
    for qubit in qr:
        circuit.append(restore_gate(), [qubit])


def obfuscate_circuit(circuit, obfuscate=False):
    if obfuscate:
        qr = circuit.qubits
        apply_auxiliary_gates(circuit, qr)
        apply_restore_gates(circuit, qr)
    return circuit


def insert_obfuscation(circuit, encapsulate_probability=0.5):
    """ Insert obfuscation gates and partially encapsulate original gates within composite gates """
    new_circuit = QuantumCircuit(*circuit.qregs, *circuit.cregs)
    obfuscation_done = False
    measurement_instructions = []

    for instr, qargs, cargs in circuit.data:
        if instr.name == 'measure':
            measurement_instructions.append((instr, qargs, cargs))
        else:
            if not obfuscation_done:
                obfuscate_circuit(new_circuit, obfuscate=True)  # Apply obfuscation before original gates
                obfuscation_done = True

            if random.random() < encapsulate_probability:
                encapsulated_gate = encapsulate_original_gate(instr, len(qargs))
                new_circuit.append(encapsulated_gate, qargs, cargs)
            else:
                new_circuit.append(instr, qargs, cargs)

    if obfuscation_done:
        obfuscate_circuit(new_circuit, obfuscate=True)  # Apply obfuscation after original gates but before measurements

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


def main():
    if len(sys.argv) != 2:
        print("Usage: python CompositeGates.py input.qasm")
        sys.exit(1)

    input_qasm = sys.argv[1]
    output_qasm = 'CloakedGatesObf.qasm'

    original_circuit = QuantumCircuit.from_qasm_file(input_qasm)
    obfuscated_circuit = insert_obfuscation(original_circuit)

    print("\nOriginal Circuit:")
    print(original_circuit.draw(output='text'))

    print("\nObfuscated Circuit:")
    print(obfuscated_circuit.draw(output='text'))

    original_results, original_time = execute_circuit(original_circuit)
    obfuscated_results, obfuscated_time = execute_circuit(obfuscated_circuit)

    print("Original Results:")
    for key, value in original_results.items():
        print(f"{key}: {value}")

    print("Obfuscated Results for Composite Gates Obfuscation:")
    for key, value in obfuscated_results.items():
        print(f"{key}: {value}")

    semantic_accuracy = compare_results(original_results, obfuscated_results)
    print(f"Semantic accuracy: {semantic_accuracy:.2f}%")

    print(f"Original Circuit Execution Time: {original_time:.4f} seconds")
    print(f"Obfuscated Circuit Execution Time: {obfuscated_time:.4f} seconds")

    save_circuit_to_qasm(obfuscated_circuit, 'CompositeGates.qasm')

    # Plot the circuits
    plot_circuits(original_circuit, obfuscated_circuit)

if __name__ == "__main__":
    main()
