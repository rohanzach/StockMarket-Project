import react from 'react'
import { BrowserRouter, Route, Routes, Navigate } from 'react-router-dom'
import  Home  from './pages/Home'
import  Register  from './pages/Register'
import  Login  from './pages/Login'
import  NotFound  from './pages/NotFound'
import  ProtectedRoute  from './components/ProtectedRoute'


function Logout(){
  localStorage.clear()
  return <Navigate to="/login" />
}

function RegisterAndLogout(){
  localStorage.clear()
  return <Register />
}

function App() {

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={
          <ProtectedRoute>
            <Home />
          </ProtectedRoute>
          } />
        <Route path="/register" element={<RegisterAndLogout />} />
        <Route path="/login" element={<Login />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>

  )
}

export default App
