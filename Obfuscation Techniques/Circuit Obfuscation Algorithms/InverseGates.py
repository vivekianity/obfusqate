import sys
import random
import time
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import circuit_drawer
from qiskit.qasm3 import dumps as qasm3_dumps
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

        segment_length = max(1, len(circuit.data) // 3)  # Split circuit into ~3 segments
        measurement_instructions = []

        for i, (instr, qargs, cargs) in enumerate(circuit.data):
            if instr.name == "measure":
                measurement_instructions.append((instr, qargs, cargs))
            else:
                # Apply obfuscation roughly at segment boundaries
                if i % segment_length == 0 and i != 0:
                    apply_dynamic_obfuscation(obfuscated_circuit, qr)
                obfuscated_circuit.append(instr, qargs, cargs)
                if i % segment_length == segment_length - 1:
                    apply_dynamic_obfuscation(obfuscated_circuit, qr)

        # Re-append the measurement instructions
        for instr, qargs, cargs in measurement_instructions:
            obfuscated_circuit.append(instr, qargs, cargs)

        return obfuscated_circuit
    return circuit

def execute_circuit(circuit):
    simulator = AerSimulator()
    execution_times = []
    for _ in range(10):
        start_time = time.time()

        # Transpile explicitly
        transpiled_circuit = transpile(circuit, simulator)

        # Run the transpiled circuit
        result = simulator.run(transpiled_circuit, shots=1024).result()
        counts = result.get_counts()

        end_time = time.time()
        execution_times.append(end_time - start_time)

    average_execution_time = sum(execution_times) / len(execution_times)
    return counts, average_execution_time

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
        print(f"Hidden string: {key}, Count: {value}")

def save_circuit_to_qasm3(circuit, filename):

    qasm_output = qasm3_dumps(circuit)
    with open(filename, 'w') as f:
        f.write(qasm_output)

def plot_circuits(original_circuit, obfuscated_circuit):
    original_plot = circuit_drawer(original_circuit, output='mpl', style='clifford')
    obfuscated_plot = circuit_drawer(obfuscated_circuit, output='mpl', style='clifford')

    original_plot.savefig('original_circuit.png')
    obfuscated_plot.savefig('obfuscated_circuit.png')

    original_image = plt.imread('original_circuit.png')
    obfuscated_image = plt.imread('obfuscated_circuit.png')

    plt.figure(figsize=(12, 6))

    plt.subplot(121)
    plt.title('Original Circuit')
    plt.imshow(original_image)
    plt.axis('off')

    plt.subplot(122)
    plt.title('Obfuscated Circuit')
    plt.imshow(obfuscated_image)
    plt.axis('off')

    plt.show()

def main():
    if len(sys.argv) != 2:
        print("Usage: python InverseGates.py input.qasm")
        sys.exit(1)

    input_qasm = sys.argv[1]
    output_qasm = 'InverseGatesObf.qasm'

    try:
        original_circuit = QuantumCircuit.from_qasm_file(input_qasm)
    except Exception:
        from qiskit.qasm3 import loads as qasm3_loads
        with open(input_qasm, 'r') as f:
            original_circuit = qasm3_loads(f.read())
    obfuscated_circuit = original_circuit.copy()
    obfuscated_circuit = obfuscate_circuit(obfuscated_circuit, obfuscate=True)

    print("\nOriginal Circuit:")
    print(original_circuit.draw(output='text'))

    print("\nObfuscated Circuit:")
    print(obfuscated_circuit.draw(output='text'))

    # Check and print the circuit depths
    original_depth = original_circuit.depth()
    obfuscated_depth = obfuscated_circuit.depth()
    print(f"\nOriginal circuit depth: {original_depth}")
    print(f"Obfuscated circuit depth: {obfuscated_depth}")

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

    save_circuit_to_qasm3(obfuscated_circuit, output_qasm)

    # Plot the circuits
    plot_circuits(original_circuit, obfuscated_circuit)

if __name__ == "__main__":
    main()