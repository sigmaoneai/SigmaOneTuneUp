<template>
  <div class="card">
    <div class="card-header">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-lg font-medium text-gray-900">Development Services</h3>
          <p class="text-sm text-gray-500">Manage local development services for E2E testing</p>
        </div>
        <div class="flex items-center space-x-2">
          <button @click="refreshServices" class="btn-sm btn-secondary">
            <ArrowPathIcon class="w-3 h-3 mr-1" />
            Refresh
          </button>
          <button @click="startAllServices" :disabled="allServicesRunning" class="btn-sm btn-primary">
            <PlayIcon class="w-3 h-3 mr-1" />
            Start All
          </button>
        </div>
      </div>
    </div>
    
    <div class="card-body space-y-4">
      <!-- Backend Service -->
      <div class="service-item">
        <div class="flex items-center justify-between p-3 border rounded-lg" :class="{
          'border-green-200 bg-green-50': services.backend.status === 'running',
          'border-red-200 bg-red-50': services.backend.status === 'stopped',
          'border-yellow-200 bg-yellow-50': services.backend.status === 'starting'
        }">
          <div class="flex items-center space-x-3">
            <div class="flex-shrink-0">
              <div :class="[
                'w-3 h-3 rounded-full',
                services.backend.status === 'running' ? 'bg-green-500' : 
                services.backend.status === 'starting' ? 'bg-yellow-500' : 'bg-red-500'
              ]"></div>
            </div>
            <div>
              <div class="text-sm font-medium text-gray-900">Backend API</div>
              <div class="text-xs text-gray-500">
                FastAPI server on port 8000
                <span v-if="services.backend.url" class="ml-2">
                  → <a :href="services.backend.url" target="_blank" class="text-blue-600 hover:text-blue-800">
                    {{ services.backend.url }}
                  </a>
                </span>
              </div>
            </div>
          </div>
          <div class="flex items-center space-x-2">
            <span :class="[
              'px-2 py-1 text-xs font-medium rounded',
              services.backend.status === 'running' ? 'bg-green-100 text-green-800' :
              services.backend.status === 'starting' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'
            ]">
              {{ services.backend.status }}
            </span>
            <button 
              v-if="services.backend.status === 'stopped'"
              @click="startService('backend')"
              class="btn-xs btn-primary"
            >
              <PlayIcon class="w-3 h-3" />
            </button>
            <button 
              v-if="services.backend.status === 'running'"
              @click="stopService('backend')"
              class="btn-xs btn-secondary"
            >
              <StopIcon class="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>

      <!-- Ngrok Tunnels -->
      <div class="service-item">
        <div class="flex items-center justify-between p-3 border rounded-lg" :class="{
          'border-green-200 bg-green-50': services.ngrok.status === 'running',
          'border-red-200 bg-red-50': services.ngrok.status === 'stopped',
          'border-yellow-200 bg-yellow-50': services.ngrok.status === 'starting'
        }">
          <div class="flex items-center space-x-3">
            <div class="flex-shrink-0">
              <div :class="[
                'w-3 h-3 rounded-full',
                services.ngrok.status === 'running' ? 'bg-green-500' : 
                services.ngrok.status === 'starting' ? 'bg-yellow-500' : 'bg-red-500'
              ]"></div>
            </div>
            <div class="flex-1">
              <div class="text-sm font-medium text-gray-900">Ngrok Tunnels</div>
                             <div class="text-xs text-gray-500">
                 <strong>Backend (8000):</strong> 
                 <span v-if="services.ngrok.tunnels.backend">
                   <a :href="services.ngrok.tunnels.backend" target="_blank" class="text-blue-600 hover:text-blue-800 ml-1">
                     {{ services.ngrok.tunnels.backend }}
                   </a>
                 </span>
                 <span v-else class="text-gray-400 ml-1">Not running</span>
               </div>
            </div>
          </div>
          <div class="flex items-center space-x-2">
            <span :class="[
              'px-2 py-1 text-xs font-medium rounded',
              services.ngrok.status === 'running' ? 'bg-green-100 text-green-800' :
              services.ngrok.status === 'starting' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'
            ]">
              {{ services.ngrok.status }}
            </span>
            <button 
              v-if="services.ngrok.status === 'stopped'"
              @click="startService('ngrok')"
              class="btn-xs btn-primary"
            >
              <PlayIcon class="w-3 h-3" />
            </button>
            <button 
              v-if="services.ngrok.status === 'running'"
              @click="stopService('ngrok')"
              class="btn-xs btn-secondary"
            >
              <StopIcon class="w-3 h-3" />
            </button>
          </div>
        </div>
             </div>

       <!-- Frontend Service -->
       <div class="service-item">
         <div class="flex items-center justify-between p-3 border rounded-lg" :class="{
           'border-green-200 bg-green-50': services.frontend.status === 'running',
           'border-red-200 bg-red-50': services.frontend.status === 'stopped',
           'border-yellow-200 bg-yellow-50': services.frontend.status === 'starting'
         }">
           <div class="flex items-center space-x-3">
             <div class="flex-shrink-0">
               <div :class="[
                 'w-3 h-3 rounded-full',
                 services.frontend.status === 'running' ? 'bg-green-500' : 
                 services.frontend.status === 'starting' ? 'bg-yellow-500' : 'bg-red-500'
               ]"></div>
             </div>
             <div>
               <div class="text-sm font-medium text-gray-900">Frontend Dev Server</div>
               <div class="text-xs text-gray-500">
                 Vue.js on port 3000
                 <span v-if="services.frontend.url" class="ml-2">
                   → <a :href="services.frontend.url" target="_blank" class="text-blue-600 hover:text-blue-800">
                     {{ services.frontend.url }}
                   </a>
                 </span>
               </div>
             </div>
           </div>
           <div class="flex items-center space-x-2">
             <span :class="[
               'px-2 py-1 text-xs font-medium rounded',
               services.frontend.status === 'running' ? 'bg-green-100 text-green-800' :
               services.frontend.status === 'starting' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'
             ]">
               {{ services.frontend.status }}
             </span>
             <span class="text-xs text-green-600 font-medium">
               Currently Active
             </span>
           </div>
         </div>
       </div>

       <!-- RetellAI Webhook Status -->
      <div class="service-item">
        <div class="flex items-center justify-between p-3 border rounded-lg" :class="{
          'border-green-200 bg-green-50': webhookStatus.status === 'configured',
          'border-yellow-200 bg-yellow-50': webhookStatus.status === 'needs_update',
          'border-red-200 bg-red-50': webhookStatus.status === 'not_configured'
        }">
          <div class="flex items-center space-x-3">
            <div class="flex-shrink-0">
              <div :class="[
                'w-3 h-3 rounded-full',
                webhookStatus.status === 'configured' ? 'bg-green-500' : 
                webhookStatus.status === 'needs_update' ? 'bg-yellow-500' : 'bg-red-500'
              ]"></div>
            </div>
            <div>
              <div class="text-sm font-medium text-gray-900">RetellAI Webhook</div>
              <div class="text-xs text-gray-500">
                <div>Current: {{ webhookStatus.current || 'Not set' }}</div>
                <div v-if="webhookStatus.suggested">
                  Suggested: {{ webhookStatus.suggested }}
                </div>
              </div>
            </div>
          </div>
          <div class="flex items-center space-x-2">
            <span :class="[
              'px-2 py-1 text-xs font-medium rounded',
              webhookStatus.status === 'configured' ? 'bg-green-100 text-green-800' :
              webhookStatus.status === 'needs_update' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'
            ]">
              {{ webhookStatus.status === 'configured' ? 'OK' : 
                 webhookStatus.status === 'needs_update' ? 'Update Needed' : 'Not Set' }}
            </span>
            <button 
              v-if="webhookStatus.status !== 'configured'"
              @click="updateWebhookUrl"
              :disabled="!services.ngrok.tunnels.backend"
              class="btn-xs btn-primary"
              title="Automatically update all RetellAI agents with current webhook URL"
            >
              <LinkIcon class="w-3 h-3 mr-1" />
              Auto-Update
            </button>
          </div>
        </div>
      </div>

             <!-- Team Member Setup -->
       <div v-if="!services.ngrok.tunnels.backend" class="border-t pt-4">
         <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
           <div class="text-sm font-medium text-yellow-900 mb-2">🔧 Setup Required</div>
           <div class="text-xs text-yellow-800 space-y-1">
             <div>1. Get your ngrok URL: <code class="bg-white px-1 rounded">ngrok http --url=your-name-sigmaonetune.ngrok.io 8000</code></div>
             <div>2. Add to <code class="bg-white px-1 rounded">frontend/.env</code>:</div>
             <div class="ml-4"><code class="bg-white px-2 py-1 rounded block">VITE_NGROK_URL=https://your-name-sigmaonetune.ngrok.io</code></div>
             <div>3. Restart the frontend dev server</div>
           </div>
         </div>
       </div>

       <!-- Quick Actions -->
       <div class="border-t pt-4">
         <div class="flex items-center justify-between">
           <div class="text-sm font-medium text-gray-900">Quick Actions</div>
           <div class="flex items-center space-x-2">
             <button @click="openApiDocs" :disabled="!services.backend.url" class="btn-xs btn-secondary">
               <DocumentTextIcon class="w-3 h-3 mr-1" />
               API Docs
             </button>
             <button @click="testWebhook" :disabled="!services.ngrok.tunnels.backend" class="btn-xs btn-secondary">
               <CheckCircleIcon class="w-3 h-3 mr-1" />
               Test Webhook
             </button>
             <button @click="copyWebhookUrl" :disabled="!services.ngrok.tunnels.backend" class="btn-xs btn-secondary">
               <ClipboardIcon class="w-3 h-3 mr-1" />
               Copy URL
             </button>
           </div>
         </div>
       </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useToast } from 'vue-toastification'
