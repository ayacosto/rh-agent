import React from "react"
export default function MessageBubble({ message }) {
  const isUser = message.role === "user"

  return (
    <div className={`flex items-start gap-3 ${isUser ? "flex-row-reverse" : ""}`}>

      {/* Avatar */}
      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-bold
        ${isUser ? "bg-slate-300 text-slate-700" : "bg-[#1F4E79] text-white"}`}>
        {isUser ? "Moi" : "RH"}
      </div>

      {/* Contenu */}
      <div className={`max-w-[75%] ${isUser ? "items-end" : "items-start"} flex flex-col gap-1`}>
        <div className={`px-4 py-3 rounded-2xl shadow-sm text-sm leading-relaxed whitespace-pre-wrap
          ${isUser
            ? "bg-[#1F4E79] text-white rounded-tr-none"
            : "bg-white text-slate-800 rounded-tl-none"
          }`}>
          {message.content}
        </div>

        {/* Sources */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-1">
            {message.sources.map((src, i) => (
              <span key={i} className="text-xs bg-blue-50 border border-blue-100 text-blue-600 px-2 py-0.5 rounded-full">
                📄 {src.title}
              </span>
            ))}
          </div>
        )}

        {/* Timestamp */}
        {message.timestamp && (
          <span className="text-xs text-slate-400">
            {new Date(message.timestamp).toLocaleTimeString("fr-FR", {
              hour: "2-digit", minute: "2-digit"
            })}
          </span>
        )}
      </div>

    </div>
  )
}