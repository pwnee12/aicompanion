const { contextBridge, ipcRenderer } = require('electron')

// Exponer APIs seguras al renderer
contextBridge.exposeInMainWorld('electron', {
  getBackendUrl: () => ipcRenderer.invoke('get-backend-url'),
  openExternalLink: (url) => ipcRenderer.invoke('open-external-link', url)
})
