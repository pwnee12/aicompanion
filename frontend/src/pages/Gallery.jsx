import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { imageService } from '../services/api'
import { Image as ImageIcon, Download } from 'lucide-react'

export default function Gallery() {
  const { id } = useParams()

  const { data: images = [] } = useQuery({
    queryKey: ['character-images', id],
    queryFn: () => imageService.getCharacterImages(id).then(res => res.data)
  })

  const handleDownload = async (imageUrl, filename) => {
    try {
      const response = await fetch(imageUrl)
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Error downloading image:', error)
    }
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Galería de Imágenes</h1>
        <p className="text-dark-400">
          Todas las imágenes generadas por este personaje
        </p>
      </div>

      {/* Grid de imágenes */}
      {images.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {images.map((img, index) => (
            <div
              key={img.id}
              className="group relative aspect-square bg-dark-800 rounded-xl overflow-hidden border border-dark-700 hover:border-primary-500 transition-colors"
            >
              <img
                src={img.image_url}
                alt={`Image ${index + 1}`}
                className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
              />
              
              {/* Overlay con info */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                <div className="absolute bottom-0 left-0 right-0 p-4">
                  {img.prompt && (
                    <p className="text-white text-xs line-clamp-2 mb-3">
                      {img.prompt}
                    </p>
                  )}
                  
                  <div className="flex items-center justify-between">
                    <span className="text-dark-300 text-xs">
                      {new Date(img.created_at).toLocaleDateString('es-ES')}
                    </span>
                    
                    <button
                      onClick={() => handleDownload(img.image_url, `character_${img.id}.png`)}
                      className="p-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors"
                      title="Descargar"
                    >
                      <Download className="w-4 h-4 text-white" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-16">
          <ImageIcon className="w-16 h-16 text-dark-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">
            No hay imágenes aún
          </h3>
          <p className="text-dark-400">
            Las imágenes generadas durante el chat aparecerán aquí
          </p>
        </div>
      )}
    </div>
  )
}
