<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Page Header -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Voice Agents</h1>
          <p class="mt-2 text-gray-600">Manage your RetellAI voice agents and their configurations</p>
        </div>
        <router-link to="/agents/create" class="btn-primary">
          <PlusIcon class="w-4 h-4 mr-2" />
          Create Agent
        </router-link>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <div class="card">
        <div class="card-body text-center">
          <MicrophoneIcon class="w-8 h-8 text-primary-600 mx-auto mb-2" />
          <div class="text-2xl font-bold text-gray-900">{{ stats.totalAgents }}</div>
          <div class="text-sm text-gray-500">Total Agents</div>
        </div>
      </div>
      <div class="card">
        <div class="card-body text-center">
          <CheckCircleIcon class="w-8 h-8 text-success-600 mx-auto mb-2" />
          <div class="text-2xl font-bold text-gray-900">{{ stats.activeAgents }}</div>
          <div class="text-sm text-gray-500">Active Agents</div>
        </div>
      </div>
      <div class="card">
        <div class="card-body text-center">
          <PhoneIcon class="w-8 h-8 text-blue-600 mx-auto mb-2" />
          <div class="text-2xl font-bold text-gray-900">{{ stats.callsToday }}</div>
          <div class="text-sm text-gray-500">Calls Today</div>
        </div>
      </div>
      <div class="card">
        <div class="card-body text-center">
          <StarIcon class="w-8 h-8 text-warning-600 mx-auto mb-2" />
          <div class="text-2xl font-bold text-gray-900">{{ stats.avgRating }}</div>
          <div class="text-sm text-gray-500">Avg Rating</div>
        </div>
      </div>
    </div>

    <!-- Search and Filters -->
    <div class="card mb-6">
      <div class="card-body">
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          <div class="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-4">
            <div class="relative">
              <MagnifyingGlassIcon class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search agents..."
                class="form-input pl-10"
              />
            </div>
            
            <select v-model="statusFilter" class="form-select">
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="training">Training</option>
            </select>

            <select v-model="languageFilter" class="form-select">
              <option value="">All Languages</option>
              <option value="en-US">English (US)</option>
              <option value="en-GB">English (UK)</option>
              <option value="es-ES">Spanish</option>
              <option value="fr-FR">French</option>
            </select>
          </div>

          <button
            @click="refreshAgents"
            :disabled="loading"
            class="btn-primary btn-sm"
          >
            <ArrowPathIcon 
              :class="['w-4 h-4 mr-2', loading ? 'animate-spin' : '']" 
            />
            Refresh
          </button>
        </div>
      </div>
    </div>

    <!-- Agents Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="agent in filteredAgents"
        :key="agent.id"
        class="card hover:shadow-lg transition-shadow cursor-pointer"
        @click="viewAgent(agent)"
      >
        <div class="card-body">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center">
              <div class="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                <MicrophoneIcon class="w-6 h-6 text-primary-600" />
              </div>
              <div class="ml-3">
                <h3 class="text-lg font-medium text-gray-900">{{ agent.name }}</h3>
                <p class="text-sm text-gray-500">{{ agent.language }} • {{ agent.voice }}</p>
              </div>
            </div>
            <span :class="getStatusBadge(agent.status)" class="badge">
              {{ agent.status }}
            </span>
          </div>

          <p class="text-sm text-gray-600 mb-4 line-clamp-2">
            {{ agent.description || 'No description provided' }}
          </p>

          <div class="space-y-3">
            <div class="flex justify-between text-sm">
              <span class="text-gray-500">Phone Numbers:</span>
              <span class="text-gray-900">{{ agent.phone_numbers?.length || 0 }}</span>
            </div>
            
            <div class="flex justify-between text-sm">
              <span class="text-gray-500">Calls Today:</span>
              <span class="text-gray-900">{{ agent.calls_today || 0 }}</span>
            </div>

            <div class="flex justify-between text-sm">
              <span class="text-gray-500">Total Calls:</span>
              <span class="text-gray-900">{{ agent.total_calls || 0 }}</span>
            </div>

            <div class="flex justify-between text-sm">
              <span class="text-gray-500">Success Rate:</span>
              <span class="text-gray-900">{{ agent.success_rate || 0 }}%</span>
            </div>

            <div v-if="agent.rating" class="flex justify-between text-sm">
              <span class="text-gray-500">Rating:</span>
              <div class="flex items-center">
                <div class="flex items-center">
                  <StarIcon 
                    v-for="i in 5" 
                    :key="i"
                    :class="i <= agent.rating ? 'text-yellow-400' : 'text-gray-300'"
                    class="w-3 h-3"
                  />
                </div>
                <span class="text-gray-900 ml-1 text-xs">{{ agent.rating }}</span>
              </div>
            </div>
          </div>

          <div class="mt-4 pt-4 border-t flex items-center justify-between">
            <div class="text-xs text-gray-500">
              Created {{ formatTime(agent.created_at) }}
            </div>
            <div class="flex items-center space-x-2">
              <button
                @click.stop="testAgent(agent)"
                :disabled="agent.status !== 'active'"
                class="text-blue-600 hover:text-blue-800 text-sm disabled:text-gray-400"
              >
                Test
              </button>
              <button
                @click.stop="configureAgent(agent)"
                class="text-primary-600 hover:text-primary-800 text-sm"
              >
                Configure
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="!loading && filteredAgents.length === 0" class="col-span-full">
        <div class="text-center py-12">
          <MicrophoneIcon class="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p class="text-gray-500">No agents found</p>
          <p class="text-sm text-gray-400 mt-2">
            {{ searchQuery || statusFilter || languageFilter ? 'Try adjusting your filters' : 'Create your first voice agent to get started' }}
          </p>
          <router-link v-if="!searchQuery && !statusFilter && !languageFilter" to="/agents/create" class="btn-primary mt-4">
            <PlusIcon class="w-4 h-4 mr-2" />
            Create Agent
          </router-link>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="i in 6" :key="i" class="card">
        <div class="card-body animate-pulse">
          <div class="flex items-center mb-4">
            <div class="w-12 h-12 bg-gray-200 rounded-full"></div>
            <div class="ml-3 flex-1">
              <div class="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div class="h-3 bg-gray-200 rounded w-1/2"></div>
            </div>
          </div>
          <div class="space-y-2">
            <div class="h-3 bg-gray-200 rounded"></div>
            <div class="h-3 bg-gray-200 rounded w-2/3"></div>
            <div class="h-3 bg-gray-200 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="filteredAgents.length > pageSize" class="mt-8 flex items-center justify-center">
      <div class="flex items-center space-x-2">
        <button
          @click="currentPage = Math.max(1, currentPage - 1)"
          :disabled="currentPage <= 1"
          class="btn-secondary btn-sm"
        >
          Previous
        </button>
        <span class="text-sm text-gray-700">
          Page {{ currentPage }} of {{ totalPages }}
        </span>
        <button
          @click="currentPage = Math.min(totalPages, currentPage + 1)"
          :disabled="currentPage >= totalPages"
          class="btn-secondary btn-sm"
        >
          Next
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { formatDistanceToNow } from 'date-fns'
import api from '@/services/api'
import {
  MicrophoneIcon,
  PlusIcon,
  CheckCircleIcon,
  PhoneIcon,
  StarIcon,
  MagnifyingGlassIcon,
  ArrowPathIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const toast = useToast()

// Reactive state
const loading = ref(false)
const agents = ref([])
const searchQuery = ref('')
const statusFilter = ref('')
const languageFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(9)

const stats = ref({
  totalAgents: 4,
  activeAgents: 3,
  callsToday: 87,
  avgRating: 4.5
})

// Computed properties
const filteredAgents = computed(() => {
  let filtered = agents.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(agent => 
      agent.name.toLowerCase().includes(query) ||
      agent.description?.toLowerCase().includes(query)
    )
  }

  if (statusFilter.value) {
    filtered = filtered.filter(agent => agent.status === statusFilter.value)
  }

  if (languageFilter.value) {
    filtered = filtered.filter(agent => agent.language === languageFilter.value)
  }

  return filtered
})

const totalPages = computed(() => Math.ceil(filteredAgents.value.length / pageSize.value))

// Methods
const loadAgents = async () => {
  loading.value = true
  try {
    const response = await api.retell.listAgents()
    agents.value = response.data.agents || []
  } catch (error) {
    toast.error('Failed to load agents')
  } finally {
    loading.value = false
  }
}

const refreshAgents = () => {
  loadAgents()
}

const viewAgent = (agent) => {
  router.push(`/agents/${agent.id}`)
}

const testAgent = (agent) => {
  if (agent.status === 'active') {
    toast.success(`Test call initiated for ${agent.name}`)
  }
}

const configureAgent = (agent) => {
  // In a real app, this would open configuration modal or navigate to settings
  toast.info(`Configuration for ${agent.name} would open here`)
}

const formatTime = (timestamp) => {
  return formatDistanceToNow(new Date(timestamp), { addSuffix: true })
}

const getStatusBadge = (status) => {
  switch (status) {
    case 'active': return 'badge-success'
    case 'inactive': return 'badge-gray'
    case 'training': return 'badge-warning'
    default: return 'badge-gray'
  }
}

// Initialize
onMounted(() => {
  loadAgents()
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style> 