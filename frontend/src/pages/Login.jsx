import React from "react"
import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { loginRequest, fetchMe } from "../services/api"
import { saveToken, saveUser } from "../services/auth"

export default function Login() {
  const navigate  = useNavigate()
  const [email,    setEmail]    = useState("")
  const [password, setPassword] = useState("")
  const [error,    setError]    = useState("")
  const [loading,  setLoading]  = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      const { access_token } = await loginRequest(email, password)
      saveToken(access_token)
      const user = await fetchMe()
      saveUser(user)
      navigate("/chat")
    } catch (err) {
      setError("Email ou mot de passe incorrect.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#1F4E79] to-[#2E75B6]">
      <div className="bg-white rounded-2xl shadow-2xl p-10 w-full max-w-md">

        {/* Logo / Titre */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-[#1F4E79] rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-white text-2xl font-bold">RH</span>
          </div>
          <h1 className="text-2xl font-bold text-[#1F4E79]">Agent RH Interne</h1>
          <p className="text-slate-500 text-sm mt-1">Connectez-vous pour accéder à l'assistant</p>
        </div>

        {/* Formulaire */}
        <div className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Email professionnel
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="alice@demo.fr"
              className="w-full border border-slate-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#2E75B6]"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Mot de passe
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full border border-slate-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#2E75B6]"
              onKeyDown={(e) => e.key === "Enter" && handleSubmit(e)}
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 text-sm rounded-lg px-4 py-2">
              {error}
            </div>
          )}

          <button
            onClick={handleSubmit}
            disabled={loading || !email || !password}
            className="w-full bg-[#1F4E79] hover:bg-[#2E75B6] disabled:opacity-50 text-white font-semibold py-2.5 rounded-lg transition-colors"
          >
            {loading ? "Connexion..." : "Se connecter"}
          </button>
        </div>

        {/* Comptes de démo */}
        <div className="mt-8 border-t pt-6">
          <p className="text-xs text-slate-400 text-center mb-3">Comptes de démonstration</p>
          <div className="space-y-2">
            {[
              { email: "alice@demo.fr", role: "Employé" },
              { email: "bob@demo.fr",   role: "Manager" },
              { email: "sarah@demo.fr", role: "RH" }
            ].map((acc) => (
              <button
                key={acc.email}
                onClick={() => { setEmail(acc.email); setPassword("demo123") }}
                className="w-full text-left px-3 py-2 rounded-lg bg-slate-50 hover:bg-slate-100 transition-colors"
              >
                <span className="text-xs font-medium text-slate-700">{acc.email}</span>
                <span className="ml-2 text-xs bg-[#1F4E79] text-white px-2 py-0.5 rounded-full">
                  {acc.role}
                </span>
              </button>
            ))}
          </div>
        </div>

      </div>
    </div>
  )
}