execute_circuit = '''
def execute_circuit(qc):
    backend = AerSimulator()
    transpiled = transpile(qc, backend)
    result = backend.run(transpiled, shots=1024).result()
    return result.get_counts(qc)

'''

measure_all = '''
def measure_all(qc, qr, cr):
    qc.measure(qr, cr)

'''

imports = '''
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
from qiskit_aer import AerSimulator

'''