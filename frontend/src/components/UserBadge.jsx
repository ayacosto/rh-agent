import React from "react"
import { useNavigate } from "react-router-dom"
import { logout } from "../services/auth"

const ROLE_LABELS = {
  employee: "Employé",
  manager:  "Manager",
  rh:       "RH"
}

const ROLE_COLORS = {
  employee: "bg-blue-100 text-blue-800",
  manager:  "bg-purple-100 text-purple-800",
  rh:       "bg-green-100 text-green-800"
}

export default function UserBadge({ user }) {
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate("/login")
  }

  if (!user) return null

  return (
    <div className="flex items-center gap-3">
      <div className="text-right hidden sm:block">
        <p className="text-sm font-medium text-white leading-none">{user.full_name}</p>
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium mt-1 inline-block ${ROLE_COLORS[user.role]}`}>
          {ROLE_LABELS[user.role] || user.role}
        </span>
      </div>
      <button
        onClick={handleLogout}
        className="text-xs bg-white/10 hover:bg-white/20 text-white px-3 py-1.5 rounded-lg transition-colors"
      >
        Déconnexion
      </button>
    </div>
  )
}