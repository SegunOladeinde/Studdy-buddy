// DOM Elements
const chatWindow = document.getElementById('chatWindow');
const noteInput = document.getElementById('noteInput');
const inputForm = document.getElementById('inputForm');
const modeButtons = document.querySelectorAll('.mode-btn');
const chatHistoryList = document.getElementById('chatHistoryList');
const newChatBtn = document.getElementById('newChatBtn');

let activeMode = 'Simplifier';
let currentChatId = null;

// Load chat history on page load
window.addEventListener('DOMContentLoaded', () => {
  const chats = JSON.parse(localStorage.getItem('studyBuddyChats')) || [];
  chats.forEach(chat => {
    const item = document.createElement('li');
    item.textContent = `Chat ${chat.id}`;
    item.addEventListener('click', () => {
      alert(`Opening chat ID: ${chat.id}`);
    });
    chatHistoryList.appendChild(item);
  });
});

// Set active mode when a button is clicked
modeButtons.forEach(button => {
  button.addEventListener('click', () => {
    modeButtons.forEach(btn => btn.classList.remove('active'));
    button.classList.add('active');
    activeMode = button.getAttribute('data-mode');
  });
});

// Send message to backend
inputForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const userText = noteInput.value.trim();
  if (!userText) return;

  addMessageToChat(userText, 'user');

  try {
    const response = await fetch('http://127.0.0.1:8000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode: activeMode, text: userText })
    });

    console.log("📡 Response status:", response.status); // Log HTTP status

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    console.log("🧠 AI Response:", data.reply); // See what comes back

    if (!data.reply || data.reply.trim() === "") {
      addMessageToChat("⚠️ Got empty response from AI.", "bot");
    } else {
      addMessageToChat(data.reply, "bot");
    }

  } catch (error) {
    console.error("🚫 Error sending message:", error);
    addMessageToChat("⚠️ Failed to get a response from the AI.", "bot");
  }

  noteInput.value = '';
});

// Add message to chat window
function addMessageToChat(text, sender) {
  const msgDiv = document.createElement('div');
  msgDiv.className = `message ${sender}`;

  // Handle undefined or empty text safely
  const safeText = text ? text.replace(/\n/g, '<br>') : "⚠️ No content";
  msgDiv.innerHTML = safeText;

  chatWindow.appendChild(msgDiv);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

// Clear chat
newChatBtn.addEventListener('click', () => {
  if (confirm("Start a new chat?")) {
    chatWindow.innerHTML = '<div class="message bot">Welcome to Study Buddy...</div>';
    noteInput.value = '';
    currentChatId = null;
  }
});