<template>
  <div class="p-6">
    <div class="max-w-7xl mx-auto">
      <div class="bg-white rounded-lg shadow-sm">
        <!-- Header -->
        <div class="flex justify-between items-center mb-6">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Call Management</h1>
            <p class="text-gray-600">Monitor and manage voice AI calls</p>
          </div>
          <div class="flex space-x-3">
            <button
              @click="showAgentToAgentModal = true"
              class="btn btn-secondary"
            >
              <UserGroupIcon class="w-4 h-4 mr-2" />
              Agent-to-Agent Call
            </button>
            <button @click="syncCallsFromRetell" class="btn btn-secondary mr-3">
              <ArrowPathIcon class="w-4 h-4 mr-2" />
              Sync from Retell
            </button>
            <button @click="refreshCalls" class="btn btn-primary">
              <ArrowPathIcon class="w-4 h-4 mr-2" />
              Refresh
            </button>
          </div>
        </div>

        <!-- Filters and Search -->
        <div class="mb-6 grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search calls..."
              class="input"
            />
          </div>
          <div>
            <select v-model="statusFilter" class="input">
              <option value="">All Statuses</option>
              <option value="registered">Registered</option>
              <option value="ongoing">Ongoing</option>
              <option value="ended">Ended</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
            </select>
          </div>
          <div>
            <select v-model="directionFilter" class="input">
              <option value="">All Directions</option>
              <option value="inbound">Inbound</option>
              <option value="outbound">Outbound</option>
              <option value="agent_to_agent">Agent-to-Agent</option>
            </select>
          </div>
          <div>
            <select v-model="pageSize" class="input">
              <option :value="10">10 per page</option>
              <option :value="25">25 per page</option>
              <option :value="50">50 per page</option>
            </select>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="text-center py-12">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p class="text-gray-500 mt-4">Loading calls...</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="calls.length === 0" class="text-center py-12">
          <PhoneIcon class="mx-auto h-12 w-12 text-gray-400" />
          <h3 class="mt-2 text-sm font-medium text-gray-900">No calls found</h3>
          <p class="mt-1 text-sm text-gray-500">Get started by making your first call.</p>
        </div>

        <!-- Calls Table -->
        <div v-else class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
          <table class="min-w-full divide-y divide-gray-300">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Call Details
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Direction
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Duration
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="call in paginatedCalls" :key="call.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="flex-shrink-0 w-10 h-10">
                      <div class="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                        <PhoneIcon class="w-5 h-5 text-primary-600" />
                      </div>
                    </div>
                    <div class="ml-4">
                      <div class="text-sm font-medium text-gray-900">{{ call.from_number }} → {{ call.to_number }}</div>
                      <div class="text-sm text-gray-500">
                        <span v-if="call.direction === 'agent_to_agent'">
                          {{ call.caller_agent_name }} → {{ call.inbound_agent_name }}
                        </span>
                        <span v-else">{{ call.direction }} call</span>
                      </div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <component 
                      :is="getDirectionIcon(call.direction)"
                      :class="getDirectionColor(call.direction)"
                      class="w-4 h-4 mr-2"
                    />
                    <span class="text-sm text-gray-900 capitalize">{{ formatDirection(call.direction) }}</span>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ formatDuration(call.duration || (call.duration_ms ? Math.floor(call.duration_ms / 1000) : 0)) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="getStatusBadge(call.status || 'completed')" class="badge">
                    {{ call.status || 'completed' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatTime(call.created_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                  <button
                    @click="viewCall(call)"
                    class="text-primary-600 hover:text-primary-900"
                  >
                    View
                  </button>
                  <button
                    v-if="call.recording_url"
                    @click="playRecording(call)"
                    class="text-green-600 hover:text-green-900"
                  >
                    Play
                  </button>
                  <span v-else class="text-gray-400">No recording</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="mt-6 flex items-center justify-between">
          <div class="text-sm text-gray-700">
            Showing {{ (currentPage - 1) * pageSize + 1 }} to {{ Math.min(currentPage * pageSize, filteredCalls.length) }} of {{ filteredCalls.length }} results
          </div>
          <div class="flex space-x-2">
            <button
              v-for="page in totalPages"
              :key="page"
              @click="currentPage = page"
              :class="[
                'px-3 py-2 text-sm font-medium rounded-md',
                currentPage === page
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              ]"
            >
              {{ page }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Agent-to-Agent Call Modal -->
    <AgentToAgentCallModal
      :is-open="showAgentToAgentModal"
      @close="showAgentToAgentModal = false"
      @call-initiated="onAgentToAgentCallInitiated"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { formatDistanceToNow } from 'date-fns'
import { useToast } from 'vue-toastification'
import {
  PhoneIcon,
  ArrowPathIcon,
  ArrowDownLeftIcon,
  ArrowUpRightIcon,
  UserGroupIcon
} from '@heroicons/vue/24/outline'
import api from '@/services/api'
import AgentToAgentCallModal from '@/components/calls/AgentToAgentCallModal.vue'

const router = useRouter()
const toast = useToast()

// Reactive data
const loading = ref(false)
const calls = ref([])
const searchQuery = ref('')
const statusFilter = ref('')
const directionFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(25)
const showAgentToAgentModal = ref(false)

// Computed properties
const filteredCalls = computed(() => {
  let filtered = calls.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(call => 
      call.from_number.includes(query) ||
      call.to_number.includes(query) ||
      call.transcript?.toLowerCase().includes(query)
    )
  }

  if (statusFilter.value) {
    filtered = filtered.filter(call => call.status === statusFilter.value)
  }

  if (directionFilter.value) {
    filtered = filtered.filter(call => call.direction === directionFilter.value)
  }

  return filtered
})

const totalPages = computed(() => Math.ceil(filteredCalls.value.length / pageSize.value))

const paginatedCalls = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredCalls.value.slice(start, end)
})

