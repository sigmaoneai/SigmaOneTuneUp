<template>
  <div class="fixed bottom-0 right-0 z-40 lg:left-64">
    <div class="bg-gray-800 text-white px-4 py-2 text-xs">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <!-- Connection Status -->
          <div class="flex items-center space-x-1">
            <div :class="connectionStatus" class="w-2 h-2 rounded-full"></div>
            <span>{{ connectionText }}</span>
          </div>

          <!-- API Health -->
          <div class="flex items-center space-x-1">
            <span>API:</span>
            <span :class="apiHealthColor">{{ apiHealthText }}</span>
          </div>

          <!-- Last Updated -->
          <div v-if="lastUpdated" class="flex items-center space-x-1">
            <span>Updated:</span>
            <span class="text-gray-300">{{ formatTime(lastUpdated) }}</span>
          </div>
        </div>

        <div class="flex items-center space-x-4">
          <!-- Active Calls -->
          <div v-if="activeCalls > 0" class="flex items-center space-x-1">
            <div class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span>{{ activeCalls }} active call{{ activeCalls !== 1 ? 's' : '' }}</span>
          </div>

          <!-- Environment -->
          <div class="flex items-center space-x-1">
            <span class="text-gray-400">ENV:</span>
            <span :class="envColor">{{ environment }}</span>
          </div>

          <!-- Version -->
          <div class="text-gray-400">
            v1.0.0
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAppStore } from '@/stores/app'
import { formatDistanceToNow } from 'date-fns'

const appStore = useAppStore()
const lastUpdated = ref(null)
const connected = ref(true)
const environment = ref('dev') // This would come from config

// Update timestamp
const updateTimestamp = () => {
  lastUpdated.value = new Date()
}

// Connection status
const connectionStatus = computed(() => {
  return connected.value ? 'bg-green-400' : 'bg-red-400'
})

const connectionText = computed(() => {
  return connected.value ? 'Connected' : 'Disconnected'
})

// API health
const apiHealthColor = computed(() => {
  const health = appStore.systemHealth.overall
  switch (health) {
    case 'healthy': return 'text-green-400'
    case 'degraded': return 'text-yellow-400'
    case 'unhealthy': return 'text-red-400'
    default: return 'text-gray-400'
  }
})

const apiHealthText = computed(() => {
  const health = appStore.systemHealth.overall
  switch (health) {
    case 'healthy': return 'Healthy'
    case 'degraded': return 'Degraded'
    case 'unhealthy': return 'Unhealthy'
    default: return 'Unknown'
  }
})

// Active calls
const activeCalls = computed(() => appStore.stats.active_calls || 0)

// Environment color
const envColor = computed(() => {
  switch (environment.value) {
    case 'prod': return 'text-red-400'
    case 'staging': return 'text-yellow-400'
    case 'dev': return 'text-green-400'
    default: return 'text-gray-400'
  }
})

// Format time
const formatTime = (date) => {
  return formatDistanceToNow(date, { addSuffix: true })
}

// Setup periodic updates
let interval = null

onMounted(() => {
  updateTimestamp()
  
  // Update every 30 seconds
  interval = setInterval(() => {
    appStore.checkSystemHealth()
    appStore.loadDashboardStats()
    updateTimestamp()
  }, 30000)
})

onUnmounted(() => {
  if (interval) {
    clearInterval(interval)
  }
})
</script> 