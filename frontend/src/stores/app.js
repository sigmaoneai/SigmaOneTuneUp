import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useAppStore = defineStore('app', () => {
  // State
  const initialized = ref(false)
  const loading = ref(false)
  const error = ref(null)
  const systemHealth = ref({
    database: 'unknown',
    retell_ai: 'unknown',
    syncro_msp: 'unknown',
    overall: 'unknown'
  })
  const stats = ref({
    total_agents: 0,
    total_phone_numbers: 0,
    total_calls_today: 0,
    active_calls: 0
  })
  const notifications = ref([])

  // Getters
  const isHealthy = computed(() => systemHealth.value.overall === 'healthy')
  const hasErrors = computed(() => error.value !== null)

  // Actions
  async function initialize() {
    if (initialized.value) return

    loading.value = true
    error.value = null

    try {
      // Load initial data
      await Promise.all([
        checkSystemHealth(),
        loadDashboardStats()
      ])

      initialized.value = true
    } catch (err) {
      error.value = err.message || 'Failed to initialize application'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function checkSystemHealth() {
    try {
      const response = await api.dashboard.healthCheck()
      systemHealth.value = response.data
    } catch (error) {
      console.error('Health check failed:', error)
      systemHealth.value.overall = 'unhealthy'
    }
  }

  async function loadDashboardStats() {
    try {
      const response = await api.dashboard.getStats()
      stats.value = response.data
    } catch (error) {
      console.error('Failed to load dashboard stats:', error)
    }
  }

  function addNotification(notification) {
    notifications.value.push({
      id: Date.now(),
      timestamp: new Date(),
      ...notification
    })
  }

  function removeNotification(id) {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  function clearError() {
    error.value = null
  }

  // Periodic health checks
  function startHealthChecks() {
    setInterval(checkSystemHealth, 60000) // Check every minute
  }

  return {
    // State
    initialized,
    loading,
    error,
    systemHealth,
    stats,
    notifications,
    
    // Getters
    isHealthy,
    hasErrors,
    
    // Actions
    initialize,
    checkSystemHealth,
    loadDashboardStats,
    addNotification,
    removeNotification,
    clearError,
    startHealthChecks
  }
}) 