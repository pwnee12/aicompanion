import { useState, useRef, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { chatService, characterService } from '../services/api'
import { Send, Image as ImageIcon, Mic, Trash2, ArrowLeft } from 'lucide-react'

export default function Chat() {
  const { id } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const messagesEndRef = useRef(null)

  const [message, setMessage] = useState('')
  const [generateImage, setGenerateImage] = useState(false)
  const [generateAudio, setGenerateAudio] = useState(false)

  // Obtener chat y mensajes
  const { data: chat } = useQuery({
    queryKey: ['chat', id],
    queryFn: () => chatService.getById(id).then(res => res.data)
  })

  const { data: messages = [], refetch: refetchMessages } = useQuery({
    queryKey: ['messages', id],
    queryFn: () => chatService.getMessages(id).then(res => res.data),
    enabled: !!chat
  })

  // Obtener personaje
  const { data: character } = useQuery({
    queryKey: ['character', chat?.character_id],
    queryFn: () => characterService.getById(chat?.character_id).then(res => res.data),
    enabled: !!chat?.character_id
  })

  // Auto-scroll al final
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Mutation para enviar mensaje
  const sendMessageMutation = useMutation({
    mutationFn: (data) => chatService.sendMessage(id, data.message, {
      generateImage: data.generateImage,
      generateAudio: data.generateAudio
    }),
    onSuccess: () => {
      refetchMessages()
      setMessage('')
    },
    onError: (error) => {
      console.error('Error sending message:', error)
      alert('Error al enviar mensaje')
    }
  })

  // Mutation para eliminar chat
  const deleteChatMutation = useMutation({
    mutationFn: () => chatService.delete(id),
    onSuccess: () => {
      navigate('/')
    }
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!message.trim() || sendMessageMutation.isPending) return

    sendMessageMutation.mutate({
      message: message.trim(),
      generateImage,
      generateAudio
    })
  }

  const handleDeleteChat = () => {
    if (confirm('¿Estás seguro de eliminar este chat?')) {
      deleteChatMutation.mutate()
    }
  }

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 bg-dark-800 border-b border-dark-700">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/')}
            className="p-2 hover:bg-dark-700 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-dark-400" />
          </button>
          
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-primary-600 flex items-center justify-center">
              {character?.avatar_url ? (
                <img
                  src={character.avatar_url}
                  alt={character.name}
                  className="w-full h-full rounded-full object-cover"
                />
              ) : (
                <span className="text-white font-bold">
                  {character?.name?.[0]?.toUpperCase()}
                </span>
              )}
            </div>
            <div>
              <h2 className="text-white font-semibold">{character?.name || 'Cargando...'}</h2>
              <p className="text-sm text-dark-400">
                {character?.relationship_type || 'Personaje'}
              </p>
            </div>
          </div>
        </div>

        <button
          onClick={handleDeleteChat}
          className="p-2 text-dark-400 hover:text-red-500 hover:bg-dark-700 rounded-lg transition-colors"
          title="Eliminar chat"
        >
          <Trash2 className="w-5 h-5" />
        </button>
      </header>

      {/* Mensajes */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((msg, index) => {
          const isUser = msg.sender === 'user'
          
          return (
            <div
              key={msg.id}
              className={`flex ${isUser ? 'justify-end' : 'justify-start'} fade-in`}
            >
              <div
                className={`max-w-[70%] rounded-2xl px-4 py-3 ${
                  isUser
                    ? 'message-user text-white'
                    : 'message-character text-white'
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>
                
                {/* Imagen adjunta */}
                {msg.image_url && (
                  <div className="mt-3 rounded-lg overflow-hidden">
                    <img
                      src={msg.image_url}
                      alt="Generated image"
                      className="w-full h-auto"
                    />
                  </div>
                )}

                {/* Audio adjunto */}
                {msg.audio_url && (
                  <div className="mt-3">
                    <audio controls className="w-full">
                      <source src={msg.audio_url} type="audio/mpeg" />
                      Tu navegador no soporta audio
                    </audio>
                  </div>
                )}

                <p className={`text-xs mt-2 ${isUser ? 'text-primary-200' : 'text-dark-400'}`}>
                  {new Date(msg.created_at).toLocaleTimeString('es-ES', {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </p>
              </div>
            </div>
          )
        })}
        
        {sendMessageMutation.isPending && (
          <div className="flex justify-start fade-in">
            <div className="message-character rounded-2xl px-4 py-3">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-dark-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-dark-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-dark-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 bg-dark-800 border-t border-dark-700">
        {/* Opciones */}
        <div className="flex gap-4 mb-4 px-2">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={generateImage}
              onChange={(e) => setGenerateImage(e.target.checked)}
              className="w-4 h-4 rounded border-dark-600 text-primary-600 focus:ring-primary-500 bg-dark-900"
            />
            <ImageIcon className="w-4 h-4 text-dark-400" />
            <span className="text-sm text-dark-400">Generar imagen</span>
          </label>
          
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={generateAudio}
              onChange={(e) => setGenerateAudio(e.target.checked)}
              className="w-4 h-4 rounded border-dark-600 text-primary-600 focus:ring-primary-500 bg-dark-900"
            />
            <Mic className="w-4 h-4 text-dark-400" />
            <span className="text-sm text-dark-400">Generar audio</span>
          </label>
        </div>

        <div className="flex gap-3">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Escribe tu mensaje..."
            className="flex-1 px-4 py-3 bg-dark-900 border border-dark-700 rounded-xl text-white placeholder-dark-500 focus:outline-none focus:border-primary-500 transition-colors"
          />
          
          <button
            type="submit"
            disabled={!message.trim() || sendMessageMutation.isPending}
            className="px-6 py-3 bg-primary-600 hover:bg-primary-700 disabled:bg-primary-800 text-white rounded-xl font-medium transition-colors flex items-center gap-2"
          >
            <Send className="w-5 h-5" />
            Enviar
          </button>
        </div>
      </form>
    </div>
  )
}
