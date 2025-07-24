import axios from 'axios'
import { useToast } from 'vue-toastification'

// Create axios instance
const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add request ID for tracking
    config.headers['X-Request-ID'] = `fe-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    const toast = useToast()
    
    if (error.response) {
      // Server responded with error
      const message = error.response.data?.detail || 'An error occurred'
      
      if (error.response.status >= 500) {
        toast.error(`Server Error: ${message}`)
      } else if (error.response.status === 404) {
        toast.warning('Resource not found')
      } else if (error.response.status >= 400) {
        toast.error(`Error: ${message}`)
      }
    } else if (error.request) {
      // Network error
      toast.error('Network error - please check your connection')
    } else {
      // Other error
      toast.error('An unexpected error occurred')
    }
    
    return Promise.reject(error)
  }
)

// API endpoints
const api = {
  // Dashboard
  dashboard: {
    getStats: () => apiClient.get('/dashboard/stats/'),
    healthCheck: () => apiClient.get('/dashboard/health-check/'),
    getCallActivity: (hours = 24) => apiClient.get(`/dashboard/call-activity/?hours=${hours}`),
    getAgentPerformance: (days = 7) => apiClient.get(`/dashboard/agent-performance/?days=${days}`),
    getSystemOverview: () => apiClient.get('/dashboard/system-overview/')
  },

  // Agents
  agents: {
    list: (params = {}) => apiClient.get('/agents/', { params }),
    get: (id) => apiClient.get(`/agents/${id}/`),
    create: (data) => apiClient.post('/agents/', data),
    update: (id, data) => apiClient.put(`/agents/${id}/`, data),
    delete: (id) => apiClient.delete(`/agents/${id}/`),
    testCall: (id, data) => apiClient.post(`/agents/${id}/test-call/`, data),
    syncWithRetell: (id) => apiClient.get(`/agents/${id}/sync-retell/`),
    syncAllFromRetell: () => apiClient.get('/agents/sync-all-from-retell/'),
    savePrompt: (id, promptName) => apiClient.post(`/agents/${id}/save-prompt/`, { prompt_name: promptName }),
    getPromptSuggestions: (id) => apiClient.get(`/agents/${id}/prompt-suggestions/`)
  },

  // Phone Numbers
  phoneNumbers: {
    list: (params = {}) => apiClient.get('/phone-numbers/', { params }),
    get: (id) => apiClient.get(`/phone-numbers/${id}/`),
    syncFromRetell: () => apiClient.get('/phone-numbers/sync-from-retell/'),
    assign: (data) => apiClient.post('/phone-numbers/assign/', data),
    unassign: (id) => apiClient.post(`/phone-numbers/${id}/unassign/`),
    getRetellDetails: (retellId) => apiClient.get(`/phone-numbers/retell/${retellId}/details/`)
  },

  // Calls
  calls: {
    list: (params = {}) => apiClient.get('/calls/', { params }),
    get: (id) => apiClient.get(`/calls/${id}/`),
    create: (data) => apiClient.post('/calls/', data),
    createAgentToAgent: (data) => apiClient.post('/calls/', { ...data, call_type: 'agent_to_agent' }),
    syncAllFromRetell: () => apiClient.get('/calls/sync-all/retell/'),
    getStats: () => apiClient.get('/calls/stats/today/')
  },

  // Prompts
  prompts: {
    list: () => apiClient.get('/prompts/'),
    get: (name) => apiClient.get(`/prompts/${name}/`),
    create: (name, data) => apiClient.post(`/prompts/${name}/`, data),
    update: (name, data) => apiClient.put(`/prompts/${name}/`, data),
    delete: (name) => apiClient.delete(`/prompts/${name}/`),
    preview: (name, data) => apiClient.post(`/prompts/${name}/preview/`, data),
    render: (name, variables) => apiClient.get(`/prompts/${name}/render/`, { params: { variables } }),
    createFromRetellAgent: (data) => apiClient.post('/prompts/from-retell-agent/', data),
    listCategories: () => apiClient.get('/prompts/categories/list/'),
    getByCategory: (category) => apiClient.get(`/prompts/category/${category}/`)
  },

  // SyncroMSP
  syncro: {
    // Tickets
    listTickets: (params = {}) => apiClient.get('/syncro/tickets/', { params }),
    getTicket: (id) => apiClient.get(`/syncro/tickets/${id}/`),
    createTicket: (data) => apiClient.post('/syncro/tickets/', data),
    syncTickets: (params = {}) => apiClient.get('/syncro/tickets/sync-from-syncro/', { params }),
    addTicketComment: (id, comment, hidden = false) => 
      apiClient.post(`/syncro/tickets/${id}/comments/`, { comment, hidden }),
    
    // Customers
    listCustomers: (limit = 100) => apiClient.get(`/syncro/customers/?limit=${limit}`),
    getCustomer: (id) => apiClient.get(`/syncro/customers/${id}/`),
    searchCustomers: (searchTerm) => apiClient.get(`/syncro/customers/search/${encodeURIComponent(searchTerm)}/`)
  },

  // Eval Tests
  evalTests: {
    list: (testScenarioId = null) => {
      const params = testScenarioId ? { test_scenario_id: testScenarioId } : {}
      return apiClient.get('/eval-tests/', { params })
    },
    get: (id) => apiClient.get(`/eval-tests/${id}/`),
    create: (data) => apiClient.post('/eval-tests/', data),
    update: (id, data) => apiClient.put(`/eval-tests/${id}/`, data),
    delete: (id) => apiClient.delete(`/eval-tests/${id}/`),
    evaluate: (id, score, notes = null) => apiClient.post(`/eval-tests/${id}/evaluate/`, { score, notes })
  },

  // Onboarding
  onboarding: {
    // Session management
    createSession: (userId) => apiClient.post('/onboarding/sessions/', { user_id: userId }),
    getSession: (sessionId) => apiClient.get(`/onboarding/sessions/${sessionId}/`),
    listSessions: (params = {}) => apiClient.get('/onboarding/sessions/', { params }),
    updateSession: (sessionId, data) => apiClient.put(`/onboarding/sessions/${sessionId}/`, data),
    deleteSession: (sessionId) => apiClient.delete(`/onboarding/sessions/${sessionId}/`),
    
    // Call management
    startCall: (sessionId, userId) => apiClient.post(`/onboarding/sessions/${sessionId}/start-call/`, { user_id: userId }),
    endCall: (sessionId) => apiClient.post(`/onboarding/sessions/${sessionId}/end-call/`),
    
    // Transcript and SOP updates
    addTranscriptMessage: (sessionId, message) => apiClient.post(`/onboarding/sessions/${sessionId}/transcript/`, message),
    updateSOPData: (sessionId, sopUpdate) => apiClient.post(`/onboarding/sessions/${sessionId}/sop-update/`, sopUpdate),
    
    // Export
    exportSOPs: (sessionId) => apiClient.get(`/onboarding/sessions/${sessionId}/export/`),
    
    // WebSocket connection helper
    getWebSocketUrl: (sessionId) => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const host = window.location.host
      return `${protocol}//${host}/api/v1/onboarding/sessions/${sessionId}/ws`
    }
  },

  // RetellAI Integration (uses existing backend APIs)
  retell: {
    // Agents - uses the existing agents API
    listAgents: (params = {}) => apiClient.get('/agents/', { params }),
    getAgent: (id) => apiClient.get(`/agents/${id}/`),
    
    // Calls - uses the existing calls API
    listCalls: (params = {}) => apiClient.get('/calls/', { params }),
    getCall: (id) => apiClient.get(`/calls/${id}/`),
    
    // Phone Numbers - uses the existing phone-numbers API
    listPhoneNumbers: (params = {}) => apiClient.get('/phone-numbers/', { params }),
    getPhoneNumber: (id) => apiClient.get(`/phone-numbers/${id}/`)
  },

  // Knowledge Base (ITGlue Integration)
  knowledgeBase: {
    // Statistics and overview
    getStats: () => apiClient.get('/knowledge-base/stats/'),
    
    // Categories
    getCategories: () => apiClient.get('/knowledge-base/categories/'),
    
    // Articles
    getArticles: (params = {}) => apiClient.get('/knowledge-base/articles/', { params }),
    getArticle: (id) => apiClient.get(`/knowledge-base/articles/${id}/`),
    createArticle: (data) => apiClient.post('/knowledge-base/articles/', data),
    updateArticle: (id, data) => apiClient.put(`/knowledge-base/articles/${id}/`, data),
    deleteArticle: (id) => apiClient.delete(`/knowledge-base/articles/${id}/`),
    searchArticles: (query) => apiClient.get(`/knowledge-base/articles/search/?q=${encodeURIComponent(query)}`),
    
    // Configurations
    getConfigurations: (params = {}) => apiClient.get('/knowledge-base/configurations/', { params }),
    getConfiguration: (id) => apiClient.get(`/knowledge-base/configurations/${id}/`),
    
    // Passwords
    getPasswords: (params = {}) => apiClient.get('/knowledge-base/passwords/', { params }),
    getPassword: (id) => apiClient.get(`/knowledge-base/passwords/${id}/`),
    
    // Contacts
    getContacts: (params = {}) => apiClient.get('/knowledge-base/contacts/', { params }),
    getContact: (id) => apiClient.get(`/knowledge-base/contacts/${id}/`),
    
    // ITGlue Sync
    syncWithITGlue: () => apiClient.post('/knowledge-base/sync/itglue/'),
    getSyncStatus: () => apiClient.get('/knowledge-base/sync/status/'),
    
    // Advanced search across all content types
    globalSearch: (query, filters = {}) => apiClient.get('/knowledge-base/search/', { 
      params: { q: query, ...filters } 
    })
  }
}

export default api 