import {
  PlayIcon,
  StopIcon,
  ArrowPathIcon,
  DocumentTextIcon,
  CheckCircleIcon,
  ClipboardIcon,
  LinkIcon
} from '@heroicons/vue/24/outline'

const toast = useToast()

// Service states
const services = ref({
  backend: {
    status: 'stopped', // stopped, starting, running
    url: null,
    port: 8000
  },
  ngrok: {
    status: 'stopped',
    tunnels: {
      backend: null, // https://classic-husky-steady.ngrok-free.app
    }
  },
  frontend: {
    status: 'stopped',
    url: null,
    port: 3000
  }
})

const webhookStatus = ref({
  status: 'not_configured', // not_configured, needs_update, configured
  current: null,
  suggested: null
})

// Auto-refresh timer
let refreshTimer = null

 const allServicesRunning = computed(() => {
   return services.value.backend.status === 'running' && 
          services.value.ngrok.status === 'running'
   // Frontend is obviously running if we're viewing this page!
 })

const refreshServices = async () => {
  try {
    // Check backend status
    try {
      const response = await fetch('http://localhost:8000/health')
      if (response.ok) {
        services.value.backend.status = 'running'
        services.value.backend.url = 'http://localhost:8000'
      } else {
        services.value.backend.status = 'stopped'
        services.value.backend.url = null
      }
    } catch {
      services.value.backend.status = 'stopped'
      services.value.backend.url = null
    }

         // Check ngrok status via backend proxy (avoids CORS issues)
     try {
       const response = await fetch('http://localhost:8000/api/v1/dashboard/ngrok-status')
       if (response.ok) {
         const data = await response.json()
         const tunnels = data.tunnels || []
         
         services.value.ngrok.status = tunnels.length > 0 ? 'running' : 'stopped'
         
         // Find backend tunnel (port 8000)
         const backendTunnel = tunnels.find(t => 
           t.config && t.config.addr && t.config.addr.includes('8000') && t.proto === 'https'
         )
         services.value.ngrok.tunnels.backend = backendTunnel?.public_url || null
         
       } else {
         services.value.ngrok.status = 'stopped'
         services.value.ngrok.tunnels.backend = null
       }
     } catch {
       // Fallback - get from environment variable
       const envNgrokUrl = import.meta.env.VITE_NGROK_URL
       
       if (envNgrokUrl) {
         services.value.ngrok.status = 'running'
         services.value.ngrok.tunnels.backend = envNgrokUrl
       } else {
         services.value.ngrok.status = 'stopped'
         services.value.ngrok.tunnels.backend = null
       }
     }

     // Frontend status - if we're viewing this page, it's obviously running!
     services.value.frontend.status = 'running'
     services.value.frontend.url = 'http://localhost:3000'

    // Update webhook status
    updateWebhookStatus()
    
  } catch (error) {
    console.error('Error refreshing services:', error)
    toast.error('Failed to refresh service status')
  }
}

 const updateWebhookStatus = () => {
   const envNgrokUrl = import.meta.env.VITE_NGROK_URL
   const currentNgrokUrl = services.value.ngrok.tunnels.backend
   const suggestedUrl = currentNgrokUrl ? 
     `${currentNgrokUrl}/api/v1/retellai/agent-level-webhook` : null

   webhookStatus.value.current = envNgrokUrl ? `${envNgrokUrl}/api/v1/retellai/agent-level-webhook` : 'Not configured in .env'
   webhookStatus.value.suggested = suggestedUrl

   if (envNgrokUrl && currentNgrokUrl && envNgrokUrl === currentNgrokUrl) {
     webhookStatus.value.status = 'configured'
   } else if (!envNgrokUrl) {
     webhookStatus.value.status = 'not_configured'
   } else {
     webhookStatus.value.status = 'needs_update' 
   }
 }

