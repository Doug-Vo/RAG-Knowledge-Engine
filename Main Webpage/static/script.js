// Get the form and the button by their IDs
const form = document.getElementById('translation-form');
const button = document.getElementById('translate-button');

// Listen for the form's 'submit' event
form.addEventListener('submit', function() {
    // Change the button text
    button.innerHTML = 'Translating...';
    
    // Disable the button and add the disabled style
    button.disabled = true;
    button.classList.add('btn-disabled');
});