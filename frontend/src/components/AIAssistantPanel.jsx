import { useState, useRef, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { addUserMessage, addAssistantMessage, addErrorMessage, setThinking } from '../store/chatSlice'
import { applyFormUpdate } from '../store/interactionSlice'
import { sendChatMessage } from '../api/client'

export default function AIAssistantPanel({ sessionId }) {
  const dispatch = useDispatch()
  const { messages, isThinking } = useSelector((s) => s.chat)
  const form = useSelector((s) => s.interaction.form)
  const [draft, setDraft] = useState('')
  const scrollRef = useRef(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, isThinking])

  const handleSend = async () => {
    const text = draft.trim()
    if (!text || isThinking) return
    dispatch(addUserMessage(text))
    setDraft('')
    dispatch(setThinking(true))
    try {
      const data = await sendChatMessage(sessionId, text, form)
      dispatch(applyFormUpdate({ form_state: data.form_state, changed_fields: data.changed_fields }))
      dispatch(addAssistantMessage({ text: data.reply, toolCalls: data.tool_calls }))
    } catch (e) {
      const detail = e?.response?.data?.detail || 'Something went wrong reaching the AI Assistant. Is the backend running on port 8000?'
      dispatch(addErrorMessage(detail))
    } finally {
      dispatch(setThinking(false))
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <section className="panel">
      <div className="ai-header">
        <p className="ai-header-title">🤖 AI Assistant</p>
        <p className="ai-header-sub">Log Interaction details here via chat</p>
      </div>

      <div className="ai-messages scrollbar-thin" ref={scrollRef}>
        {messages.map((m) => (
          <div key={m.id} className={`bubble ${m.role === 'user' ? 'user' : m.kind === 'error' ? 'error' : m.kind === 'success' ? 'success' : 'assistant'}`}>
            {m.kind === 'success' && <span>✅ </span>}
            {m.text}
            {m.toolCalls && m.toolCalls.length > 0 && (
              <div className="tool-trace">
                {m.toolCalls.map((tc, i) => (
                  <div className="tool-trace-item" key={i}>
                    <code>{tc.tool}</code> → {tc.result_summary}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
        {isThinking && (
          <div className="thinking-dots"><span /><span /><span /></div>
        )}
      </div>

      <div className="ai-input-bar">
        <textarea
          className="ai-textarea"
          placeholder="Describe Interaction..."
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button className="ai-send-btn" onClick={handleSend} disabled={isThinking || !draft.trim()}>
          AI<br />Log
        </button>
      </div>
    </section>
  )
}
