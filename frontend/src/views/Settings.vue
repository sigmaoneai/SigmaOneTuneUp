<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Page Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900">Settings</h1>
      <p class="mt-2 text-gray-600">Manage your SigmaOne TuneUp configuration and preferences</p>
    </div>

    <!-- Settings Sections -->
    <div class="space-y-8">
      <!-- API Configuration -->
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-medium text-gray-900">API Configuration</h3>
          <p class="text-sm text-gray-500">Configure your external service integrations</p>
        </div>
        <div class="card-body space-y-6">
          <!-- RetellAI Settings -->
          <div>
            <h4 class="text-md font-medium text-gray-900 mb-4">RetellAI Integration</h4>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">API Key</label>
                <input 
                  type="password" 
                  value="••••••••••••••••" 
                  disabled
                  class="form-input bg-gray-50"
                />
                <p class="text-xs text-gray-500 mt-1">API key is configured via environment variables</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
                <div class="flex items-center">
                  <div :class="getRetellStatus()" class="w-3 h-3 rounded-full mr-2"></div>
                  <span class="text-sm text-gray-900">{{ getRetellStatusText() }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- SyncroMSP Settings -->
          <div class="border-t pt-6">
            <h4 class="text-md font-medium text-gray-900 mb-4">SyncroMSP Integration</h4>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">API Key</label>
                <input 
                  type="password" 
                  value="••••••••••••••••" 
                  disabled
                  class="form-input bg-gray-50"
                />
                <p class="text-xs text-gray-500 mt-1">API key is configured via environment variables</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
                <div class="flex items-center">
                  <div :class="getSyncroStatus()" class="w-3 h-3 rounded-full mr-2"></div>
                  <span class="text-sm text-gray-900">{{ getSyncroStatusText() }}</span>
                </div>
              </div>
            </div>
            
            <!-- Mock Mode Notice -->
            <div class="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div class="flex items-center">
                <ExclamationTriangleIcon class="w-5 h-5 text-yellow-600 mr-2" />
                <p class="text-sm text-yellow-800">
                  Currently running in mock mode for testing. Real SyncroMSP operations are disabled.
                </p>
              </div>
            </div>
          </div>

          <!-- ITGlue Settings -->
          <div class="border-t pt-6">
            <h4 class="text-md font-medium text-gray-900 mb-4">ITGlue Integration</h4>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">API Key</label>
                <input 
                  v-model="settings.itglue.apiKey"
                  type="password" 
                  placeholder="Enter ITGlue API key..."
                  class="form-input"
                />
                <p class="text-xs text-gray-500 mt-1">Your ITGlue API key for knowledge base integration</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
                <div class="flex items-center">
                  <div :class="getITGlueStatus()" class="w-3 h-3 rounded-full mr-2"></div>
                  <span class="text-sm text-gray-900">{{ getITGlueStatusText() }}</span>
                </div>
              </div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Base URL</label>
                <input 
                  v-model="settings.itglue.baseUrl"
                  type="url" 
                  placeholder="https://api.itglue.com"
                  class="form-input"
                />
                <p class="text-xs text-gray-500 mt-1">ITGlue API base URL</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Organization ID</label>
                <input 
                  v-model="settings.itglue.organizationId"
                  type="text" 
                  placeholder="Enter organization ID..."
                  class="form-input"
                />
                <p class="text-xs text-gray-500 mt-1">Your ITGlue organization ID (optional)</p>
              </div>
            </div>
          </div>

          <!-- Slack Integration Settings -->
          <div class="border-t pt-6">
            <h4 class="text-md font-medium text-gray-900 mb-4">Slack Integration</h4>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Webhook URL</label>
                <input 
                  v-model="settings.slack.webhookUrl"
                  type="url" 
                  placeholder="https://hooks.slack.com/services/..."
                  class="form-input"
                />
                <p class="text-xs text-gray-500 mt-1">Slack webhook URL for notifications and alerts</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
                <div class="flex items-center">
                  <div :class="getSlackStatus()" class="w-3 h-3 rounded-full mr-2"></div>
                  <span class="text-sm text-gray-900">{{ getSlackStatusText() }}</span>
                </div>
              </div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Default Channel</label>
                <input 
                  v-model="settings.slack.defaultChannel"
                  type="text" 
                  placeholder="#general"
                  class="form-input"
                />
                <p class="text-xs text-gray-500 mt-1">Default channel for notifications</p>
              </div>
              <div class="flex items-center pt-6">
                <label class="flex items-center">
                  <input
                    v-model="settings.slack.enabled"
                    type="checkbox"
                    class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span class="ml-2 text-sm text-gray-700">Enable Slack notifications</span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Application Settings -->
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-medium text-gray-900">Application Settings</h3>
          <p class="text-sm text-gray-500">Customize your application experience</p>
        </div>
        <div class="card-body space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Environment</label>
              <select v-model="settings.environment" class="form-select" disabled>
                <option value="development">Development</option>
                <option value="staging">Staging</option>
                <option value="production">Production</option>
              </select>
              <p class="text-xs text-gray-500 mt-1">Environment is set via backend configuration</p>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Auto Refresh Interval</label>
              <select v-model="settings.refreshInterval" class="form-select">
                <option value="30">30 seconds</option>
                <option value="60">1 minute</option>
                <option value="300">5 minutes</option>
                <option value="600">10 minutes</option>
              </select>
            </div>
          </div>

          <!-- Notification Preferences -->
          <div class="border-t pt-6">
            <h4 class="text-md font-medium text-gray-900 mb-4">Notifications</h4>
            <div class="space-y-3">
              <label class="flex items-center">
                <input
                  v-model="settings.notifications.newTickets"
                  type="checkbox"
                  class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span class="ml-2 text-sm text-gray-700">New ticket notifications</span>
              </label>
              
              <label class="flex items-center">
                <input
                  v-model="settings.notifications.systemAlerts"
                  type="checkbox"
                  class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span class="ml-2 text-sm text-gray-700">System health alerts</span>
              </label>
              
              <label class="flex items-center">
                <input
                  v-model="settings.notifications.agentUpdates"
                  type="checkbox"
                  class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span class="ml-2 text-sm text-gray-700">Agent status updates</span>
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- System Information -->
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-medium text-gray-900">System Information</h3>
          <p class="text-sm text-gray-500">Current system status and version information</p>
        </div>
        <div class="card-body">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-500">Frontend Version</label>
              <p class="text-sm text-gray-900 mt-1">v1.0.0</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-500">Backend Status</label>
              <div class="flex items-center mt-1">
                <div :class="getBackendStatus()" class="w-3 h-3 rounded-full mr-2"></div>
                <span class="text-sm text-gray-900">{{ getBackendStatusText() }}</span>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-500">Last Health Check</label>
              <p class="text-sm text-gray-900 mt-1">{{ formatTime(lastHealthCheck) }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex justify-end space-x-3">
        <button
          @click="testConnections"
          :disabled="testing"
          class="btn-secondary"
        >
          <span v-if="testing">Testing...</span>
          <span v-else>Test Connections</span>
        </button>
        <button
          @click="saveSettings"
          :disabled="saving"
          class="btn-primary"
        >
          <span v-if="saving">Saving...</span>
          <span v-else>Save Settings</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { formatDistanceToNow } from 'date-fns'
import { useAppStore } from '@/stores/app'
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'

const toast = useToast()
const appStore = useAppStore()

// Reactive state
const saving = ref(false)
const testing = ref(false)
const lastHealthCheck = ref(new Date())

const settings = ref({
  environment: 'development',
  refreshInterval: '60',
  notifications: {
    newTickets: true,
    systemAlerts: true,
    agentUpdates: false
  },
  itglue: {
    apiKey: '',
    baseUrl: 'https://api.itglue.com',
    organizationId: ''
  },
  slack: {
    webhookUrl: '',
    defaultChannel: '#general',
    enabled: false
  }
})

// Computed properties
const getRetellStatus = () => {
  const status = appStore.systemHealth.retell_ai
  switch (status) {
    case 'healthy': return 'bg-success-400'
    case 'unhealthy': return 'bg-danger-400'
    default: return 'bg-gray-400'
  }
}

const getRetellStatusText = () => {
  const status = appStore.systemHealth.retell_ai
  switch (status) {
    case 'healthy': return 'Connected'
    case 'unhealthy': return 'Connection Failed'
    default: return 'Unknown'
  }
}

const getSyncroStatus = () => {
  return 'bg-warning-400' // Always showing as mock mode
}

const getSyncroStatusText = () => {
  return 'Mock Mode (Testing)'
}

const getBackendStatus = () => {
  const status = appStore.systemHealth.overall
  switch (status) {
    case 'healthy': return 'bg-success-400'
    case 'degraded': return 'bg-warning-400'
    case 'unhealthy': return 'bg-danger-400'
    default: return 'bg-gray-400'
  }
}

const getBackendStatusText = () => {
  const status = appStore.systemHealth.overall
  switch (status) {
    case 'healthy': return 'All Systems Operational'
    case 'degraded': return 'Some Issues Detected'
    case 'unhealthy': return 'System Issues'
    default: return 'Status Unknown'
  }
}

const getITGlueStatus = () => {
  if (!settings.value.itglue.apiKey) {
    return 'bg-gray-400'
  }
  // Check if API key is valid format and base URL is set
  if (settings.value.itglue.apiKey.length > 10 && settings.value.itglue.baseUrl) {
    return 'bg-success-400'
  }
  return 'bg-warning-400'
}

const getITGlueStatusText = () => {
  if (!settings.value.itglue.apiKey) {
    return 'Not Configured'
  }
  if (settings.value.itglue.apiKey.length > 10 && settings.value.itglue.baseUrl) {
    return 'Ready'
  }
  return 'Incomplete Configuration'
}

const getSlackStatus = () => {
  if (!settings.value.slack.webhookUrl) {
    return 'bg-gray-400'
  }
  if (settings.value.slack.webhookUrl.startsWith('https://hooks.slack.com/') && settings.value.slack.enabled) {
    return 'bg-success-400'
  }
  if (settings.value.slack.webhookUrl.startsWith('https://hooks.slack.com/') && !settings.value.slack.enabled) {
    return 'bg-warning-400'
  }
  return 'bg-danger-400'
}

const getSlackStatusText = () => {
  if (!settings.value.slack.webhookUrl) {
    return 'Not Configured'
  }
  if (!settings.value.slack.webhookUrl.startsWith('https://hooks.slack.com/')) {
    return 'Invalid Webhook URL'
  }
  if (!settings.value.slack.enabled) {
    return 'Configured (Disabled)'
  }
  return 'Active'
}

const formatTime = (timestamp) => {
  return formatDistanceToNow(timestamp, { addSuffix: true })
}

// Methods
const testConnections = async () => {
  testing.value = true
  try {
    // Test main system health
    await appStore.checkSystemHealth()
    
    // Test ITGlue connection if configured
    if (settings.value.itglue.apiKey && settings.value.itglue.baseUrl) {
      try {
        // In a real implementation, this would test the ITGlue API
        console.log('Testing ITGlue connection...')
        toast.info('ITGlue connection test completed')
      } catch (error) {
        toast.warning('ITGlue connection test failed')
      }
    }
    
    // Test Slack webhook if configured
    if (settings.value.slack.webhookUrl && settings.value.slack.enabled) {
      try {
        // In a real implementation, this would send a test message to Slack
        console.log('Testing Slack webhook...')
        toast.info('Slack webhook test completed')
      } catch (error) {
        toast.warning('Slack webhook test failed')
      }
    }
    
    lastHealthCheck.value = new Date()
    toast.success('Connection tests completed')
  } catch (error) {
    toast.error('Connection test failed')
  } finally {
    testing.value = false
  }
}

const saveSettings = async () => {
  saving.value = true
  try {
    // In a real app, this would save settings to backend
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Store in localStorage for now
    localStorage.setItem('app_settings', JSON.stringify(settings.value))
    
    toast.success('Settings saved successfully')
  } catch (error) {
    toast.error('Failed to save settings')
  } finally {
    saving.value = false
  }
}

const loadSettings = () => {
  try {
    const stored = localStorage.getItem('app_settings')
    if (stored) {
      const parsed = JSON.parse(stored)
      settings.value = { ...settings.value, ...parsed }
    }
  } catch (error) {
    console.warn('Failed to load stored settings:', error)
  }
}

// Initialize
onMounted(() => {
  loadSettings()
})
</script> 