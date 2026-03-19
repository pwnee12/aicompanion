import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { characterService } from '../services/api'
import { Save, ArrowLeft, Sparkles } from 'lucide-react'

export default function CharacterBuilder() {
  const { id } = useParams()
  const navigate = useNavigate()
  const isEdit = !!id

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    personality: '',
    backstory: '',
    appearance: '',
    voice_tone: '',
    relationship_type: '',
    age: '',
    is_public: false,
    is_nsfw: false,
    lora_scale: 0.8
  })

  // Cargar datos si es edición
  const { data: character } = useQuery({
    queryKey: ['character', id],
    queryFn: () => characterService.getById(id).then(res => res.data),
    enabled: isEdit
  })

  useEffect(() => {
    if (character) {
      setFormData({
        name: character.name || '',
        description: character.description || '',
        personality: character.personality || '',
        backstory: character.backstory || '',
        appearance: character.appearance || '',
        voice_tone: character.voice_tone || '',
        relationship_type: character.relationship_type || '',
        age: character.age || '',
        is_public: character.is_public || false,
        is_nsfw: character.is_nsfw || false,
        lora_scale: character.lora_scale || 0.8
      })
    }
  }, [character])

  // Mutation para guardar
  const saveMutation = useMutation({
    mutationFn: (data) => 
      isEdit 
        ? characterService.update(id, data)
        : characterService.create(data),
    onSuccess: () => {
      navigate('/characters')
    },
    onError: (error) => {
      console.error('Error saving character:', error)
      alert('Error al guardar personaje')
    }
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    
    const data = {
      ...formData,
      age: formData.age ? parseInt(formData.age) : null,
      lora_scale: parseFloat(formData.lora_scale)
    }
    
    saveMutation.mutate(data)
  }

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <button
          onClick={() => navigate('/characters')}
          className="p-2 hover:bg-dark-700 rounded-lg transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-dark-400" />
        </button>
        <div>
          <h1 className="text-3xl font-bold text-white mb-1">
            {isEdit ? 'Editar Personaje' : 'Crear Nuevo Personaje'}
          </h1>
          <p className="text-dark-400">
            Configura la personalidad, apariencia y comportamiento de tu personaje
          </p>
        </div>
      </div>

      {/* Formulario */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Información básica */}
        <section className="bg-dark-800 rounded-xl p-6 border border-dark-700">
          <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-primary-500" />
            Información Básica
          </h2>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-2">
                Nombre *
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-dark-900 border border-dark-700 rounded-lg text-white placeholder-dark-500 focus:outline-none focus:border-primary-500 transition-colors"
                placeholder="Ej: Sofía"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-2">
                Edad
              </label>
              <input
                type="number"
                name="age"
                value={formData.age}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-dark-900 border border-dark-700 rounded-lg text-white placeholder-dark-500 focus:outline-none focus:border-primary-500 transition-colors"
                placeholder="Ej: 25"
                min="1"
                max="150"
              />
            </div>
          </div>
          
          <div className="mt-4">
            <label className="block text-sm font-medium text-dark-300 mb-2">
              Descripción
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows={3}
              className="w-full px-4 py-3 bg-dark-900 border border-dark-700 rounded-lg text-white placeholder-dark-500 focus:outline-none focus:border-primary-500 transition-colors resize-none"
              placeholder="Una breve descripción del personaje..."
            />
          </div>
        </section>

        {/* Personalidad */}
        <section className="bg-dark-800 rounded-xl p-6 border border-dark-700">
          <h2 className="text-xl font-semibold text-white mb-4">Personalidad</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-2">
                Rasgos de personalidad
              </label>
              <textarea
                name="personality"
                value={formData.personality}
                onChange={handleChange}
                rows={4}
                className="w-full px-4 py-3 bg-dark-900 border border-dark-700 rounded-lg text-white placeholder-dark-500 focus:outline-none focus:border-primary-500 transition-colors resize-none"
                placeholder="Ej: Sarcástica pero cariñosa, creativa, divertida, empática..."
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-2">
                Trasfondo / Historia
              </label>
              <textarea
                name="backstory"
                value={formData.backstory}
                onChange={handleChange}
                rows={4}
                className="w-full px-4 py-3 bg-dark-900 border border-dark-700 rounded-lg text-white placeholder-dark-500 focus:outline-none focus:border-primary-500 transition-colors resize-none"
                placeholder="La historia del personaje, su pasado, motivaciones..."
              />
            </div>
          </div>
        </section>

        {/* Apariencia y Voz */}
        <section className="bg-dark-800 rounded-xl p-6 border border-dark-700">
          <h2 className="text-xl font-semibold text-white mb-4">Apariencia y Voz</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-2">
                Apariencia física
              </label>
              <textarea
                name="appearance"
                value={formData.appearance}
                onChange={handleChange}
                rows={3}
                className="w-full px-4 py-3 bg-dark-900 border border-dark-700 rounded-lg text-white placeholder-dark-500 focus:outline-none focus:border-primary-500 transition-colors resize-none"
                placeholder="Ej: Mujer joven, cabello rubio largo, ojos verdes, figura atlética..."
              />
              <p className="text-xs text-dark-500 mt-1">
                Esta descripción se usará para generar imágenes coherentes del personaje
              </p>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-dark-300 mb-2">
                  Tono de voz
                </label>
                <input
                  type="text"
                  name="voice_tone"
                  value={formData.voice_tone}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-dark-900 border border-dark-700 rounded-lg text-white placeholder-dark-500 focus:outline-none focus:border-primary-500 transition-colors"
                  placeholder="Ej: Cálido, juvenil, serio..."
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-dark-300 mb-2">
                  Tipo de relación
                </label>
                <select
                  name="relationship_type"
                  value={formData.relationship_type}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-dark-900 border border-dark-700 rounded-lg text-white focus:outline-none focus:border-primary-500 transition-colors"
                >
                  <option value="">Seleccionar...</option>
                  <option value="friend">Amigo/a</option>
                  <option value="romantic">Romántico/a</option>
                  <option value="mentor">Mentor</option>
                  <option value="companion">Compañero</option>
                  <option value="rival">Rival</option>
                  <option value="custom">Personalizado</option>
                </select>
              </div>
            </div>
          </div>
        </section>

        {/* Configuración avanzada */}
        <section className="bg-dark-800 rounded-xl p-6 border border-dark-700">
          <h2 className="text-xl font-semibold text-white mb-4">Configuración Avanzada</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-2">
                LoRA Scale (Coherencia visual)
              </label>
              <input
                type="range"
                name="lora_scale"
                value={formData.lora_scale}
                onChange={handleChange}
                min="0"
                max="1"
                step="0.1"
                className="w-full"
              />
              <div className="flex justify-between text-xs text-dark-500 mt-1">
                <span>Bajo (0.0)</span>
                <span>{formData.lora_scale}</span>
                <span>Alto (1.0)</span>
              </div>
              <p className="text-xs text-dark-500 mt-1">
                Controla qué tanto se parece la imagen generada al personaje base
              </p>
            </div>
            
            <div className="flex gap-6">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  name="is_public"
                  checked={formData.is_public}
                  onChange={handleChange}
                  className="w-4 h-4 rounded border-dark-600 text-primary-600 focus:ring-primary-500 bg-dark-900"
                />
                <span className="text-sm text-dark-300">Hacer público (visible en el directorio)</span>
              </label>
              
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  name="is_nsfw"
                  checked={formData.is_nsfw}
                  onChange={handleChange}
                  className="w-4 h-4 rounded border-dark-600 text-primary-600 focus:ring-primary-500 bg-dark-900"
                />
                <span className="text-sm text-dark-300">Contenido +18 (NSFW)</span>
              </label>
            </div>
          </div>
        </section>

        {/* Botones */}
        <div className="flex gap-4 justify-end">
          <button
            type="button"
            onClick={() => navigate('/characters')}
            className="px-6 py-3 bg-dark-700 hover:bg-dark-600 text-white rounded-lg font-medium transition-colors"
          >
            Cancelar
          </button>
          
          <button
            type="submit"
            disabled={saveMutation.isPending}
            className="flex items-center gap-2 px-6 py-3 bg-primary-600 hover:bg-primary-700 disabled:bg-primary-800 text-white rounded-lg font-medium transition-colors"
          >
            <Save className="w-5 h-5" />
            {saveMutation.isPending ? 'Guardando...' : 'Guardar Personaje'}
          </button>
        </div>
      </form>
    </div>
  )
}
