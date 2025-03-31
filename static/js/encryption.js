// Function to set up event listeners for each button
function setup() {
    document.getElementById('buttonid').addEventListener('click', function() {
        document.getElementById('fileid').click();
    });
    document.getElementById('buttonid2').addEventListener('click', function() {
        document.getElementById('fileid2').click();
    });
    document.getElementById('buttonid3').addEventListener('click', function() {
        document.getElementById('fileid3').click();
    });
}

// Function to display the selected file name
function displayFileName(fileInputId, displayElementId) {
    const fileInput = document.getElementById(fileInputId);
    const fileName = fileInput.files[0]?.name || 'No file chosen';
    document.getElementById(displayElementId).textContent = fileName;
}

// Call the setup function when the window loads
window.onload = setup;
