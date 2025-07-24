import { ref, onUnmounted, nextTick } from 'vue'
import { useToast } from 'vue-toastification'

export function useWebSocket() {
  const toast = useToast()
  
  // WebSocket state
  const isConnected = ref(false)
  const isConnecting = ref(false)
  const connectionStatus = ref('disconnected') // disconnected, connecting, connected, error
  const lastError = ref(null)
  const messageQueue = ref([])
  const eventHandlers = ref(new Map())
  
  // WebSocket instance
  let ws = null
  let reconnectAttempts = 0
  let maxReconnectAttempts = 5
  let reconnectTimeout = null
  let heartbeatInterval = null
  let connectionId = null
  
  // Connect to WebSocket
  const connect = (url, userId = 'anonymous') => {
    if (ws && (ws.readyState === WebSocket.CONNECTING || ws.readyState === WebSocket.OPEN)) {
      console.log('WebSocket already connected or connecting')
      return
    }
    
    connectionStatus.value = 'connecting'
    isConnecting.value = true
    connectionId = `${userId}_${Date.now()}`
    
    // Add user_id as query parameter
    const wsUrl = `${url}?user_id=${encodeURIComponent(userId)}`
    
    try {
      ws = new WebSocket(wsUrl)
      
      ws.onopen = () => {
        console.log('WebSocket connected:', url)
        isConnected.value = true
        isConnecting.value = false
        connectionStatus.value = 'connected'
        lastError.value = null
        reconnectAttempts = 0
        
        // Send queued messages
        flushMessageQueue()
        
        // Start heartbeat
        startHeartbeat()
        
        // Emit connected event
        emit('connected', { url, userId, connectionId })
      }
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          handleMessage(data)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }
      
      ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason)
        isConnected.value = false
        isConnecting.value = false
        connectionStatus.value = 'disconnected'
        
        // Stop heartbeat
        stopHeartbeat()
        
        // Emit disconnected event
        emit('disconnected', { code: event.code, reason: event.reason, connectionId })
        
        // Attempt reconnection if not a clean close
        if (event.code !== 1000 && reconnectAttempts < maxReconnectAttempts) {
          scheduleReconnect(url, userId)
        }
      }
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        lastError.value = error
        connectionStatus.value = 'error'
        isConnecting.value = false
        
        // Emit error event
        emit('error', { error, connectionId })
      }
      
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
      connectionStatus.value = 'error'
      isConnecting.value = false
      lastError.value = error
    }
  }
  
  // Disconnect WebSocket
  const disconnect = () => {
    if (reconnectTimeout) {
      clearTimeout(reconnectTimeout)
      reconnectTimeout = null
    }
    
    stopHeartbeat()
    
    if (ws) {
      ws.close(1000, 'Client disconnect')
      ws = null
    }
    
    isConnected.value = false
    isConnecting.value = false
    connectionStatus.value = 'disconnected'
    reconnectAttempts = 0
  }
  
  // Send message
  const send = (message) => {
    const messageData = typeof message === 'string' ? message : JSON.stringify(message)
    
    if (isConnected.value && ws) {
      try {
        ws.send(messageData)
        return true
      } catch (error) {
        console.error('Error sending WebSocket message:', error)
        // Queue message for retry
        messageQueue.value.push(messageData)
        return false
      }
    } else {
      // Queue message for when connection is established
      messageQueue.value.push(messageData)
      console.log('Message queued - WebSocket not connected')
      return false
    }
  }
  
  // Handle incoming messages
  const handleMessage = (data) => {
    const messageType = data.type
    
    // Handle built-in message types
    if (messageType === 'pong') {
      // Heartbeat response - just log
      console.log('Received heartbeat pong')
      return
    }
    
    if (messageType === 'error') {
      console.error('Server error:', data.message)
      toast.error(`Server error: ${data.message}`)
      return
    }
    
    // Emit to registered handlers
    emit(messageType, data)
    emit('message', data) // Generic message event
  }
  
  // Event handling
  const on = (event, handler) => {
    if (!eventHandlers.value.has(event)) {
      eventHandlers.value.set(event, [])
    }
    eventHandlers.value.get(event).push(handler)
    
    // Return unsubscribe function
    return () => {
      const handlers = eventHandlers.value.get(event)
      if (handlers) {
        const index = handlers.indexOf(handler)
        if (index > -1) {
          handlers.splice(index, 1)
        }
      }
    }
  }
  
  const off = (event, handler) => {
    const handlers = eventHandlers.value.get(event)
    if (handlers && handler) {
      const index = handlers.indexOf(handler)
      if (index > -1) {
        handlers.splice(index, 1)
      }
    } else if (handlers) {
      // Remove all handlers for event
      eventHandlers.value.set(event, [])
    }
  }
  
  const emit = (event, data) => {
    const handlers = eventHandlers.value.get(event)
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data)
        } catch (error) {
          console.error(`Error in WebSocket event handler for ${event}:`, error)
        }
      })
    }
  }
  
  // Utility methods
  const flushMessageQueue = () => {
    while (messageQueue.value.length > 0 && isConnected.value) {
      const message = messageQueue.value.shift()
      try {
        ws.send(message)
      } catch (error) {
        console.error('Error sending queued message:', error)
        break
      }
    }
  }
  
  const scheduleReconnect = (url, userId) => {
    reconnectAttempts++
    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts - 1), 10000) // Exponential backoff, max 10s
    
    console.log(`Reconnection attempt ${reconnectAttempts}/${maxReconnectAttempts} in ${delay}ms`)
    
    reconnectTimeout = setTimeout(() => {
      if (reconnectAttempts <= maxReconnectAttempts) {
        connect(url, userId)
      } else {
        console.error('Max reconnection attempts reached')
        toast.error('Connection lost - please refresh the page')
      }
    }, delay)
  }
  
  const startHeartbeat = () => {
    heartbeatInterval = setInterval(() => {
      if (isConnected.value) {
        send({ type: 'ping' })
      }
    }, 30000) // Send ping every 30 seconds
  }
  
  const stopHeartbeat = () => {
    if (heartbeatInterval) {
      clearInterval(heartbeatInterval)
      heartbeatInterval = null
    }
  }
  
  // Convenience methods for onboarding-specific messages
  const startEditing = (field) => {
    send({ type: 'start_editing', field })
  }
  
  const stopEditing = () => {
    send({ type: 'stop_editing' })
  }
  
  const sendTyping = (field, content) => {
    send({ type: 'typing', field, content })
  }
  
  const sendCursorPosition = (field, position) => {
    send({ type: 'cursor_position', field, position })
  }
  
  const requestPresence = () => {
    send({ type: 'request_presence' })
  }
  
  // Cleanup on unmount
  onUnmounted(() => {
    disconnect()
  })
  
  return {
    // State
    isConnected,
    isConnecting,
    connectionStatus,
    lastError,
    
    // Methods
    connect,
    disconnect,
    send,
    on,
    off,
    
    // Convenience methods
    startEditing,
    stopEditing,
    sendTyping,
    sendCursorPosition,
    requestPresence
  }
} 