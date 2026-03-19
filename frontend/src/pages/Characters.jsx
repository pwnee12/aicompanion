import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { characterService, chatService } from '../services/api'
import { Search, Plus, Sparkles, MessageSquare, Edit, Trash2 } from 'lucide-react'

export default function Characters() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [searchTerm, setSearchTerm] = useState('')
  const [filter, setFilter] = useState('all') // all, my, public

  const { data: characters = [], isLoading } = useQuery({
    queryKey: ['characters', filter],
    queryFn: () => {
      const params = filter === 'public' ? { public_only: true } : {}
      return characterService.getAll(params).then(res => res.data)
    }
  })

  const deleteMutation = useMutation({
    mutationFn: (id) => characterService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['characters'])
    }
  })

  const startChat = async (characterId) => {
    try {
      const response = await chatService.create(characterId)
      navigate(`/chat/${response.data.id}`)
    } catch (error) {
      console.error('Error creating chat:', error)
    }
  }

  const handleDelete = (e, id) => {
    e.preventDefault()
    if (confirm('¿Estás seguro de eliminar este personaje?')) {
      deleteMutation.mutate(id)
    }
  }

  const filteredCharacters = characters.filter(char =>
    char.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    char.description?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Directorio de Personajes</h1>
          <p className="text-dark-400">Explora y chatea con personajes creados por la comunidad</p>
        </div>
        
        <Link
          to="/characters/new"
          className="flex items-center gap-2 px-4 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors"
        >
          <Plus className="w-5 h-5" />
          Crear Personaje
        </Link>
      </div>

      {/* Buscador y filtros */}
      <div className="flex gap-4 mb-8">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-500" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Buscar personajes..."
            className="w-full pl-10 pr-4 py-3 bg-dark-800 border border-dark-700 rounded-lg text-white placeholder-dark-500 focus:outline-none focus:border-primary-500 transition-colors"
          />
        </div>
        
        <div className="flex gap-2">
          {['all', 'my', 'public'].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-3 rounded-lg font-medium transition-colors ${
                filter === f
                  ? 'bg-primary-600 text-white'
                  : 'bg-dark-800 text-dark-400 hover:text-white'
              }`}
            >
              {f === 'all' ? 'Todos' : f === 'my' ? 'Mis personajes' : 'Públicos'}
            </button>
          ))}
        </div>
      </div>

      {/* Grid de personajes */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="bg-dark-800 rounded-xl p-4 border border-dark-700 animate-pulse">
              <div className="aspect-square bg-dark-700 rounded-lg mb-4" />
              <div className="h-4 bg-dark-700 rounded w-3/4 mb-2" />
              <div className="h-3 bg-dark-700 rounded w-full mb-1" />
              <div className="h-3 bg-dark-700 rounded w-2/3" />
            </div>
          ))}
        </div>
      ) : filteredCharacters.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredCharacters.map((character) => (
            <div
              key={character.id}
              className="bg-dark-800 rounded-xl border border-dark-700 overflow-hidden hover:border-primary-500 transition-colors group"
            >
              {/* Avatar */}
              <div className="aspect-square bg-dark-700 overflow-hidden relative">
                {character.avatar_url ? (
                  <img
                    src={character.avatar_url}
                    alt={character.name}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <Sparkles className="w-12 h-12 text-dark-500" />
                  </div>
                )}
                
                {/* Badges */}
                <div className="absolute top-2 right-2 flex gap-1">
                  {character.is_nsfw && (
                    <span className="px-2 py-1 bg-red-600 text-white text-xs rounded">
                      18+
                    </span>
                  )}
                  {character.is_public && (
                    <span className="px-2 py-1 bg-green-600 text-white text-xs rounded">
                      Público
                    </span>
                  )}
                </div>
              </div>

              {/* Info */}
              <div className="p-4">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="text-white font-semibold">{character.name}</h3>
                  <span className="text-xs text-dark-400">{character.age ? `${character.age} años` : ''}</span>
                </div>
                
                <p className="text-sm text-dark-400 line-clamp-2 mb-4">
                  {character.description || 'Sin descripción'}
                </p>

                {/* Tags */}
                <div className="flex flex-wrap gap-2 mb-4">
                  {character.relationship_type && (
                    <span className="px-2 py-1 bg-dark-700 text-dark-300 text-xs rounded">
                      {character.relationship_type}
                    </span>
                  )}
                  {character.voice_tone && (
                    <span className="px-2 py-1 bg-dark-700 text-dark-300 text-xs rounded">
                      {character.voice_tone}
                    </span>
                  )}
                </div>

                {/* Acciones */}
                <div className="flex gap-2">
                  <button
                    onClick={() => startChat(character.id)}
                    className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg text-sm font-medium transition-colors"
                  >
                    <MessageSquare className="w-4 h-4" />
                    Chatear
                  </button>
                  
                  <Link
                    to={`/characters/${character.id}/edit`}
                    className="p-2 text-dark-400 hover:text-white hover:bg-dark-700 rounded-lg transition-colors"
                  >
                    <Edit className="w-4 h-4" />
                  </Link>
                  
                  <button
                    onClick={(e) => handleDelete(e, character.id)}
                    className="p-2 text-dark-400 hover:text-red-500 hover:bg-dark-700 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-16">
          <Sparkles className="w-16 h-16 text-dark-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">
            No se encontraron personajes
          </h3>
          <p className="text-dark-400 mb-6">
            {searchTerm ? 'Intenta con otro término de búsqueda' : 'Sé el primero en crear un personaje'}
          </p>
          <Link
            to="/characters/new"
            className="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors"
          >
            <Plus className="w-5 h-5" />
            Crear personaje
          </Link>
        </div>
      )}
    </div>
  )
}
