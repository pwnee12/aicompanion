import { useState } from 'react'
import { useAuthStore } from '../store/authStore'
import { Save, Bell, Palette, Volume2, Cpu } from 'lucide-react'

export default function Settings() {
  const { user, updateUser } = useAuthStore()
  
  const [settings, setSettings] = useState({
    // Apariencia
    theme: 'dark',
    language: 'es',
    
    // Chat
    autoGenerateImage: false,
    autoGenerateAudio: false,
    
    // Notificaciones
    enableNotifications: true,
    soundEnabled: true,
    
    // IA
    llmProvider: 'hybrid',
    imageProvider: 'replicate',
    ttsProvider: 'edge',
  })

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setSettings(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleSave = () => {
    // Guardar configuración en localStorage o backend
    localStorage.setItem('ai-companion-settings', JSON.stringify(settings))
    alert('Configuración guardada')
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Configuración</h1>
        <p className="text-dark-400">Personaliza tu experiencia con AI Companion</p>
      </div>

      {/* Información de cuenta */}
      <section className="bg-dark-800 rounded-xl p-6 border border-dark-700 mb-6">
        <h2 className="text-xl font-semibold text-white mb-4">Cuenta</h2>
        
        <div className="flex items-center gap-4 mb-4">
          <div className="w-16 h-16 rounded-full bg-primary-600 flex items-center justify-center text-white text-xl font-bold">
            {user?.username?.[0]?.toUpperCase() || 'U'}
          </div>
          <div>
            <p className="text-white font-medium">{user?.username}</p>
            <p className="text-dark-400 text-sm">{user?.email}</p>
          </div>
        </div>
      </section>

      {/* Apariencia */}
      <section className="bg-dark-800 rounded-xl p-6 border border-dark-700 mb-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <Palette className="w-5 h-5 text-primary-500" />
          Apariencia
        </h2>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-dark-300 mb-2">
              Tema
            </label>
            <select
              name="theme"
              value={settings.theme}
              onChange={handleChange}
              className="w-full px-4 py-3 bg-dark-900 border border-dark-700 rounded-lg text-white focus:outline-none focus:border-primary-500 transition-colors"
            >
              <option value="dark">Oscuro</option>
              <option value="light">Claro</option>
              <option value="system">Sistema</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-dark-300 mb-2">
              Idioma
            </label>
            <select
              name="language"
              value={settings.language}
              onChange={handleChange}
              className="w-full px-4 py-3 bg-dark-900 border border-dark-700 rounded-lg text-white focus:outline-none focus:border-primary-500 transition-colors"
            >
              <option value="es">Español</option>
              <option value="en">English</option>
              <option value="pt">Português</option>
            </select>
          </div>
        </div>
      </section>

      {/* Chat */}
      <section className="bg-dark-800 rounded-xl p-6 border border-dark-700 mb-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-primary-500" />
          Chat
        </h2>
        
        <div className="space-y-4">
          <label className="flex items-center justify-between cursor-pointer">
            <div>
              <p className="text-white font-medium">Generar imagen automáticamente</p>
              <p className="text-sm text-dark-400">Crear una imagen con cada respuesta del personaje</p>
            </div>
            <input
              type="checkbox"
              name="autoGenerateImage"
              checked={settings.autoGenerateImage}
              onChange={handleChange}
              className="w-5 h-5 rounded border-dark-600 text-primary-600 focus:ring-primary-500 bg-dark-900"
            />
          </label>
          
          <label className="flex items-center justify-between cursor-pointer">
            <div>
              <p className="text-white font-medium">Generar audio automáticamente</p>
              <p className="text-sm text-dark-400">Convertir respuestas a voz automáticamente</p>
            </div>
            <input
              type="checkbox"
              name="autoGenerateAudio"
              checked={settings.autoGenerateAudio}
              onChange={handleChange}
              className="w-5 h-5 rounded border-dark-600 text-primary-600 focus:ring-primary-500 bg-dark-900"
            />
          </label>
        </div>
      </section>

      {/* Notificaciones */}
      <section className="bg-dark-800 rounded-xl p-6 border border-dark-700 mb-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <Bell className="w-5 h-5 text-primary-500" />
          Notificaciones
        </h2>
        
        <div className="space-y-4">
          <label className="flex items-center justify-between cursor-pointer">
            <div>
              <p className="text-white font-medium">Activar notificaciones</p>
              <p className="text-sm text-dark-400">Recibir notificaciones del escritorio</p>
            </div>
            <input
              type="checkbox"
              name="enableNotifications"
              checked={settings.enableNotifications}
              onChange={handleChange}
              className="w-5 h-5 rounded border-dark-600 text-primary-600 focus:ring-primary-500 bg-dark-900"
            />
          </label>
          
          <label className="flex items-center justify-between cursor-pointer">
            <div>
              <p className="text-white font-medium">Sonidos</p>
              <p className="text-sm text-dark-400">Reproducir sonidos para mensajes</p>
            </div>
            <input
              type="checkbox"
              name="soundEnabled"
              checked={settings.soundEnabled}
              onChange={handleChange}
              className="w-5 h-5 rounded border-dark-600 text-primary-600 focus:ring-primary-500 bg-dark-900"
            />
          </label>
        </div>
      </section>

      {/* IA */}
      <section className="bg-dark-800 rounded-xl p-6 border border-dark-700 mb-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <Cpu className="w-5 h-5 text-primary-500" />
          Inteligencia Artificial
        </h2>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-dark-300 mb-2">
              Proveedor LLM
            </label>
            <select
              name="llmProvider"
              value={settings.llmProvider}
              onChange={handleChange}
              className="w-full px-4 py-3 bg-dark-900 border border-dark-700 rounded-lg text-white focus:outline-none focus:border-primary-500 transition-colors"
            >
              <option value="hybrid">Híbrido (Local + Cloud)</option>
              <option value="openai">OpenAI (GPT-4)</option>
              <option value="anthropic">Anthropic (Claude)</option>
              <option value="ollama">Ollama (Local)</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-dark-300 mb-2">
              Generación de Imágenes
            </label>
            <select
              name="imageProvider"
              value={settings.imageProvider}
              onChange={handleChange}
              className="w-full px-4 py-3 bg-dark-900 border border-dark-700 rounded-lg text-white focus:outline-none focus:border-primary-500 transition-colors"
            >
              <option value="replicate">Replicate (SDXL)</option>
              <option value="stability">Stability AI</option>
              <option value="local_sd">Stable Diffusion Local</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-dark-300 mb-2">
              Texto a Voz
            </label>
            <select
              name="ttsProvider"
              value={settings.ttsProvider}
              onChange={handleChange}
              className="w-full px-4 py-3 bg-dark-900 border border-dark-700 rounded-lg text-white focus:outline-none focus:border-primary-500 transition-colors"
            >
              <option value="edge">Edge TTS (Azure)</option>
              <option value="coqui">Coqui TTS (Local)</option>
              <option value="gtts">Google TTS</option>
            </select>
          </div>
        </div>
      </section>

      {/* Botón guardar */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          className="flex items-center gap-2 px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors"
        >
          <Save className="w-5 h-5" />
          Guardar Configuración
        </button>
      </div>
    </div>
  )
}

// Icono auxiliar
function MessageSquare({ className }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
    </svg>
  )
}
