import { ref, computed } from 'vue'
import apiService from '../services/apiService'

// Global session state
const sessions = ref(new Map())
const activeSessionId = ref(null)
const isLoading = ref(false)
const error = ref('')

export function useSessionManager() {
  // Computed
  const activeSessions = computed(() => {
    return Array.from(sessions.value.values()).sort((a, b) => 
      new Date(b.lastActivity) - new Date(a.lastActivity)
    )
  })

  const activeSession = computed(() => {
    return activeSessionId.value ? sessions.value.get(activeSessionId.value) : null
  })

  const activeMessages = computed(() => {
    return activeSession.value?.messages || []
  })

  // Methods
  const createSession = async (name = null) => {
    isLoading.value = true
    error.value = ''

    try {
      const sessionName = name || `Chat ${Date.now()}`
      const response = await apiService.createNewSession(sessionName)
      
      const session = {
        id: response.session_id,
        name: sessionName,
        messages: [],
        createdAt: new Date().toISOString(),
        lastActivity: new Date().toISOString()
      }

      sessions.value.set(session.id, session)
      activeSessionId.value = session.id

      console.log('Session created:', session.id)
      return session

    } catch (err) {
      console.error('Error creating session:', err)
      error.value = 'Erreur lors de la création de la session'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const loadSession = async (sessionId) => {
    if (!sessionId) return null

    isLoading.value = true
    error.value = ''

    try {
      const response = await apiService.getSession(sessionId)
      
      const messages = (response.messages || []).map(msg => ({
        text: msg.content || msg.text || '',
        isUser: msg.role === 'user',
        created_at: msg.created_at || msg.timestamp || new Date().toISOString()
      }))

      const session = {
        id: sessionId,
        name: response.session_name || `Session ${sessionId.substring(0, 8)}`,
        messages,
        createdAt: response.created_at || new Date().toISOString(),
        lastActivity: new Date().toISOString()
      }

      sessions.value.set(sessionId, session)
      activeSessionId.value = sessionId

      console.log('Session loaded:', sessionId, 'with', messages.length, 'messages')
      return session

    } catch (err) {
      console.error('Error loading session:', err)
      error.value = 'Erreur lors du chargement de la session'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const loadAllSessions = async () => {
    isLoading.value = true
    error.value = ''

    try {
      const response = await apiService.listSessions()
      const sessionList = response.sessions || []

      // Clear existing sessions
      sessions.value.clear()

      // Load each session
      for (const sessionInfo of sessionList) {
        try {
          await loadSession(sessionInfo.session_id)
        } catch (err) {
          console.error('Error loading session:', sessionInfo.session_id, err)
          // Continue loading other sessions even if one fails
        }
      }

      // Set active session to the most recent one
      if (activeSessions.value.length > 0) {
        activeSessionId.value = activeSessions.value[0].id
      }

      console.log('Loaded', sessions.value.size, 'sessions')
      return activeSessions.value

    } catch (err) {
      console.error('Error loading sessions:', err)
      error.value = 'Erreur lors du chargement des sessions'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const selectSession = async (sessionId) => {
    if (!sessionId) return null

    // If session is already loaded, just switch to it
    if (sessions.value.has(sessionId)) {
      activeSessionId.value = sessionId
      updateLastActivity(sessionId)
      return sessions.value.get(sessionId)
    }

    // Otherwise, load it first
    return await loadSession(sessionId)
  }

  const renameSession = async (sessionId, newName) => {
    if (!sessionId || !newName?.trim()) return false

    try {
      // Update locally first
      const session = sessions.value.get(sessionId)
      if (session) {
        session.name = newName.trim()
        session.lastActivity = new Date().toISOString()
        sessions.value.set(sessionId, session)
      }

      // Update on server (if API supports it)
      // await apiService.updateSession(sessionId, { name: newName.trim() })

      console.log('Session renamed:', sessionId, 'to', newName)
      return true

    } catch (err) {
      console.error('Error renaming session:', err)
      error.value = 'Erreur lors du renommage de la session'
      return false
    }
  }

  const deleteSession = async (sessionId) => {
    if (!sessionId) return false

    try {
      // Delete on server first
      await apiService.deleteSession(sessionId)

      // Remove from local state
      sessions.value.delete(sessionId)

      // If this was the active session, switch to another one
      if (activeSessionId.value === sessionId) {
        const remainingSessions = activeSessions.value
        activeSessionId.value = remainingSessions.length > 0 ? remainingSessions[0].id : null
      }

      console.log('Session deleted:', sessionId)
      return true

    } catch (err) {
      console.error('Error deleting session:', err)
      error.value = 'Erreur lors de la suppression de la session'
      return false
    }
  }

  const addMessage = (sessionId, message) => {
    const session = sessions.value.get(sessionId)
    if (!session) return false

    const messageWithTimestamp = {
      ...message,
      created_at: message.created_at || new Date().toISOString()
    }

    session.messages.push(messageWithTimestamp)
    session.lastActivity = new Date().toISOString()
    sessions.value.set(sessionId, session)

    return true
  }

  const addMessages = (sessionId, messages) => {
    if (!Array.isArray(messages)) return false

    const session = sessions.value.get(sessionId)
    if (!session) return false

    const messagesWithTimestamp = messages.map(msg => ({
      ...msg,
      created_at: msg.created_at || new Date().toISOString()
    }))

    session.messages.push(...messagesWithTimestamp)
    session.lastActivity = new Date().toISOString()
    sessions.value.set(sessionId, session)

    return true
  }

  const updateLastActivity = (sessionId) => {
    const session = sessions.value.get(sessionId)
    if (session) {
      session.lastActivity = new Date().toISOString()
      sessions.value.set(sessionId, session)
    }
  }

  const clearError = () => {
    error.value = ''
  }

  const getSessionById = (sessionId) => {
    return sessions.value.get(sessionId) || null
  }

  const getSessionsAsArray = () => {
    return activeSessions.value.map(session => ({
      id: session.id,
      name: session.name
    }))
  }

  return {
    // State
    sessions: readonly(sessions),
    activeSessionId: readonly(activeSessionId),
    isLoading: readonly(isLoading),
    error: readonly(error),

    // Computed
    activeSessions,
    activeSession,
    activeMessages,

    // Methods
    createSession,
    loadSession,
    loadAllSessions,
    selectSession,
    renameSession,
    deleteSession,
    addMessage,
    addMessages,
    updateLastActivity,
    clearError,
    getSessionById,
    getSessionsAsArray
  }
}

// Helper function to make refs readonly
function readonly(ref) {
  return computed(() => ref.value)
}
