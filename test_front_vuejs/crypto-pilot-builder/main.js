import { app, BrowserWindow, ipcMain } from 'electron'
import path from 'path'
import { fileURLToPath } from 'url'
import { spawn } from 'child_process'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

let mainWindow

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1000,
    height: 700,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true
    }
  })

  // Charge le front en dev
  mainWindow.loadURL('http://localhost:5173')
}

// Communication avec Python
ipcMain.handle('run-python', async (event, prompt) => {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python', [path.join(__dirname, 'python/chatbot.py'), prompt])

    let output = ''
    pythonProcess.stdout.on('data', data => output += data.toString())
    pythonProcess.stderr.on('data', data => console.error(data.toString()))

    pythonProcess.on('close', code => {
      if (code === 0) resolve(output.trim())
      else reject(`Erreur Python (code ${code})`)
    })
  })
})

app.whenReady().then(() => {
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})