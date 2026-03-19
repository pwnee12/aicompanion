import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { characterService, chatService } from '../services/api'
import { MessageSquare, Users, Plus, Sparkles } from 'lucide-react'

export default function Home() {
  const { data: chats = [] } = useQuery({
    queryKey: ['chats'],
    queryFn: () => chatService.getAll().then(res => res.data)
  })

  const { data: characters = [] } = useQuery({
    queryKey: ['characters'],
    queryFn: () => characterService.getAll({ public_only: true }).then(res => res.data)
  })

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Bienvenido de nuevo</h1>
        <p className="text-dark-400">Continúa tus conversaciones o crea nuevos personajes</p>
      </div>

      {/* Chats recientes */}
      <section className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-primary-500" />
            Chats recientes
          </h2>
          <Link to="/characters" className="text-primary-500 hover:text-primary-400 text-sm font-medium">
            Ver todos
          </Link>
        </div>

        {chats.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {chats.slice(0, 6).map((chat) => (
              <Link
                key={chat.id}
                to={`/chat/${chat.id}`}
                className="bg-dark-800 rounded-xl p-4 border border-dark-700 hover:border-primary-500 transition-colors group"
              >
                <h3 className="text-white font-medium mb-1 group-hover:text-primary-400 transition-colors">
                  {chat.title || 'Chat sin título'}
                </h3>
                <p className="text-sm text-dark-400">
                  {new Date(chat.updated_at).toLocaleDateString('es-ES', {
                    day: 'numeric',
                    month: 'short',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </p>
              </Link>
            ))}
          </div>
        ) : (
          <div className="bg-dark-800 rounded-xl p-8 border border-dark-700 text-center">
            <MessageSquare className="w-12 h-12 text-dark-600 mx-auto mb-4" />
            <p className="text-dark-400 mb-4">No tienes chats aún</p>
            <Link
              to="/characters"
              className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors"
            >
              <Plus className="w-4 h-4" />
              Comenzar un chat
            </Link>
          </div>
        )}
      </section>

      {/* Personajes destacados */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white flex items-center gap-2">
            <Users className="w-5 h-5 text-primary-500" />
            Personajes destacados
          </h2>
          <Link to="/characters" className="text-primary-500 hover:text-primary-400 text-sm font-medium">
            Ver directorio
          </Link>
        </div>

        {characters.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {characters.slice(0, 4).map((character) => (
              <Link
                key={character.id}
                to={`/characters/${character.id}`}
                className="bg-dark-800 rounded-xl p-4 border border-dark-700 hover:border-primary-500 transition-colors group"
              >
                <div className="aspect-square rounded-lg bg-dark-700 mb-4 overflow-hidden">
                  {character.avatar_url ? (
                    <img
                      src={character.avatar_url}
                      alt={character.name}
                      className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <Sparkles className="w-8 h-8 text-dark-500" />
                    </div>
                  )}
                </div>
                <h3 className="text-white font-medium mb-1">{character.name}</h3>
                <p className="text-sm text-dark-400 line-clamp-2">
                  {character.description || 'Sin descripción'}
                </p>
              </Link>
            ))}
          </div>
        ) : (
          <div className="bg-dark-800 rounded-xl p-8 border border-dark-700 text-center">
            <Users className="w-12 h-12 text-dark-600 mx-auto mb-4" />
            <p className="text-dark-400 mb-4">No hay personajes públicos aún</p>
            <Link
              to="/characters/new"
              className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors"
            >
              <Plus className="w-4 h-4" />
              Crear personaje
            </Link>
          </div>
        )}
      </section>
    </div>
  )
}
