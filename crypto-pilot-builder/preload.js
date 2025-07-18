import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
  invoke: (channel, data) => ipcRenderer.invoke(channel, data),
  send: (channel, data) => ipcRenderer.send(channel, data),
  on: (channel, func) => ipcRenderer.on(channel, (event, ...args) => func(...args)),
  once: (channel, func) => ipcRenderer.once(channel, (event, ...args) => func(...args)),
  onTransactionStatus: (callback) => ipcRenderer.on('transaction-status', callback),
  confirmTransaction: (callback) => ipcRenderer.on('confirm-transaction', callback)
})