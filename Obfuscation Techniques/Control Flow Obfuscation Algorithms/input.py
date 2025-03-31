from qiskit_aer.primitives import Sampler
from qiskit_machine_learning.algorithms import VQC
from qiskit_machine_learning.optimizers import COBYLA
from qiskit.circuit.library import ZZFeatureMap, RealAmplitudes
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import classification_report
import numpy as np

def prepare_data(test_size=0.2, random_state=42):
    X = np.random.rand(100, 4)
    y = np.random.choice([0, 1], size=100, p=[0.7, 0.3])
    scaler = MinMaxScaler((0, np.pi))
    X = scaler.fit_transform(X)
    return train_test_split(X, y, test_size=test_size, random_state=random_state)

def train_and_evaluate(X_train, X_test, y_train, y_test):
    feature_map = ZZFeatureMap(feature_dimension=4, reps=2)
    ansatz = RealAmplitudes(num_qubits=4, reps=2)
    optimizer = COBYLA(maxiter=100)

    vqc = VQC(
        feature_map=feature_map,
        ansatz=ansatz,
        optimizer=optimizer,
        sampler=Sampler(shots=1024),
        output_shape=2
    )

    vqc.fit(X_train, y_train)
    y_pred = vqc.predict(X_test)

    print("Quantum‑enhanced IDS (VQC):\n")
    print(classification_report(y_test, y_pred, target_names=["Benign", "Malicious"]))

def main():
    X_train, X_test, y_train, y_test = prepare_data()
    train_and_evaluate(X_train, X_test, y_train, y_test)

if __name__ == "__main__":
    main()
