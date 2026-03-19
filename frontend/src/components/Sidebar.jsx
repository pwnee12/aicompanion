import { Link, useLocation } from 'react-router-dom'
import { 
  MessageSquare, 
  Users, 
  Image as ImageIcon, 
  Settings, 
  LogOut,
  Sparkles,
  Plus
} from 'lucide-react'
import { useAuthStore } from '../store/authStore'

export default function Sidebar() {
  const location = useLocation()
  const { user, logout } = useAuthStore()

  const navItems = [
    { path: '/', icon: MessageSquare, label: 'Chats' },
    { path: '/characters', icon: Users, label: 'Personajes' },
    { path: '/gallery', icon: ImageIcon, label: 'Galería' },
    { path: '/settings', icon: Settings, label: 'Configuración' },
  ]

  return (
    <aside className="fixed left-0 top-0 h-full w-64 bg-dark-800 border-r border-dark-700 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-dark-700">
        <div className="flex items-center gap-3">
          <Sparkles className="w-8 h-8 text-primary-500" />
          <div>
            <h1 className="text-xl font-bold text-white">AI Companion</h1>
            <p className="text-xs text-dark-400">Tu compañero virtual</p>
          </div>
        </div>
      </div>

      {/* Navegación */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            
            return (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-primary-600 text-white'
                      : 'text-dark-300 hover:bg-dark-700 hover:text-white'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                </Link>
              </li>
            )
          })}
        </ul>

        {/* Botón nuevo personaje */}
        <Link
          to="/characters/new"
          className="mt-4 flex items-center justify-center gap-2 w-full px-4 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors"
        >
          <Plus className="w-5 h-5" />
          Nuevo Personaje
        </Link>
      </nav>

      {/* Usuario */}
      <div className="p-4 border-t border-dark-700">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-full bg-primary-600 flex items-center justify-center text-white font-bold">
            {user?.username?.[0]?.toUpperCase() || 'U'}
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-white">{user?.username}</p>
            <p className="text-xs text-dark-400">{user?.email}</p>
          </div>
        </div>
        
        <button
          onClick={logout}
          className="flex items-center gap-2 w-full px-4 py-2 text-dark-400 hover:text-white transition-colors"
        >
          <LogOut className="w-4 h-4" />
          <span>Cerrar sesión</span>
        </button>
      </div>
    </aside>
  )
}
