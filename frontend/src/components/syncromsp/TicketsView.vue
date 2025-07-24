<template>
  <div class="space-y-6">
    <!-- Search and Filters -->
    <div class="flex flex-col sm:flex-row gap-4">
      <div class="flex-1">
        <div class="relative">
          <MagnifyingGlassIcon class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search tickets by subject, customer, or ID..."
            class="form-input pl-10"
            @input="debouncedSearch"
          />
        </div>
      </div>
      <div class="flex space-x-3">
        <select v-model="statusFilter" @change="filterTickets" class="form-select">
          <option value="">All Status</option>
          <option value="open">Open</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
          <option value="urgent">Urgent</option>
        </select>
        <select v-model="priorityFilter" @change="filterTickets" class="form-select">
          <option value="">All Priority</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        <button
          @click="showCreateModal = true"
          class="btn-primary whitespace-nowrap"
        >
          <PlusIcon class="w-4 h-4 mr-2" />
          Create Ticket
        </button>
      </div>
    </div>

    <!-- Tickets List -->
    <div class="card">
      <div class="card-header">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-lg font-medium text-gray-900">Support Tickets</h3>
            <p class="text-sm text-gray-500">
              {{ filteredTickets.length }} of {{ allTickets.length }} tickets
            </p>
          </div>
          <button
            @click="refreshTickets"
            :disabled="refreshing"
            class="btn-secondary btn-sm"
          >
            <ArrowPathIcon 
              :class="['w-4 h-4 mr-2', refreshing ? 'animate-spin' : '']" 
            />
            Refresh
          </button>
        </div>
      </div>

      <div class="card-body p-0">
        <template v-if="loading">
          <div class="divide-y divide-gray-200">
            <div v-for="i in 5" :key="i" class="p-4 animate-pulse">
              <div class="flex items-center space-x-4">
                <div class="w-12 h-12 bg-gray-200 rounded-lg"></div>
                <div class="flex-1">
                  <div class="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div class="h-3 bg-gray-100 rounded w-1/2"></div>
                </div>
                <div class="w-20 h-6 bg-gray-200 rounded"></div>
              </div>
            </div>
          </div>
        </template>

        <template v-else-if="filteredTickets.length === 0">
          <div class="text-center py-12">
            <TicketIcon class="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 class="text-lg font-medium text-gray-900 mb-2">No tickets found</h3>
            <p class="text-gray-600 mb-6">
              {{ allTickets.length === 0 
                ? "No tickets available. Create your first support ticket." 
                : "Try adjusting your search or filters" }}
            </p>
            <button
              @click="showCreateModal = true"
              class="btn-primary"
            >
              Create New Ticket
            </button>
          </div>
        </template>

        <template v-else>
          <div class="divide-y divide-gray-200">
            <div
              v-for="ticket in paginatedTickets"
              :key="ticket.id"
              class="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
              @click="viewTicket(ticket)"
            >
              <div class="flex items-center space-x-4">
                <!-- Priority & Status Indicator -->
                <div class="flex-shrink-0">
                  <div 
                    :class="getPriorityClasses(ticket.priority, ticket.status)"
                    class="w-12 h-12 rounded-lg flex items-center justify-center"
                  >
                    <component 
                      :is="getPriorityIcon(ticket.priority, ticket.status)" 
                      class="w-6 h-6 text-white" 
                    />
                  </div>
                </div>

                <!-- Ticket Info -->
                <div class="flex-1 min-w-0">
                  <div class="flex items-center justify-between">
                    <h4 class="text-sm font-medium text-gray-900 truncate">
                      #{{ ticket.id }} - {{ ticket.subject }}
                    </h4>
                    <div class="flex items-center space-x-2">
                      <span :class="getStatusBadge(ticket.status)" class="badge text-xs">
                        {{ getStatusText(ticket.status) }}
                      </span>
                      <span :class="getPriorityBadge(ticket.priority)" class="badge text-xs">
                        {{ ticket.priority }}
                      </span>
                    </div>
                  </div>
                  
                  <div class="mt-1 flex items-center text-xs text-gray-500">
                    <span class="truncate">{{ ticket.customer_business_then_name }}</span>
                    <span class="mx-2">•</span>
                    <span>{{ ticket.problem_type }}</span>
                    <span class="mx-2">•</span>
                    <span>{{ formatTime(ticket.created_at) }}</span>
                  </div>

                  <div v-if="ticket.description" class="mt-2">
                    <p class="text-sm text-gray-600 line-clamp-2">
                      {{ ticket.description }}
                    </p>
                  </div>

                  <!-- Comments Count -->
                  <div v-if="ticket.comments && ticket.comments.length > 0" class="mt-2 flex items-center text-xs text-gray-500">
                    <ChatBubbleLeftIcon class="w-3 h-3 mr-1" />
                    {{ ticket.comments.length }} comment{{ ticket.comments.length !== 1 ? 's' : '' }}
                  </div>
                </div>

                <!-- Actions -->
                <div class="flex-shrink-0">
                  <ChevronRightIcon class="w-5 h-5 text-gray-400" />
                </div>
              </div>
            </div>
          </div>

          <!-- Pagination -->
          <div v-if="totalPages > 1" class="px-4 py-3 border-t border-gray-200 bg-gray-50">
            <div class="flex items-center justify-between">
              <div class="text-sm text-gray-500">
                Showing {{ (currentPage - 1) * pageSize + 1 }} to {{ Math.min(currentPage * pageSize, filteredTickets.length) }} 
                of {{ filteredTickets.length }} tickets
              </div>
              <div class="flex space-x-2">
                <button
                  @click="currentPage = Math.max(1, currentPage - 1)"
                  :disabled="currentPage === 1"
                  class="btn-secondary btn-sm"
                >
                  Previous
                </button>
                <button
                  @click="currentPage = Math.min(totalPages, currentPage + 1)"
                  :disabled="currentPage === totalPages"
                  class="btn-secondary btn-sm"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- Create Ticket Modal -->
    <CreateTicketModal
      v-if="showCreateModal"
      @close="showCreateModal = false"
      @ticket-created="handleTicketCreated"
    />

    <!-- Ticket Detail Modal -->
    <TicketDetailModal
      v-if="showDetailModal && selectedTicket"
      :ticket="selectedTicket"
      @close="showDetailModal = false"
      @ticket-updated="handleTicketUpdated"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { formatDistanceToNow } from 'date-fns'
