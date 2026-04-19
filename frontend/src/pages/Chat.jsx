import React from "react"
import { useState, useEffect } from "react"
import { fetchHistory } from "../services/api"
import { getUser } from "../services/auth"
import UserBadge from "../components/UserBadge"
import ChatWindow from "../components/ChatWindow"
import ChatInput from "../components/ChatInput"

export default function Chat() {
  const [messages, setMessages] = useState([])
  const [loading,  setLoading]  = useState(false)
  const user = getUser()

  useEffect(() => {
    async function loadHistory() {
      try {
        const history = await fetchHistory()
        const formatted = history.map((m) => ({
          role:      m.role,
          content:   m.content,
          timestamp: m.timestamp,
          sources:   []
        }))
        setMessages(formatted)
      } catch {
        // Historique vide au premier démarrage
      }
    }
    loadHistory()
  }, [])

  function addMessage(msg) {
    setMessages((prev) => [...prev, msg])
  }

  return (
    <div className="flex flex-col h-screen bg-slate-100">

      {/* Header */}
      <header className="bg-[#1F4E79] text-white px-6 py-4 flex items-center justify-between shadow-md">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-white rounded-full flex items-center justify-center">
            <span className="text-[#1F4E79] font-bold text-sm">RH</span>
          </div>
          <div>
            <h1 className="font-semibold text-lg leading-none">Agent RH Interne</h1>
            <p className="text-blue-200 text-xs mt-0.5">Assistant ressources humaines</p>
          </div>
        </div>
        <UserBadge user={user} />
      </header>

      {/* Zone de chat */}
      <div className="flex-1 overflow-hidden flex flex-col max-w-4xl w-full mx-auto px-4 py-4 gap-4">
        <ChatWindow messages={messages} loading={loading} />
        <ChatInput
          onSend={addMessage}
          setLoading={setLoading}
          loading={loading}
        />
      </div>

    </div>
  )
}