// Methods
const loadCalls = async () => {
  loading.value = true
  try {
    const response = await api.retell.listCalls()
    calls.value = response.data || []
  } catch (error) {
    toast.error('Failed to load calls')
  } finally {
    loading.value = false
  }
}

const refreshCalls = () => {
  loadCalls()
}

const syncCallsFromRetell = async () => {
  try {
    toast.info('Syncing calls from Retell.ai...')
    await api.calls.syncAllFromRetell()
    toast.success('Calls synced successfully')
    loadCalls() // Refresh the list
  } catch (error) {
    toast.error('Failed to sync calls from Retell.ai')
  }
}

const viewCall = (call) => {
  router.push(`/calls/${call.id}`)
}

const playRecording = (call) => {
  if (call.recording_url) {
    window.open(call.recording_url, '_blank')
  } else {
    toast.info('Recording not available for this call')
  }
}

const onAgentToAgentCallInitiated = (call) => {
  // Add the new call to the list
  calls.value.unshift(call)
}

const formatTime = (timestamp) => {
  return formatDistanceToNow(new Date(timestamp), { addSuffix: true })
}

const formatDuration = (seconds) => {
  if (!seconds) return 'N/A'
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}m ${secs}s`
}

const formatDirection = (direction) => {
  if (direction === 'agent_to_agent') return 'Agent-to-Agent'
  return direction
}

const getDirectionIcon = (direction) => {
  switch (direction) {
    case 'inbound':
      return ArrowDownLeftIcon
    case 'outbound':
      return ArrowUpRightIcon
    case 'agent_to_agent':
      return UserGroupIcon
    default:
      return PhoneIcon
  }
}

const getDirectionColor = (direction) => {
  switch (direction) {
    case 'inbound':
      return 'text-green-600'
    case 'outbound':
      return 'text-blue-600'
    case 'agent_to_agent':
      return 'text-purple-600'
    default:
      return 'text-gray-600'
  }
}

const getStatusBadge = (status) => {
  switch (status) {
    case 'completed':
      return 'bg-green-100 text-green-800'
    case 'ongoing':
      return 'bg-blue-100 text-blue-800'
    case 'registered':
      return 'bg-yellow-100 text-yellow-800'
    case 'ended':
      return 'bg-gray-100 text-gray-800'
    case 'failed':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

// Load calls on component mount
onMounted(() => {
  loadCalls()
})
</script> 