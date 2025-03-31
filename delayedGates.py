import sys
import time
import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

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

def insert_obfuscation(circuit):
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

def execute_circuit(circuit):
    simulator = AerSimulator()
    execution_times = []
    counts = None
    for _ in range(10):
        start_time = time.time()

        # Transpile the circuit for the simulator
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

def interpret_results(results):
    for key, value in results.items():
        hidden_string = key
        print(f"Result: {hidden_string}, Count: {value}")

def dg_obfuscate_and_execute(input_qasm):
    
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
 

