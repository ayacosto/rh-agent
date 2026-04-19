import React from "react"
import { useEffect, useRef } from "react"
import MessageBubble from "./MessageBubble"

export default function ChatWindow({ messages, loading }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, loading])

  return (
    <div className="flex-1 overflow-y-auto space-y-4 pr-1">

      {/* Message de bienvenue */}
      {messages.length === 0 && !loading && (
        <div className="flex flex-col items-center justify-center h-full text-center py-12">
          <div className="w-16 h-16 bg-[#1F4E79] rounded-full flex items-center justify-center mb-4">
            <span className="text-white text-2xl">💼</span>
          </div>
          <h2 className="text-lg font-semibold text-slate-700">Bonjour, comment puis-je vous aider ?</h2>
          <p className="text-sm text-slate-400 mt-2 max-w-md">
            Posez vos questions sur vos contrats, congés, paie ou toute autre question RH.
          </p>
          <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-lg">
            {[
              "Combien de jours de congés me reste-t-il ?",
              "Quand suis-je payé ce mois-ci ?",
              "Comment poser un arrêt maladie ?",
              "Comment obtenir une attestation employeur ?"
            ].map((q) => (
              <div key={q} className="bg-white border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-600 cursor-default hover:border-[#2E75B6] transition-colors">
                {q}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Messages */}
      {messages.map((msg, i) => (
        <MessageBubble key={i} message={msg} />
      ))}

      {/* Indicateur de chargement */}
      {loading && (
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 bg-[#1F4E79] rounded-full flex items-center justify-center flex-shrink-0">
            <span className="text-white text-xs font-bold">RH</span>
          </div>
          <div className="bg-white rounded-2xl rounded-tl-none px-4 py-3 shadow-sm">
            <div className="flex gap-1 items-center h-5">
              <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
              <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
              <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
            </div>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  )
}