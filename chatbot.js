function sendMessage() {
    var userInput = document.getElementById('userInput').value;
    var chatDiv = document.getElementById('chat');
    
    // Display user message
    chatDiv.innerHTML += '<div class="message user-message">' + userInput + '</div>';

    // Send user message to server for processing
    fetch('/get_bot_response', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'userText=' + userInput
    })
    .then(response => response.json())
    .then(data => {
        // Display bot response
        chatDiv.innerHTML += '<div class="message bot-message">' + data.response + '</div>';
    });

    // Clear input field
    document.getElementById('userInput').value = '';

    return false;
}
