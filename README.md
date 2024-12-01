# ObfusQate
This Quantum-Obfuscation framework provides methodologies for obfuscating quantum circuits and classical control flow, enhancing security through advanced obfuscation techniques. The toolkit supports both quantum circuit obfuscation using QASM (Quantum Assembly Language) inputs and control flow obfuscation for traditional code, ensuring that both quantum and classical algorithms are harder to reverse-engineer or analyze.

## Quantum Circuit Obfuscation: 
Obfuscate quantum circuits by providing a QASM file, resulting in an obfuscated QASM output.

Control Flow Obfuscation: Obfuscate classical control flow by providing normal source code, and receive an obfuscated version of the code as output. This is ideal for protecting classical algorithms and logic.
Usage
Quantum Circuit Obfuscation
To obfuscate a quantum circuit, provide a valid QASM file as input. The script will output an obfuscated version of the same QASM circuit, making the underlying logic significantly harder to analyze.

### Example:

'python circobf.py input.qasm'

Input: A QASM file representing the quantum circuit to be obfuscated.
Output: An obfuscated version of the provided QASM file.


## Control Flow Obfuscation
To obfuscate traditional code (e.g., Python), simply run the control flow obfuscation tool with a source code file as input. The tool will output a more complex, obfuscated version of the code.

### Example:

'python controlflowobf.py sample.py'

Input: A Python source code file to obfuscate.
Output: An obfuscated version of the provided Python file.

## Modularization and Extending Obfuscation Techniques
This framework has been designed with modularity in mind, allowing users to extend and create new obfuscation techniques for both quantum circuits and classical control flow. By following the methodology outlined in the existing files, you can implement your own customized obfuscation techniques. Below is the guide to help you get started.

### Circuit Obfuscation: Create Your Own Technique
To create a new quantum circuit obfuscation technique, examine the baseline that is the InvertedGates.py file. This file showcases the methodology for building an obfuscation routine for QASM quantum circuits by manipulating the gates and structure.

You can follow a similar process to create your own circuit obfuscation techniques.

#### Steps:
1. Review InvertedGates.py: Understand how quantum circuits are modified to obfuscate the original circuit.
2. Create a New Python File: Start by creating a new Python file that will contain your obfuscation logic, e.g., MyCircuitObfuscation.py.
3. Manipulate QASM Input: Just like InvertedGates.py, your script should take a QASM file as input, manipulate the circuit, and output an obfuscated QASM file.
4. Keep Qiskit's Limitation in Mind: Qiskit supports up to 29 qubits, so ensure your technique operates within this constraint.

### Control Flow Obfuscation: Create Your Own Technique
For traditional control flow obfuscation, examine the baseline that is the SuperPosShroud.py file. This file demonstrates how to obfuscate classical control flow by restructuring and hiding the logic, similar to superposition in quantum circuits but applied to classical code.

You can follow the same methodology to create a new control flow obfuscation technique.

#### Steps:
1. Review SuperPosShroud.py: Study how classical control flow is obfuscated using techniques that obscure the structure and logic.
2. Create a New Python File: Start by creating a new Python file that will contain your control flow obfuscation logic, e.g., MyControlFlowObfuscation.py.
3. Manipulate Source Code: Like SuperPosShroud.py, your script should take a source code file as input (e.g., .py), modify the control flow, and output an obfuscated version of the code.
4. Ensure Semantic Accuracy: Ensure that your obfuscation technique retains the functionality of the original code while making it harder to understand.

## Libraries

Make sure to use the specific libraries under requirements.txt
Especially for "qiskit-terra", 'qiskit-aer' and 'qiskit'
pip install -r requirements.txt
