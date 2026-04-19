import React from "react"
import { useState } from "react"
import { sendMessage } from "../services/api"

export default function ChatInput({ onSend, setLoading, loading }) {
  const [input, setInput] = useState("")

  async function handleSend() {
    const question = input.trim()
    if (!question || loading) return

    setInput("")

    // Afficher le message utilisateur immédiatement
    onSend({
      role:      "user",
      content:   question,
      timestamp: new Date().toISOString(),
      sources:   []
    })

    setLoading(true)

    try {
      const response = await sendMessage(question)
      onSend({
        role:      "assistant",
        content:   response.answer,
        timestamp: response.timestamp,
        sources:   response.sources || []
      })
    } catch (err) {
      onSend({
        role:      "assistant",
        content:   "Une erreur est survenue. Veuillez réessayer ou contacter le service RH directement.",
        timestamp: new Date().toISOString(),
        sources:   []
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 flex items-end gap-3 px-4 py-3">
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault()
            handleSend()
          }
        }}
        placeholder="Posez votre question RH... (Entrée pour envoyer)"
        rows={1}
        disabled={loading}
        className="flex-1 resize-none text-sm text-slate-700 placeholder-slate-400 focus:outline-none disabled:opacity-50 max-h-32 overflow-y-auto"
        style={{ lineHeight: "1.5rem" }}
      />
      <button
        onClick={handleSend}
        disabled={!input.trim() || loading}
        className="bg-[#1F4E79] hover:bg-[#2E75B6] disabled:opacity-40 text-white w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 transition-colors"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
          <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z" />
        </svg>
      </button>
    </div>
  )
}