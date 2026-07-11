import { createSlice } from '@reduxjs/toolkit'

let idCounter = 0
const nextId = () => `msg_${Date.now()}_${idCounter++}`

const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    messages: [
      {
        id: nextId(),
        role: 'assistant',
        kind: 'info',
        text:
          'Log interaction details here (e.g., "Met Dr. Smith, discussed Prodo-X efficacy, positive sentiment, shared brochure") or ask for help.',
      },
    ],
    isThinking: false,
  },
  reducers: {
    addUserMessage(state, action) {
      state.messages.push({ id: nextId(), role: 'user', kind: 'text', text: action.payload })
    },
    addAssistantMessage(state, action) {
      const { text, toolCalls } = action.payload
      state.messages.push({
        id: nextId(),
        role: 'assistant',
        kind: toolCalls && toolCalls.length ? 'success' : 'text',
        text,
        toolCalls: toolCalls || [],
      })
    },
    addErrorMessage(state, action) {
      state.messages.push({ id: nextId(), role: 'assistant', kind: 'error', text: action.payload })
    },
    setThinking(state, action) {
      state.isThinking = action.payload
    },
  },
})

export const { addUserMessage, addAssistantMessage, addErrorMessage, setThinking } = chatSlice.actions
export default chatSlice.reducer
