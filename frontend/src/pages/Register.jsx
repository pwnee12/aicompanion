import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { authService } from '../services/api'
import { useAuthStore } from '../store/authStore'
import { Sparkles, Mail, Lock, User } from 'lucide-react'

export default function Register() {
  const navigate = useNavigate()
  const login = useAuthStore((state) => state.login)
  
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  })

  const registerMutation = useMutation({
    mutationFn: (data) => authService.register(data.username, data.email, data.password),
    onSuccess: (response) => {
      // Auto login después del registro
      loginMutation.mutate({ username: data.username, password: data.password })
    },
    onError: (error) => {
      console.error('Error registering:', error)
      alert(error.response?.data?.detail || 'Error al registrar')
    }
  })

  const loginMutation = useMutation({
    mutationFn: (data) => authService.login(data.username, data.password),
    onSuccess: (response) => {
      const { access_token } = response.data
      const user = response.data
      login(user, access_token)
      navigate('/')
    },
    onError: (error) => {
      console.error('Error logging in:', error)
    }
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    
    if (formData.password !== formData.confirmPassword) {
      alert('Las contraseñas no coinciden')
      return
    }

    if (formData.password.length < 6) {
      alert('La contraseña debe tener al menos 6 caracteres')
      return
    }

    registerMutation.mutate(formData)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-dark-900 px-4">
      <div className="max-w-md w-full">
        {/* Logo */}
        <div className="text-center mb-8">
          <Sparkles className="w-12 h-12 text-primary-500 mx-auto mb-4" />
          <h1 className="text-3xl font-bold text-white mb-2">AI Companion</h1>
          <p className="text-dark-400">Crea tu cuenta para comenzar</p>
        </div>

        {/* Formulario */}
        <form onSubmit={handleSubmit} className="bg-dark-800 rounded-2xl p-8 border border-dark-700">
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-2">
                Username
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-500" />
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  className="w-full pl-10 pr-4 py-3 bg-dark-900 border border-dark-700 rounded-lg text-white placeholder-dark-500 focus:outline-none focus:border-primary-500 transition-colors"
                  placeholder="Elige un username"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-dark-300 mb-2">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-500" />
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full pl-10 pr-4 py-3 bg-dark-900 border border-dark-700 rounded-lg text-white placeholder-dark-500 focus:outline-none focus:border-primary-500 transition-colors"
                  placeholder="tu@email.com"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-dark-300 mb-2">
                Contraseña
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-500" />
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full pl-10 pr-4 py-3 bg-dark-900 border border-dark-700 rounded-lg text-white placeholder-dark-500 focus:outline-none focus:border-primary-500 transition-colors"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-dark-300 mb-2">
                Confirmar contraseña
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-500" />
                <input
                  type="password"
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                  className="w-full pl-10 pr-4 py-3 bg-dark-900 border border-dark-700 rounded-lg text-white placeholder-dark-500 focus:outline-none focus:border-primary-500 transition-colors"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={registerMutation.isPending}
              className="w-full py-3 bg-primary-600 hover:bg-primary-700 disabled:bg-primary-800 text-white rounded-lg font-medium transition-colors"
            >
              {registerMutation.isPending ? 'Creando cuenta...' : 'Crear cuenta'}
            </button>
          </div>
        </form>

        {/* Login link */}
        <p className="text-center mt-6 text-dark-400">
          ¿Ya tienes cuenta?{' '}
          <Link to="/login" className="text-primary-500 hover:text-primary-400 font-medium">
            Inicia sesión
          </Link>
        </p>
      </div>
    </div>
  )
}
