<template>
  <Teleport to="body">
    <Transition name="drawer-slide">
      <div v-if="isOpen" class="assistant-overlay" @click.self="close">
        <div class="assistant-drawer glass-panel">
          <!-- Header -->
          <div class="assistant-header">
            <div class="header-content">
              <span class="assistant-icon">🤖</span>
              <div>
                <h3>AI Teaching Assistant</h3>
                <p class="assistant-subtitle">Ask me anything about this lecture</p>
              </div>
            </div>
            <button @click="close" class="close-btn">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Chat Messages -->
          <div class="chat-container" ref="chatContainer">
            <div
              v-for="(message, index) in messages"
              :key="index"
              class="chat-message"
              :class="message.role"
            >
              <div class="message-avatar">
                {{ message.role === 'user' ? '👤' : '🤖' }}
              </div>
              <div class="message-bubble">
                <div class="message-content" v-html="formatMessage(message.content)"></div>
                <div class="message-time">{{ message.timestamp }}</div>
              </div>
            </div>

            <!-- Typing Indicator -->
            <div v-if="isTyping" class="chat-message assistant">
              <div class="message-avatar">🤖</div>
              <div class="message-bubble">
                <div class="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>

            <!-- Welcome Message -->
            <div v-if="messages.length === 0 && !isTyping" class="welcome-message">
              <div class="welcome-icon">👋</div>
              <h4>Welcome! I'm your AI Teaching Assistant</h4>
              <p>You can ask me:</p>
              <ul>
                <li>📝 "Explain this concept in simpler terms"</li>
                <li>🔍 "What's an example of this?"</li>
                <li>🎯 "Why is this important?"</li>
                <li>🔗 "How does this relate to previous topics?"</li>
              </ul>
            </div>
          </div>

          <!-- Quick Actions -->
          <div v-if="messages.length === 0" class="quick-actions">
            <button
              v-for="(action, index) in quickActions"
              :key="index"
              @click="sendQuickAction(action.prompt)"
              class="quick-action-btn"
            >
              <span>{{ action.icon }}</span>
              <span>{{ action.label }}</span>
            </button>
          </div>

          <!-- Input Area -->
          <div class="input-area">
            <textarea
              v-model="userInput"
              @keydown.enter.prevent="sendMessage"
              placeholder="Ask a question about the lecture..."
              class="message-input"
              rows="2"
            ></textarea>
            <button
              @click="sendMessage"
              :disabled="!userInput.trim() || isTyping"
              class="send-btn"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { invoke } from '@tauri-apps/api/tauri'

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true
  },
  currentSlide: {
    type: Object,
    default: null
  },
  currentContent: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['close'])

const messages = ref([])
const userInput = ref('')
const isTyping = ref(false)
const chatContainer = ref(null)

const quickActions = [
  { icon: '💡', label: 'Explain this', prompt: 'Can you explain this concept in simpler terms?' },
  { icon: '📚', label: 'Give examples', prompt: 'Can you provide real-world examples of this?' },
  { icon: '🎯', label: 'Key takeaways', prompt: 'What are the key takeaways from this slide?' },
  { icon: '🔗', label: 'Connect concepts', prompt: 'How does this relate to what we learned before?' }
]

function formatMessage(content) {
  // Simple markdown-like formatting
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
}

function getTimestamp() {
  const now = new Date()
  return now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
}

async function sendMessage() {
  if (!userInput.value.trim() || isTyping.value) return

  const question = userInput.value.trim()
  
  // Add user message
  messages.value.push({
    role: 'user',
    content: question,
    timestamp: getTimestamp()
  })

  userInput.value = ''
  isTyping.value = true

  // Scroll to bottom
  nextTick(() => {
    scrollToBottom()
  })

  try {
    // Build context
    const context = {
      slide_title: props.currentSlide?.title || '',
      slide_content: props.currentContent || '',
      slide_number: props.currentSlide?.slide_number || 1,
      question: question
    }

    // Call backend API
    const response = await invoke('tauri_fetch', {
      url: 'http://127.0.0.1:8765/assistant',
      options: {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(context),
        responseType: 1 // JSON
      }
    })

    // Add assistant response
    messages.value.push({
      role: 'assistant',
      content: response.data.answer || 'I apologize, but I could not generate a response at this time.',
      timestamp: getTimestamp()
    })
  } catch (error) {
    console.error('Assistant error:', error)
    
    // Fallback response
    messages.value.push({
      role: 'assistant',
      content: generateFallbackResponse(question),
      timestamp: getTimestamp()
    })
  } finally {
    isTyping.value = false
    nextTick(() => {
      scrollToBottom()
    })
  }
}

function sendQuickAction(prompt) {
  userInput.value = prompt
  sendMessage()
}

