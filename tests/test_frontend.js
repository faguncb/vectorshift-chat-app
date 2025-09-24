// Simple test harness (vanilla JS asserts)
function assert(condition, message) {
    if (!condition) {
        console.error(`Fail: ${message}`);
        return false;
    }
    console.log(`Pass: ${message}`);
    return true;
}

function runTests() {
    let passed = 0;

    // Test 1: addMessage function
    const mockDiv = document.createElement('div');
    document.body.appendChild(mockDiv);
    addMessage('Test user msg', 'user');
    const userMsg = document.querySelector('.user');
    passed += assert(!!userMsg && userMsg.textContent === 'Test user msg', 'addMessage adds user message');

    addMessage('Test bot msg', 'bot');
    const botMsg = document.querySelector('.bot');
    passed += assert(!!botMsg && botMsg.textContent === 'Test bot msg', 'addMessage adds bot message');

    // Test 2: sendMessage (mock fetch)
    const originalFetch = window.fetch;
    let fetchCalled = false;
    window.fetch = () => {
        fetchCalled = true;
        return Promise.resolve({ json: () => Promise.resolve({ reply: 'Mock reply' }) });
    };

    const event = new MouseEvent('click');
    document.getElementById('send-btn').dispatchEvent(event);  // Assumes DOM loaded, but for test, simulate
    // Note: Full integration needs manual trigger; this checks call flag post-send
    setTimeout(() => {
        passed += assert(fetchCalled, 'sendMessage calls fetch');
    }, 100);

    console.log(`Tests completed: ${passed}/3 passed`);  // Adjust count as needed
    if (passed === 3) console.log('All frontend tests passed!');
}

document.addEventListener('DOMContentLoaded', runTests);