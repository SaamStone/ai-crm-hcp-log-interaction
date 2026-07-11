import { useRef } from 'react'
import LogInteractionForm from './components/LogInteractionForm'
import AIAssistantPanel from './components/AIAssistantPanel'

function makeSessionId() {
  if (crypto?.randomUUID) return crypto.randomUUID()
  return `session_${Date.now()}_${Math.random().toString(16).slice(2)}`
}

export default function App() {
  const sessionIdRef = useRef(makeSessionId())

  return (
    <div className="app-shell">
      <LogInteractionForm />
      <AIAssistantPanel sessionId={sessionIdRef.current} />
    </div>
  )
}
