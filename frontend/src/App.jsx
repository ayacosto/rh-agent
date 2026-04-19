import React from "react"
import { Routes, Route, Navigate } from "react-router-dom"
import Login from "./pages/Login"
import Chat from "./pages/Chat"
import { getToken } from "./services/auth"

function PrivateRoute({ children }) {
  return getToken() ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/chat"
        element={
          <PrivateRoute>
            <Chat />
          </PrivateRoute>
        }
      />
      <Route path="*" element={<Navigate to="/chat" replace />} />
    </Routes>
  )
}