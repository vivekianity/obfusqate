document.addEventListener('DOMContentLoaded', function () {
    var originalBtn = document.getElementById('originalCircuitBtn');
    var obfuscatedBtn = document.getElementById('obfuscatedCircuitBtn');
    var modal = document.getElementById('resultModal');
    var span = document.getElementsByClassName('close')[0];
    var modalTitle = document.getElementById('modalTitle');
    var modalText = document.getElementById('modalText');

    originalBtn.onclick = function () {
        var originalCircuit = originalBtn.getAttribute('data-original-circuit');
        modal.style.display = 'block';
        modalTitle.innerText = 'Original Circuit Results';
        modalText.innerText = originalCircuit;
    }

    obfuscatedBtn.onclick = function () {
        var obfuscatedCircuit = obfuscatedBtn.getAttribute('data-obfuscated-circuit');
        modal.style.display = 'block';
        modalTitle.innerText = 'Obfuscated Circuit Results';
        modalText.innerText = obfuscatedCircuit;
    }

    span.onclick = function () {
        modal.style.display = 'none';
    }

    window.onclick = function (event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }
});
