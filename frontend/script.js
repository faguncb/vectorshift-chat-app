document.addEventListener('DOMContentLoaded', () => {
    const messagesDiv = document.getElementById('messages');
    const input = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');

    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });

    function sendMessage() {
        const message = input.value.trim();
        if (!message) return;

        // Add user message
        addMessage(message, 'user');
        input.value = '';

        // Fetch response from backend
        fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        })
            .then(response => response.json())
            .then(data => {
                if (data.reply) {
                    addMessage(data.reply, 'bot');
                } else if (data.error) {
                    addMessage(`Error: ${data.error}`, 'bot');
                }
            })
            .catch(error => addMessage(`Error: ${error.message}`, 'bot'));
    }

    function addMessage(text, sender) {
        const div = document.createElement('div');
        div.className = `message ${sender}`;
        div.textContent = text;
        messagesDiv.appendChild(div);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
});