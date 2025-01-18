from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.qasm2 import dumps
import time
import matplotlib.pyplot as plt
from qiskit.visualization import circuit_drawer

def save_circuit_to_qasm(circuit: QuantumCircuit, filename: str) -> None:
    with open(filename, 'w') as f:
        f.write(dumps(circuit))
        
def plot_circuits(original_circuit: QuantumCircuit, obfuscated_circuit: QuantumCircuit, original_filename: str = 'original_circuit.png', obfuscated_filename: str ='obfuscated_circuit.png') -> None:
    original_plot = circuit_drawer(original_circuit, output='mpl', style='clifford', filename=original_filename)
    obfuscated_plot = circuit_drawer(obfuscated_circuit, output='mpl', style='clifford', filename=obfuscated_filename)
    plt.close(original_plot)
    plt.close(obfuscated_plot)
    
    plt.figure()
    plt.title('Original Circuit')
    plt.imshow(original_plot.canvas.buffer_rgba())
    plt.axis('off')
    
    plt.figure()
    plt.title('Obfuscated Circuit')
    plt.imshow(obfuscated_plot.canvas.buffer_rgba())
    plt.axis('off')
    
    plt.show()

def execute_circuit(circuit: QuantumCircuit):
    simulator = AerSimulator()
    execution_times = []
    for _ in range(10):
        start_time = time.time()
        transpiled_circuit = transpile(circuit, simulator)
        result = simulator.run(transpiled_circuit, shots=1024).result()
        end_time = time.time()
        execution_times.append(end_time - start_time)
    average_execution_time = sum(execution_times) / len(execution_times)
    return result.get_counts(), average_execution_time

