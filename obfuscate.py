from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, session
import io
from inverseGates import ig_obfuscate_and_execute
from compositeGates import cg_obfuscate_and_execute
from delayedGates import dg_obfuscate_and_execute
from entangledOP import eop_obfuscate_and_execute #Variable Qubit Pairs Obfuscation
from superpositionShroudOP import ssop_obfuscate_and_execute #Superposition Shroud
from simpleEntanglementOP import seop_obfuscate_and_execute #Simple Entanglement Obfuscation
from qiskit.qasm3 import dumps

import tempfile

ALLOWED_EXTENSIONS = {
    'code': {'py'},
    'circuit': {'qasm'}
}

obfuscate_bp = Blueprint("obfuscate", __name__)

# Helper function to check allowed file types
def allowed_file(filename, context):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS[context]

# Route to display pre-obfuscation page
# This function handles all pre-obf logic
@obfuscate_bp.route("/obfuscate")
def preObfuscate():
    method_string = request.args.get("method")
    circuitObf_methodNames = {
        'inverseGates': 'Inverse Gates',
        'compositeGates': 'Composite Gates',
        'delayedGates': 'Delayed Gates',
        # 'cloakedGates': 'Cloaked Gates',

        # Add other methods here
    }
    
    codeObf_methodNames = {
        'entangledOP': 'Variable Qubit Pairs Obfuscation',
        # 'superpositionOP': 'Branch Obfuscation via Superposition',
        'superpositionShroudOP': 'Superposition Shroud',
        'simpleEntanglementOP': 'Simple Entanglement Obfuscation',
        # Add other methods here
    }
    
    if method_string in circuitObf_methodNames:
        with open('sample.qasm', 'r') as file:
            qasm_code = file.read()
        return render_template("preCircuitObfuscate.html", method=method_string, method_names=circuitObf_methodNames, qasm_code=qasm_code)

    elif(method_string in codeObf_methodNames):
        with open('sample.py', 'r') as file:
            python_code = file.read()
        return render_template("preCodeObfuscate.html", method=method_string, method_names=codeObf_methodNames, python_code=python_code)
    else:
        flash("Invalid obfuscation method selected.", "error")
        return redirect("methods")

# This route will be for post circuit obfuscation page
# The function looks for two inputs, either code or file.
@obfuscate_bp.route("/postCircuitObfuscation", methods=["GET", "POST"])
def handle_CircuitObfuscate():
    
    method = request.form.get("method")
    
    circuitObf_methodNames = {
        'inverseGates': 'Inverse Gates',
        'compositeGates': 'Composite Gates',
        'delayedGates': 'Delayed Gates',
        # 'cloakedGates': 'Cloaked Gates',
        # Add other methods here
    }

    file_input = request.files.get("file_input")
    code_input = request.form.get("code_input")
    
    if(method in circuitObf_methodNames):
        
        # Based on html class button name
        if request.form.get("obfuscate-button") == "obfuscate":
            
            # Error handling: Checks if any code is even inputted
            if not code_input:
                flash("Please paste your QASM code to obfuscate.", "error")
                
                # This redirect ensures that if any error is detected, will go back to the og preobf page
                return redirect(url_for("obfuscate.preObfuscate", method=method))
            else:
                result = process_CircuitObfuscation(method, code_input)
                
                # Error handling: Checks if backend logic has any errors caught
                # This is applied for code input
                if result is None or 'error' in result:
                    flash("Please ensure that the code submitted is valid", "error")
                    return redirect(url_for("obfuscate.preObfuscate", method=method))
                
                return render_template("postCircuitObfuscation.html", result=result, method=method, method_names=circuitObf_methodNames)
            
        # Based on html class button name
        elif request.form.get("continue-button") == "continue":
            
            if not file_input :
                flash("Please upload a file.", "error")
                return redirect(url_for("obfuscate.preObfuscate", method=method))

            if not allowed_file(file_input.filename, 'circuit'):
                flash("Please upload a valid QASM file.", "error")
                return redirect(url_for("obfuscate.preObfuscate", method=method))

            file_content = file_input.read()
            code_input = file_content.decode('utf-8')
            result = process_CircuitObfuscation(method, code_input)
            
            # Error handling: Checks if backend logic has any errors caught
            # This is applied for file input
            if result is None or 'error' in result:
                flash("Please ensure that the code submitted is valid", "error")
                return redirect(url_for("obfuscate.preObfuscate", method=method))

            return render_template("postCircuitObfuscation.html", result=result, method=method, method_names=circuitObf_methodNames)
    
    else:
        flash("Invalid obfuscation method selected.", "error")
        return redirect("methods")

