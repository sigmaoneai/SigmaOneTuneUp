<template>
  <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
    <!-- Create Agent -->
    <router-link
      to="/agents/create"
      class="quick-action-card bg-primary-50 hover:bg-primary-100 border-primary-200"
    >
      <PlusIcon class="w-6 h-6 text-primary-600 mb-2" />
      <span class="text-sm font-medium text-primary-900">Create Agent</span>
    </router-link>

    <!-- Sync Phone Numbers -->
    <button
      @click="syncPhoneNumbers"
      :disabled="syncingPhones"
      class="quick-action-card bg-success-50 hover:bg-success-100 border-success-200 disabled:opacity-50"
    >
      <PhoneIcon 
        :class="[
          'w-6 h-6 text-success-600 mb-2',
          syncingPhones ? 'animate-spin' : ''
        ]" 
      />
      <span class="text-sm font-medium text-success-900">
        {{ syncingPhones ? 'Syncing...' : 'Sync Phones' }}
      </span>
    </button>

    <!-- View All Calls -->
    <router-link
      to="/calls"
      class="quick-action-card bg-warning-50 hover:bg-warning-100 border-warning-200"
    >
      <PhoneArrowUpRightIcon class="w-6 h-6 text-warning-600 mb-2" />
      <span class="text-sm font-medium text-warning-900">View Calls</span>
    </router-link>

    <!-- Browse Prompts -->
    <router-link
      to="/prompts"
      class="quick-action-card bg-purple-50 hover:bg-purple-100 border-purple-200"
    >
      <DocumentTextIcon class="w-6 h-6 text-purple-600 mb-2" />
      <span class="text-sm font-medium text-purple-900">Browse Prompts</span>
    </router-link>

    <!-- System Health -->
    <button
      @click="checkHealth"
      :disabled="checkingHealth"
      class="quick-action-card bg-gray-50 hover:bg-gray-100 border-gray-200 disabled:opacity-50"
    >
      <HeartIcon 
        :class="[
          'w-6 h-6 text-gray-600 mb-2',
          checkingHealth ? 'animate-pulse' : ''
        ]" 
      />
      <span class="text-sm font-medium text-gray-900">
        {{ checkingHealth ? 'Checking...' : 'Check Health' }}
      </span>
    </button>

    <!-- Knowledge Base -->
    <router-link
      to="/knowledge-base"
      class="quick-action-card bg-emerald-50 hover:bg-emerald-100 border-emerald-200"
    >
      <BookOpenIcon class="w-6 h-6 text-emerald-600 mb-2" />
      <span class="text-sm font-medium text-emerald-900">Knowledge Base</span>
    </router-link>

    <!-- Settings -->
    <router-link
      to="/settings"
      class="quick-action-card bg-indigo-50 hover:bg-indigo-100 border-indigo-200"
    >
      <CogIcon class="w-6 h-6 text-indigo-600 mb-2" />
      <span class="text-sm font-medium text-indigo-900">Settings</span>
    </router-link>
  </div>

  <!-- Recent Actions -->
  <div v-if="recentActions.length > 0" class="mt-8">
    <h4 class="text-sm font-medium text-gray-900 mb-4">Recent Actions</h4>
    <div class="space-y-2">
      <div
        v-for="action in recentActions"
        :key="action.id"
        class="flex items-center justify-between py-2 px-3 bg-gray-50 rounded-lg text-sm"
      >
        <div class="flex items-center space-x-2">
          <div :class="getActionIcon(action.type)" class="w-4 h-4"></div>
          <span class="text-gray-900">{{ action.description }}</span>
        </div>
        <span class="text-gray-500 text-xs">{{ formatTime(action.timestamp) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { formatDistanceToNow } from 'date-fns'
import { useAppStore } from '@/stores/app'
import api from '@/services/api'
import {
  PlusIcon,
  PhoneIcon,
  PhoneArrowUpRightIcon,
  DocumentTextIcon,
  HeartIcon,
  CogIcon,
  BookOpenIcon
} from '@heroicons/vue/24/outline'

const toast = useToast()
const appStore = useAppStore()

// Reactive state
const syncingPhones = ref(false)
const checkingHealth = ref(false)
const recentActions = ref([])

// Methods
const syncPhoneNumbers = async () => {
  syncingPhones.value = true
  try {
    const response = await api.phoneNumbers.syncFromRetell()
    const { new_count, updated_count } = response.data
    
    toast.success(`Synced ${new_count} new and ${updated_count} updated phone numbers`)
    
    // Add to recent actions
    addRecentAction('sync_phones', `Synced phone numbers: ${new_count} new, ${updated_count} updated`)
    
    // Refresh app stats
    await appStore.loadDashboardStats()
  } catch (error) {
    toast.error('Failed to sync phone numbers')
  } finally {
    syncingPhones.value = false
  }
}

const checkHealth = async () => {
  checkingHealth.value = true
  try {
    await appStore.checkSystemHealth()
    toast.info('System health check completed')
    
    const overallStatus = appStore.systemHealth.overall
    const statusMessage = overallStatus === 'healthy' 
      ? 'All systems healthy' 
      : `System status: ${overallStatus}`
    
    addRecentAction('health_check', statusMessage)
  } catch (error) {
    toast.error('Health check failed')
  } finally {
    checkingHealth.value = false
  }
}

const addRecentAction = (type, description) => {
  recentActions.value.unshift({
    id: Date.now(),
    type,
    description,
    timestamp: new Date()
  })
  
  // Keep only last 5 actions
  if (recentActions.value.length > 5) {
    recentActions.value = recentActions.value.slice(0, 5)
  }
  
  // Store in localStorage
  localStorage.setItem('recent_actions', JSON.stringify(recentActions.value))
}

const getActionIcon = (type) => {
  const iconMap = {
    sync_phones: 'bg-success-100 text-success-600',
    health_check: 'bg-gray-100 text-gray-600',
    create_agent: 'bg-primary-100 text-primary-600',
    test_call: 'bg-warning-100 text-warning-600'
  }
  return iconMap[type] || 'bg-gray-100 text-gray-600'
}

const formatTime = (timestamp) => {
  return formatDistanceToNow(new Date(timestamp), { addSuffix: true })
}

// Load recent actions on mount
onMounted(() => {
  const stored = localStorage.getItem('recent_actions')
  if (stored) {
    try {
      const actions = JSON.parse(stored)
      recentActions.value = actions.map(action => ({
        ...action,
        timestamp: new Date(action.timestamp)
      }))
    } catch (error) {
      console.error('Failed to load recent actions:', error)
    }
  }
})
</script>

<style scoped>
.quick-action-card {
  @apply flex flex-col items-center justify-center p-4 border-2 border-dashed rounded-lg transition-all duration-200 hover:shadow-sm cursor-pointer min-h-24;
}
</style> 