const startService = async (serviceName) => {
  services.value[serviceName].status = 'starting'
  
  try {
    if (serviceName === 'backend') {
      // Instructions for starting backend
      toast.info('Starting backend server...', {
        timeout: 5000
      })
      toast.info('Run: cd backend && python run.py', {
        timeout: 10000
      })
      
      // Check if it started after a delay
      setTimeout(async () => {
        await refreshServices()
        if (services.value.backend.status === 'running') {
          toast.success('Backend server started successfully!')
        }
      }, 3000)
      
         } else if (serviceName === 'ngrok') {
       const envNgrokUrl = import.meta.env.VITE_NGROK_URL
       
       if (envNgrokUrl) {
         const subdomain = envNgrokUrl.replace('https://', '').split('.')[0]
         toast.info('Starting ngrok tunnel...', {
           timeout: 5000
         })
         toast.info(`Run: ngrok http --url=${subdomain}.ngrok.io 8000`, {
           timeout: 10000
         })
       } else {
         toast.warning('Ngrok URL not configured in .env file', {
           timeout: 8000
         })
         toast.info('Add VITE_NGROK_URL=https://your-subdomain.ngrok.io to frontend/.env', {
           timeout: 10000
         })
       }
       
       // Check if it started after a delay
       setTimeout(async () => {
         await refreshServices()
         if (services.value.ngrok.status === 'running') {
           toast.success('Ngrok tunnel started successfully!')
         }
       }, 5000)
     }
    
  } catch (error) {
    services.value[serviceName].status = 'stopped'
    toast.error(`Failed to start ${serviceName}: ${error.message}`)
  }
}

