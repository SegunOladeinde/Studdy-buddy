// DOM Elements
const chatWindow = document.getElementById('chatWindow');
const noteInput = document.getElementById('noteInput');
const inputForm = document.getElementById('inputForm');
const modeButtons = document.querySelectorAll('.mode-btn');
const chatHistoryList = document.getElementById('chatHistoryList');
const newChatBtn = document.getElementById('newChatBtn');

let activeMode = 'Simplifier';
let currentChatId = null;

// ✅ Load chat history from backend on page load
window.addEventListener('DOMContentLoaded', async () => {
  try {
    const response = await fetch('http://ec2-13-61-185-23.eu-north-1.compute.amazonaws.com:8000/history');
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log("✅ Fetched history:", data);

    chatHistoryList.innerHTML = ''; // Clear any existing items

    data.history.forEach(chat => {
      const item = document.createElement('li');

      // Create a clean preview title
      let title = chat.text.trim();
      if (title.length > 30) {
        title = title.substring(0, 30).trim() + '...';
      }
      item.textContent = `[${chat.mode}] ${title}`;
      item.title = chat.text; // Show full message on hover

      // Click to load this chat
      item.addEventListener('click', async () => {
        try {
          // Show loading state
          chatWindow.innerHTML = '<div class="message bot">🔄 Loading conversation...</div>';

          const res = await fetch(`http://ec2-13-61-185-23.eu-north-1.compute.amazonaws.com:8000/history/${chat.chat_id}`);
          
          if (!res.ok) {
            throw new Error(`Failed to load chat: ${res.status}`);
          }

          const { messages } = await res.json();

          // Clear and rebuild chat
          chatWindow.innerHTML = '';
          messages.forEach(msg => {
            addMessageToChat(msg.text, msg.sender);
          });

          // Update current context
          currentChatId = chat.chat_id;
          console.log("🔁 Loaded chat into context:", currentChatId);

        } catch (err) {
          console.error("❌ Failed to load chat:", err);
          chatWindow.innerHTML = '<div class="message bot">❌ Could not load this conversation.</div>';
        }
      });

      chatHistoryList.appendChild(item);
    });

  } catch (err) {
    console.error("⚠️ Error loading chat history:", err);
    chatHistoryList.innerHTML = '<li style="color:red;">⚠️ Unable to load history</li>';
  }
});

// ✅ Change active mode
modeButtons.forEach(button => {
  button.addEventListener('click', () => {
    modeButtons.forEach(btn => btn.classList.remove('active'));
    button.classList.add('active');
    activeMode = button.getAttribute('data-mode');
    console.log("🎯 Active mode set to:", activeMode);
  });
});

// ✅ Send message
inputForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const userText = noteInput.value.trim();
  if (!userText) return;

  addMessageToChat(userText, 'user');

  try {
    const response = await fetch('http://ec2-13-61-185-23.eu-north-1.compute.amazonaws.com:8000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        mode: activeMode,
        text: userText,
        chat_id: currentChatId
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    console.log("🧠 AI Response:", data.reply);

    const reply = data.reply?.trim() ? data.reply : "⚠️ No response from AI.";
    addMessageToChat(reply, 'bot');

    // Save chat ID if this is a new chat
    if (!currentChatId && data.chat_id) {
      currentChatId = data.chat_id;
      console.log("🔑 Assigned new chat_id:", currentChatId);
    }

  } catch (error) {
    console.error("🚫 Error sending message:", error);
    addMessageToChat("⚠️ Failed to get response. Please try again.", "bot");
  }

  noteInput.value = '';
  noteInput.focus();
});

// ✅ Add message to chat window
function addMessageToChat(text, sender) {
  const msgDiv = document.createElement('div');
  msgDiv.className = `message ${sender}`;

  // Sanitize and preserve line breaks
  const safeText = text ? text.replace(/\n/g, '<br>') : "⚠️ No content";
  msgDiv.innerHTML = safeText;

  chatWindow.appendChild(msgDiv);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

// ✅ Start new chat
newChatBtn.addEventListener('click', () => {
  if (confirm("Start a new chat?")) {
    chatWindow.innerHTML = '<div class="message bot">Welcome to Study Buddy, I\'m here to help simplify your learning!</div>';
    noteInput.value = '';
    currentChatId = null; // Reset chat context
    console.log("🆕 New chat started.");
    noteInput.focus();
  }
});