import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'

// Páginas
import Login from './pages/Login'
import Register from './pages/Register'
import Home from './pages/Home'
import Chat from './pages/Chat'
import Characters from './pages/Characters'
import CharacterBuilder from './pages/CharacterBuilder'
import Gallery from './pages/Gallery'
import Settings from './pages/Settings'

// Componentes de layout
import Sidebar from './components/Sidebar'

function App() {
  const { isAuthenticated } = useAuthStore()

  return (
    <div className="flex h-screen bg-dark-900">
      {isAuthenticated && <Sidebar />}
      <main className={`flex-1 overflow-hidden ${isAuthenticated ? 'ml-64' : ''}`}>
        <Routes>
          {/* Rutas públicas */}
          <Route path="/login" element={isAuthenticated ? <Navigate to="/" /> : <Login />} />
          <Route path="/register" element={isAuthenticated ? <Navigate to="/" /> : <Register />} />
          
          {/* Rutas protegidas */}
          <Route path="/" element={isAuthenticated ? <Home /> : <Navigate to="/login" />} />
          <Route path="/chat/:id" element={isAuthenticated ? <Chat /> : <Navigate to="/login" />} />
          <Route path="/characters" element={isAuthenticated ? <Characters /> : <Navigate to="/login" />} />
          <Route path="/characters/new" element={isAuthenticated ? <CharacterBuilder /> : <Navigate to="/login" />} />
          <Route path="/characters/:id/edit" element={isAuthenticated ? <CharacterBuilder /> : <Navigate to="/login" />} />
          <Route path="/gallery/:id" element={isAuthenticated ? <Gallery /> : <Navigate to="/login" />} />
          <Route path="/settings" element={isAuthenticated ? <Settings /> : <Navigate to="/login" />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
