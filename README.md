# ObfusQate Docker
This Quantum-Obfuscation framework provides methodologies for obfuscating quantum circuits and classical control flow, enhancing security through advanced obfuscation techniques. The toolkit supports both quantum circuit obfuscation using QASM (Quantum Assembly Language) inputs and control flow obfuscation for traditional code, ensuring that both quantum and classical algorithms are harder to reverse-engineer or analyze.

# Documentation

Quick setup with docker

```
docker pull obfusqate/obfusqate:latest
docker run -p 5000:5000 obfusqate/obfusqate:latest
```

For advanced users (OPTIONAL):

For users that wants to run the obfuscation process quicker, they can consider to increase the GUNICORN_WORKERS=INPUT_YOUR_NUMBER. The INPUT_YOUR_NUMBER can be changed to the number of corresponding cores in your local system. Recommended calculation would be having the number of cores: (2 x $num_cores) + 1 as the maximum number.

```
docker run -p 5000:5000 -e GUNICORN_WORKERS=INPUT_YOUR_NUMBER obfusqate/obfusqate:latest
```