# This function is to process the circuit obfuscation algos
def process_CircuitObfuscation(method, code_input):
    try:
        if method == 'inverseGates':
            result = ig_obfuscate_and_execute(code_input)
        elif method == 'compositeGates':
            result = cg_obfuscate_and_execute(code_input)
        elif method == 'delayedGates':
            result = dg_obfuscate_and_execute(code_input)
        # elif method == 'cloakedGates':
        #     result = clg_obfuscate_and_execute(code_input)
        else:
            flash("Invalid obfuscation method selected.", "error")
            return None

        # Convert the QASM code to a string
        obfuscated_qasm_code = dumps(result['obfuscated_circuit'])

        # Save the obfuscated QASM code to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.qasm')
        temp_file.write(obfuscated_qasm_code.encode('utf-8'))
        temp_file.close()

        # Store the file path in the session
        session['temp_file_path'] = temp_file.name

        return result

    except Exception as e:
        flash(f"An error occurred: {e}", "error")
        return None
    
# This route will be for post code obfuscation page
# The function looks for two inputs, either code or file.
@obfuscate_bp.route("/postCodeObfuscation", methods=["GET", "POST"])
def handle_CodeObfuscate():
    
    method = request.form.get("method")

    codeObf_methodNames = {
        'entangledOP': 'Variable Qubit Pairs Obfuscation',
        # 'superpositionOP': 'Branch Obfuscation via Superposition',
        'superpositionShroudOP': 'Superposition Shroud',
        'simpleEntanglementOP': 'Simple Entanglement Obfuscation',
        # Add other methods here
    }
    
    file_input = request.files.get("file_input")
    code_input = request.form.get("code_input")
    
    if(method in codeObf_methodNames):
        # Based on html class button name
        if request.form.get("obfuscate-button") == "obfuscate":
            if not code_input:
                flash("Please paste your Python code to obfuscate.", "error")
                return redirect(url_for("obfuscate.preObfuscate", method=method))
            else:
                result = process_CodeObfuscation(method, code_input)
                if result is None or 'error' in result:
                    flash("Please ensure that the code submitted is valid", "error")
                    return redirect(url_for("obfuscate.preObfuscate", method=method))
                
                return render_template("postCodeObfuscation.html", result=result, method=method, method_names=codeObf_methodNames)
        
        # Based on html class button name
        elif request.form.get("continue-button") == "continue":

            if not file_input:
                flash("Please upload a file.", "error")
                return redirect(url_for("obfuscate.preObfuscate", method=method))

            if not allowed_file(file_input.filename, 'code'):
                flash("Please upload a valid Python file.", "error")
                return redirect(url_for("obfuscate.preObfuscate", method=method))
            
            code_input = file_input.read().decode('utf-8')

            # Process the uploaded file
            result = process_CodeObfuscation(method, code_input)
            
            if result is None or 'error' in result:
                flash("Please ensure that the code submitted is valid", "error")
                return redirect(url_for("obfuscate.preObfuscate", method=method))
            
            return render_template("postCodeObfuscation.html", result=result, method=method, method_names=codeObf_methodNames)
    
    else:
        flash("Invalid obfuscation method selected.", "error")
        return redirect("methods")

# This function is to process the code obfuscation algos
def process_CodeObfuscation(method, code_input):
    try:
        obfuscation_methods = {
            'entangledOP': eop_obfuscate_and_execute,
            # 'superpositionOP': sop_obfuscate_and_execute,
            'superpositionShroudOP': ssop_obfuscate_and_execute,
            'simpleEntanglementOP': seop_obfuscate_and_execute
        }

        if method in obfuscation_methods:
            result = obfuscation_methods[method](code_input)
            
             # Ensure result is a dictionary
            if not isinstance(result, dict):
                flash("Invalid result format from obfuscation method.", "error")
                return None

            # Convert the obfuscated code to a string
            obfuscated_code = result['obfuscated_code']

            # Save the obfuscated code to a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.py')
            temp_file.write(obfuscated_code.encode('utf-8'))
            temp_file.close()

            # Store the file path in the session
            session['temp_file_path'] = temp_file.name

            return result
        
        flash("Invalid obfuscation method selected.")
        return None

    except Exception as e:
        flash(f"An error occurred: {e}", "error")
        return None
    
@obfuscate_bp.route("/download_qasm", methods=["POST"])
def download_qasm():
    temp_file_path = session.get('temp_file_path')
    if not temp_file_path:
        flash("No obfuscated circuit available for download.", "error")
        return redirect(url_for("obfuscate.preObfuscate"))

    try:
        return send_file(
            temp_file_path,
            as_attachment=True,
            download_name='obfuscated_circuit.qasm',
            mimetype='application/qasm'
        )
    except Exception as e:
        flash(f"An error occurred while trying to download the file: {e}", "error")
        return redirect(url_for("obfuscate.preObfuscate"))
    
# This function is to download the source code in a python file after code obfuscation
@obfuscate_bp.route("/download_obfuscated_code", methods=["POST"])
def download_obfuscated_code():
    temp_file_path = session.get('temp_file_path')
    if not temp_file_path:
        flash("No obfuscated code available for download.", "error")
        return redirect(url_for("obfuscate.preObfuscate"))

    try:
        return send_file(
            temp_file_path,
            as_attachment=True,
            download_name='obfuscated_code.py',
            mimetype='text/x-python'
        )
    except Exception as e:
        flash(f"An error occurred while trying to download the file: {e}", "error")
        return redirect(url_for("obfuscate.preObfuscate"))

    