import api from '@/services/api'
import {
  MagnifyingGlassIcon,
  PlusIcon,
  ArrowPathIcon,
  TicketIcon,
  ExclamationTriangleIcon,
  ExclamationCircleIcon,
  CheckCircleIcon,
  ClockIcon,
  ChevronRightIcon,
  ChatBubbleLeftIcon
} from '@heroicons/vue/24/outline'

// Components
import CreateTicketModal from './CreateTicketModal.vue'
import TicketDetailModal from './TicketDetailModal.vue'

const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['refresh', 'ticket-updated'])

const toast = useToast()

// Reactive state
const refreshing = ref(false)
const allTickets = ref([])
const searchQuery = ref('')
const statusFilter = ref('')
const priorityFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// Modal state
const showCreateModal = ref(false)
const showDetailModal = ref(false)
const selectedTicket = ref(null)

// Computed properties
const filteredTickets = computed(() => {
  let filtered = allTickets.value

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(ticket => 
      ticket.subject.toLowerCase().includes(query) ||
      ticket.customer_business_then_name.toLowerCase().includes(query) ||
      ticket.id.toString().includes(query) ||
      (ticket.description && ticket.description.toLowerCase().includes(query))
    )
  }

  // Status filter
  if (statusFilter.value) {
    filtered = filtered.filter(ticket => ticket.status === statusFilter.value)
  }

  // Priority filter
  if (priorityFilter.value) {
    filtered = filtered.filter(ticket => ticket.priority === priorityFilter.value)
  }

  return filtered
})

const paginatedTickets = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredTickets.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredTickets.value.length / pageSize.value)
})

// Methods
const loadTickets = async () => {
  try {
    const response = await api.syncro.listTickets({
      status: statusFilter.value,
      priority: priorityFilter.value,
      limit: 100
    })
    allTickets.value = response.data.tickets || []
  } catch (error) {
    toast.error('Failed to load tickets')
  }
}

const refreshTickets = async () => {
  refreshing.value = true
  try {
    await loadTickets()
    emit('refresh')
    toast.success('Tickets refreshed')
  } catch (error) {
    toast.error('Failed to refresh tickets')
  } finally {
    refreshing.value = false
  }
}

const filterTickets = () => {
  currentPage.value = 1 // Reset to first page when filtering
  loadTickets()
}

const debouncedSearch = (() => {
  let timeout = null
  return () => {
    clearTimeout(timeout)
    timeout = setTimeout(() => {
      currentPage.value = 1
    }, 300)
  }
})()

const viewTicket = (ticket) => {
  selectedTicket.value = ticket
  showDetailModal.value = true
}

const handleTicketCreated = (ticket) => {
  allTickets.value.unshift(ticket)
  showCreateModal.value = false
  toast.success(`Ticket #${ticket.id} created successfully`)
}

const handleTicketUpdated = (ticketId) => {
  // Refresh the ticket list
  loadTickets()
  emit('ticket-updated', ticketId)
}

// Utility methods
const formatTime = (timestamp) => {
  return formatDistanceToNow(new Date(timestamp), { addSuffix: true })
}

const getPriorityClasses = (priority, status) => {
  if (status === 'urgent') return 'bg-red-500'
  
  switch (priority) {
    case 'critical': return 'bg-red-500'
    case 'high': return 'bg-orange-500'
    case 'medium': return 'bg-yellow-500'
    case 'low': return 'bg-green-500'
    default: return 'bg-gray-500'
  }
}

const getPriorityIcon = (priority, status) => {
  if (status === 'urgent') return ExclamationTriangleIcon
  if (status === 'completed') return CheckCircleIcon
  
  switch (priority) {
    case 'critical':
    case 'high':
      return ExclamationCircleIcon
    case 'medium':
      return ClockIcon
    case 'low':
      return CheckCircleIcon
    default:
      return TicketIcon
  }
}

const getStatusBadge = (status) => {
  switch (status) {
    case 'open': return 'badge-warning'
    case 'in_progress': return 'badge-primary'
    case 'completed': return 'badge-success'
    case 'urgent': return 'badge-danger'
    default: return 'badge-gray'
  }
}

const getStatusText = (status) => {
  switch (status) {
    case 'open': return 'Open'
    case 'in_progress': return 'In Progress'
    case 'completed': return 'Completed'
    case 'urgent': return 'Urgent'
    default: return status
  }
}

const getPriorityBadge = (priority) => {
  switch (priority) {
    case 'critical': return 'badge-danger'
    case 'high': return 'badge-warning'
    case 'medium': return 'badge-primary'
    case 'low': return 'badge-success'
    default: return 'badge-gray'
  }
}

// Initialize
onMounted(() => {
  loadTickets()
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