const stopService = async (serviceName) => {
  try {
    toast.info(`Stopping ${serviceName}...`)
    services.value[serviceName].status = 'stopped'
    
         if (serviceName === 'backend') {
       services.value.backend.url = null
     } else if (serviceName === 'ngrok') {
       services.value.ngrok.tunnels.backend = null
     }
    
    toast.success(`${serviceName} stopped`)
    
  } catch (error) {
    toast.error(`Failed to stop ${serviceName}: ${error.message}`)
  }
}

 const startAllServices = async () => {
   toast.info('Starting remaining development services...')
   toast.info('Please run the following commands in separate terminals:', { timeout: 15000 })
   toast.info('1. cd backend && python run.py', { timeout: 15000 })
   toast.info('2. ngrok http --url=classic-husky-steady.ngrok-free.app 8000', { timeout: 15000 })
   toast.success('Frontend is already running! ✅', { timeout: 10000 })
 }

const updateWebhookUrl = async () => {
  if (!services.value.ngrok.tunnels.backend) {
    toast.error('Backend ngrok tunnel not available')
    return
  }
  
  const webhookUrl = `${services.value.ngrok.tunnels.backend}/api/v1/retellai/agent-level-webhook`
  
  try {
    // First try automatic API update
    toast.info('Updating RetellAI agents automatically...')
    
    const response = await fetch('http://localhost:8000/api/v1/dashboard/update-retellai-webhook', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    if (response.ok) {
      const result = await response.json()
      const updateResult = result.update_result
      
      toast.success(`✅ Updated ${updateResult.updated_count}/${updateResult.total_agents} RetellAI agents automatically!`)
      
      if (updateResult.failed_updates && updateResult.failed_updates.length > 0) {
        toast.warning(`⚠️ ${updateResult.failed_updates.length} agents failed to update`)
      }
      
      // Update status
      webhookStatus.value.status = 'configured'
      
    } else {
      // Fallback to manual copy if API fails
      await navigator.clipboard.writeText(webhookUrl)
      toast.warning('❌ Auto-update failed. Webhook URL copied to clipboard.')
      toast.info('Please manually update your RetellAI agents')
    }
    
  } catch (error) {
    console.error('Auto-update failed:', error)
    try {
      // Fallback to clipboard copy
      await navigator.clipboard.writeText(webhookUrl)
      toast.warning('❌ Auto-update failed. Webhook URL copied to clipboard.')
      toast.info('Please manually update your RetellAI agents')
    } catch (clipboardError) {
      toast.error('Failed to update webhook and copy to clipboard')
    }
  }
}

const openApiDocs = () => {
  if (services.value.backend.url) {
    window.open(`${services.value.backend.url}/docs`, '_blank')
  }
}

const testWebhook = async () => {
  if (!services.value.ngrok.tunnels.backend) {
    toast.error('Backend ngrok tunnel not available')
    return
  }
  
  try {
    const response = await fetch(`${services.value.ngrok.tunnels.backend}/api/v1/retellai/agent-level-webhook`)
    if (response.ok) {
      toast.success('Webhook endpoint is accessible!')
    } else {
      toast.error('Webhook endpoint returned an error')
    }
  } catch (error) {
    toast.error('Failed to test webhook endpoint')
  }
}

const copyWebhookUrl = async () => {
  if (!services.value.ngrok.tunnels.backend) {
    toast.error('Backend ngrok tunnel not available')
    return
  }
  
  const webhookUrl = `${services.value.ngrok.tunnels.backend}/api/v1/retellai/agent-level-webhook`
  
  try {
    await navigator.clipboard.writeText(webhookUrl)
    toast.success('Webhook URL copied to clipboard!')
  } catch (error) {
    toast.error('Failed to copy webhook URL')
  }
}

onMounted(() => {
  refreshServices()
  // Auto-refresh every 10 seconds
  refreshTimer = setInterval(refreshServices, 10000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped>
.service-item {
  transition: all 0.2s ease-in-out;
}

.btn-xs {
  @apply px-2 py-1 text-xs font-medium rounded;
}
</style> 