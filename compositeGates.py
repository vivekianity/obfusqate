import sys
import time
import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

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

def execute_circuit(circuit):
    simulator = AerSimulator()
    execution_times = []
    counts = None

    for _ in range(10):
        start_time = time.time()

        # Explicit transpilation
        transpiled = transpile(circuit, simulator)

        # Run the transpiled circuit
        result = simulator.run(transpiled, shots=1024).result()
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

def cg_obfuscate_and_execute(input_qasm):

    try:
        original_circuit = QuantumCircuit.from_qasm_str(input_qasm)
    except Exception:
        # Fallback: if not QASM2, try QASM3.
        from qiskit.qasm3 import loads as qasm3_loads
        original_circuit = qasm3_loads(input_qasm)
    
    obfuscated_circuit = original_circuit.copy()
    obfuscated_circuit = insert_obfuscation(original_circuit)

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