function generateFallbackResponse(question) {
  // Simple fallback responses based on keywords
  const lowerQ = question.toLowerCase()
  
  if (lowerQ.includes('example')) {
    return `Great question! Let me provide some context. The concept mentioned in this slide can be understood through practical examples. Consider how it applies to everyday situations you encounter. Try to relate it to your own experiences to deepen your understanding.`
  } else if (lowerQ.includes('explain') || lowerQ.includes('what')) {
    return `Let me break this down for you. The key idea here is about understanding the fundamental principles. Focus on the main points presented in the slide, and think about how each part contributes to the overall concept. Would you like me to elaborate on any specific part?`
  } else if (lowerQ.includes('why')) {
    return `That's an excellent critical thinking question! Understanding the 'why' is crucial. This concept is important because it forms a foundation for more advanced topics. It helps us understand patterns and make predictions in this field of study.`
  } else if (lowerQ.includes('how')) {
    return `Good question about the process! The mechanism involves several steps that work together. Try to visualize each step and how it connects to the next. Drawing a simple diagram might help you understand the flow better.`
  } else {
    return `That's an interesting question! Based on the current slide content about "${props.currentSlide?.title || 'this topic'}", consider reviewing the key points and how they connect together. Feel free to ask more specific questions about any part you'd like to explore further.`
  }
}

function scrollToBottom() {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

function close() {
  emit('close')
}

// Watch for slide changes
watch(() => props.currentSlide, () => {
  // Could auto-add a context message when slide changes
})
</script>

<style scoped>
.assistant-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 1rem;
}

.assistant-drawer {
  width: 500px;
  max-width: 100%;
  height: calc(100vh - 2rem);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.glass-panel {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 1.5rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.5);
}

/* Header */
.assistant-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border-bottom: 2px solid rgba(139, 115, 85, 0.2);
  background: linear-gradient(135deg, #d2b48c, #daa520);
  border-radius: 1.5rem 1.5rem 0 0;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 1rem;
  color: white;
}

.assistant-icon {
  font-size: 2.5rem;
}

.assistant-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
}

.assistant-subtitle {
  margin: 0.25rem 0 0 0;
  font-size: 0.875rem;
  opacity: 0.9;
}

.close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 0.5rem;
  padding: 0.5rem;
  cursor: pointer;
  color: white;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

/* Chat Container */
.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.chat-message {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}

.chat-message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
  background: rgba(210, 180, 140, 0.3);
}

.message-bubble {
  max-width: 75%;
  padding: 1rem 1.25rem;
  border-radius: 1rem;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.user .message-bubble {
  background: linear-gradient(135deg, #d2b48c, #daa520);
  color: white;
  border-radius: 1rem 1rem 0.25rem 1rem;
}

.assistant .message-bubble {
  background: white;
  border: 1px solid rgba(139, 115, 85, 0.2);
  border-radius: 1rem 1rem 1rem 0.25rem;
}

.message-content {
  line-height: 1.6;
  color: #654321;
  font-size: 0.95rem;
}

.user .message-content {
  color: white;
}

.message-time {
  font-size: 0.75rem;
  margin-top: 0.5rem;
  opacity: 0.6;
}

/* Typing Indicator */
.typing-indicator {
  display: flex;
  gap: 0.25rem;
  padding: 0.5rem 0;
}

.typing-indicator span {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  background: #8b7355;
  animation: typing 1.4s ease-in-out infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.5;
  }
  30% {
    transform: translateY(-0.5rem);
    opacity: 1;
  }
}

/* Welcome Message */
.welcome-message {
  text-align: center;
  padding: 2rem;
  color: #654321;
}

.welcome-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.welcome-message h4 {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
}

.welcome-message p {
  margin: 1rem 0 0.5rem 0;
  font-size: 0.95rem;
  color: #8b7355;
}

.welcome-message ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.welcome-message li {
  text-align: left;
  padding: 0.75rem;
  background: rgba(210, 180, 140, 0.1);
  border-radius: 0.5rem;
  font-size: 0.9rem;
}

/* Quick Actions */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  padding: 0 1.5rem 1rem 1.5rem;
}

.quick-action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.8);
  border: 2px solid #d2b48c;
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
  font-weight: 500;
  color: #654321;
}

.quick-action-btn:hover {
  background: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(139, 115, 85, 0.2);
}

.quick-action-btn span:first-child {
  font-size: 1.5rem;
}

/* Input Area */
.input-area {
  display: flex;
  gap: 0.75rem;
  padding: 1.5rem;
  border-top: 2px solid rgba(139, 115, 85, 0.2);
  background: rgba(255, 255, 255, 0.95);
  border-radius: 0 0 1.5rem 1.5rem;
}

.message-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 2px solid #d2b48c;
  border-radius: 0.75rem;
  resize: none;
  font-family: inherit;
  font-size: 0.95rem;
  color: #654321;
  background: white;
  transition: all 0.2s ease;
}

.message-input:focus {
  outline: none;
  border-color: #8b7355;
  box-shadow: 0 0 0 3px rgba(139, 115, 85, 0.1);
}

.message-input::placeholder {
  color: #a08565;
}

.send-btn {
  padding: 0.75rem 1.25rem;
  background: linear-gradient(135deg, #d2b48c, #daa520);
  border: none;
  border-radius: 0.75rem;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(139, 115, 85, 0.3);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Transitions */
.drawer-slide-enter-active,
.drawer-slide-leave-active {
  transition: all 0.3s ease;
}

.drawer-slide-enter-from,
.drawer-slide-leave-to {
  opacity: 0;
}

.drawer-slide-enter-from .assistant-drawer {
  transform: translateX(100%);
}

.drawer-slide-leave-to .assistant-drawer {
  transform: translateX(100%);
}
</style>
