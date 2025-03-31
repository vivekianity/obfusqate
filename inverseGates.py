import sys
import random
import time
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

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
        segment_length = max(1, len(circuit.data) // 3)  # Divide into ~3 segments
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

def execute_circuit(circuit):
    simulator = AerSimulator()
    execution_times = []
    for _ in range(10):
        start_time = time.time()
        transpiled_circuit = transpile(circuit, simulator)
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
        hidden_string = key[::-1]  # Reverse to match qubit order (LSB to MSB)
        print(f"Hidden string: {hidden_string}, Count: {value}")

def ig_obfuscate_and_execute(input_qasm):

    try:
        original_circuit = QuantumCircuit.from_qasm_str(input_qasm)
    except Exception:
        # Fallback: if not QASM2, try QASM3.
        from qiskit.qasm3 import loads as qasm3_loads
        original_circuit = qasm3_loads(input_qasm)
    
    obfuscated_circuit = original_circuit.copy()
    obfuscated_circuit = obfuscate_circuit(obfuscated_circuit, obfuscate=True)

    original_results, original_time = execute_circuit(original_circuit)
    obfuscated_results, obfuscated_time = execute_circuit(obfuscated_circuit)
    semantic_accuracy = compare_results(original_results, obfuscated_results)

    return {
        "original_circuit": original_circuit,
        "obfuscated_circuit": obfuscated_circuit,
        "original_results": original_results,
        "obfuscated_results": obfuscated_results,
        "semantic_accuracy": semantic_accuracy,
        "original_time": original_time,
        "obfuscated_time": obfuscated_time,
    }