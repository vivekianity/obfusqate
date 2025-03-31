document.addEventListener('DOMContentLoaded', function () {
    var infoModal = document.getElementById('infoModal');
    var infoTitle = document.getElementById('infoTitle');
    var infoText = document.getElementById('infoText');
    var infoGif = document.getElementById('infoGif');

    var infoData = {
        'inverseGates': {
            'title': 'Inverse Gates',
            'text': 'Inverse Gates obfuscation involves using gates that perform inverse operations to obfuscate the circuit.',
            'gif': '/static/gifs/inverse.gif'
        },
        'compositeGates': {
            'title': 'Composite Gates',
            'text': 'Composite Gates obfuscation involves combining multiple gates into a single composite gate to obscure the circuit structure.',
            'gif': '/static/gifs/composite.gif'
        },
        'delayedGates': {
            'title': 'Delayed Gates',
            'text': 'Delayed Gates obfuscation involves delaying the execution of certain gates to make the circuit harder to analyze.',
            'gif': '/static/gifs/delayed.gif'
        },
        'cloakedGates': {
            'title': 'Cloaked Gates',
            'text': 'Obfuscate circuits by replacing specific gates with curated equivalent sequences to disguise the circuit structure.',
            'gif': '/static/gifs/cloakedGates.gif'
        },
        'entangledOP': {
            // 'title': 'Variable Qubit Pairs Obfuscation'
            'title': 'Variable Qubit Pairs Obfuscation',
            'text': 'Variable Qubit Pairs Obfuscation creates multiple Bell States ensuring 1 real outcome, enabling deterministic opaque predicates.',
            'gif': '/static/gifs/variableQubit.gif'
        },
        'superpositionOP': {
            // 'title': 'Superposition Opaque Predicate',
            'title': 'Superposition Opaque Predicate',
            'text': "Employs a 5-qubit circuit ensuring qubits 2 and 3 are '1', guaranteeing a particular branch is consistently true to mislead analyzers.",
            'gif': '/static/gifs/branchObfuscation.gif'
        },
        'superpositionShroudOP': {
            'title': 'Superposition Shroud',
            'text': 'Superposition Shroud obfuscation utilizes a qubit in superposition to craft a reverse opaque predicate where all branches are true.',
            'gif': '/static/gifs/superpostionShroud.gif'
        },
        'simpleEntanglementOP': {
            // 'title': 'Simple Entanglement Opaque Predicate',
            'title': 'Simple Entanglement Obfuscation',
            'text': "Simple Entanglement Obfuscation creates 4 opaque predicates in program with 2 valid branches ('00' or '11') and 2 false branches ('01' and '10')",
            'gif': '/static/gifs/simpleEntanglement.gif'
        }
    };

    window.showInfo = function(method) {
        var data = infoData[method];
        infoTitle.innerText = data.title;
        infoText.innerText = data.text;
        if (data.gif) {
            infoGif.src = data.gif;
            infoGif.style.display = 'block';
        } else {
            infoGif.style.display = 'none';
        }
        infoModal.style.display = 'block';
    };

    window.closeModal = function() {
        infoModal.style.display = 'none';
    };

    window.onclick = function(event) {
        if (event.target == infoModal) {
            infoModal.style.display = 'none';
        }
    };
});

// static/js/obfuscate.js

function openDialog() {
    document.getElementById('fileid').click();
}

function displayFileName() {
    var fileInput = document.getElementById('fileid');
    var fileNameDisplay = document.getElementById('fileNameDisplay');
    if (fileInput.files.length > 0) {
        fileNameDisplay.textContent = 'Selected file: ' + fileInput.files[0].name;
    }
}