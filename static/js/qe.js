document.addEventListener('DOMContentLoaded', function () {
    var infoModal = document.getElementById('infoModal');
    var infoTitle = document.getElementById('infoTitle');
    var infoText = document.getElementById('infoText');
    var infoMP4 = document.getElementById('infoMP4');

    var infoData = {
        'keyGeneration': {
            'title': 'Key Generation',
            'text': 'The following automatically downloads a zip file containing two different files: Public and Private key file. \n\nKeep your private key secure and confidential. \n\nDO NOT SHARE your public key with others so they can encrypt files for you.',
            'mp4': '/static/mp4/keyGeneration.mp4'
        },
        'encryption': {
            'title': 'Encryption',
            'text': 'Requirements:\n1. The recipient\'s public key file.\n2. The file you want to encrypt and send to the recipient.\n\nThe tool will:\n- Encapsulate a shared secret using the recipient\'s public key via Kyber KEM.\n- Derive an AES-256 key from the shared secret.\n- Encrypt your file using AES-256 GCM with the derived key.\n\nOutputs contained in the downloaded zip file:\n- Encrypted file\n- Encapsulated key file\n\nSend both files securely to the recipient.',
            'mp4': '/static/mp4/encryption.mp4'
        },
        'decryption': {
            'title': 'Decryption',
            'text': 'Requirements:\n1. Your private key file.\n2. The encrypted file received.\n3. The encapsulated key file received.\n\nThe tool will:\n- Decapsulate the shared secret using your private key via Kyber KEM.\n- Derive the AES-256 key from the shared secret.\n- Decrypt the file using AES-256 GCM with the derived key.',
            'mp4': '/static/mp4/decryption.mp4'
        }


    };

    window.showInfo = function (method) {
        var data = infoData[method];
        infoTitle.innerText = data.title;
        infoText.innerText = data.text;

        if (data.mp4) {
            infoMP4.querySelector('source').src = data.mp4;
            infoMP4.load(); // Reload the video source
            infoMP4.style.display = 'block';
        } else {
            infoMP4.style.display = 'none';
        }
        infoModal.style.display = 'block';
    };

    window.closeModal = function () {
        infoModal.style.display = 'none';
        infoMP4.pause(); // Pause the video when the modal is closed
    };

    window.onclick = function (event) {
        if (event.target == infoModal) {
            infoModal.style.display = 'none';
            infoMP4.pause(); // Pause the video when clicking outside the modal
        }
    };
});
