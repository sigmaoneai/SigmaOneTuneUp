<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div class="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-hidden">
      <!-- Modal Header -->
      <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <div class="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
            <span class="text-primary-600 font-semibold text-lg">
              {{ getInitials(customer.business_name || customer.contact_name) }}
            </span>
          </div>
          <div>
            <h3 class="text-lg font-semibold text-gray-900">{{ customer.business_name }}</h3>
            <p class="text-sm text-gray-500">Customer #{{ customer.id }} • {{ customer.contact_name }}</p>
          </div>
        </div>
        <button
          @click="close"
          class="text-gray-400 hover:text-gray-500 transition-colors"
        >
          <XMarkIcon class="w-6 h-6" />
        </button>
      </div>

      <!-- Mock Notice -->
      <div class="px-6 py-3 bg-blue-50 border-b border-blue-200">
        <div class="flex items-center">
          <InformationCircleIcon class="w-5 h-5 text-blue-600 mr-2" />
          <p class="text-sm text-blue-800">
            Mock Data: Customer information is simulated for testing purposes.
          </p>
        </div>
      </div>

      <!-- Modal Body -->
      <div class="overflow-y-auto max-h-[60vh]">
        <div class="p-6 space-y-6">
          <!-- Contact Information -->
          <div class="card">
            <div class="card-header">
              <h4 class="text-md font-medium text-gray-900">Contact Information</h4>
            </div>
            <div class="card-body">
              <div class="grid grid-cols-2 gap-6">
                <div class="space-y-4">
                  <div>
                    <label class="text-sm font-medium text-gray-500">Primary Contact</label>
                    <p class="text-sm text-gray-900 mt-1">{{ customer.contact_name }}</p>
                  </div>
                  
                  <div>
                    <label class="text-sm font-medium text-gray-500">Email Address</label>
                    <div class="flex items-center mt-1">
                      <EnvelopeIcon class="w-4 h-4 text-gray-400 mr-2" />
                      <a 
                        :href="`mailto:${customer.email}`"
                        class="text-sm text-primary-600 hover:text-primary-700"
                      >
                        {{ customer.email }}
                      </a>
                    </div>
                  </div>
                  
                  <div>
                    <label class="text-sm font-medium text-gray-500">Phone Number</label>
                    <div class="flex items-center mt-1">
                      <PhoneIcon class="w-4 h-4 text-gray-400 mr-2" />
                      <a 
                        :href="`tel:${customer.phone}`"
                        class="text-sm text-primary-600 hover:text-primary-700"
                      >
                        {{ customer.phone }}
                      </a>
                    </div>
                  </div>
                </div>

                <div class="space-y-4">
                  <div v-if="customer.address">
                    <label class="text-sm font-medium text-gray-500">Address</label>
                    <div class="flex items-start mt-1">
                      <MapPinIcon class="w-4 h-4 text-gray-400 mr-2 mt-0.5" />
                      <p class="text-sm text-gray-900">{{ customer.address }}</p>
                    </div>
                  </div>

                  <div v-if="customer.billing_contact">
                    <label class="text-sm font-medium text-gray-500">Billing Contact</label>
                    <p class="text-sm text-gray-900 mt-1">{{ customer.billing_contact }}</p>
                  </div>

                  <div>
                    <label class="text-sm font-medium text-gray-500">Account Status</label>
                    <div class="mt-1">
                      <span :class="getAccountStatusBadge(customer.account_status)" class="badge">
                        {{ customer.account_status || 'Active' }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Account Summary -->
          <div class="card">
            <div class="card-header">
              <h4 class="text-md font-medium text-gray-900">Account Summary</h4>
            </div>
            <div class="card-body">
              <div class="grid grid-cols-4 gap-6 text-center">
                <div>
                  <div class="text-2xl font-bold text-gray-900">{{ customer.tickets_count || 0 }}</div>
                  <div class="text-sm text-gray-500">Total Tickets</div>
                </div>
                <div>
                  <div class="text-2xl font-bold text-warning-600">{{ customer.open_tickets || 0 }}</div>
                  <div class="text-sm text-gray-500">Open Tickets</div>
                </div>
                <div>
                  <div class="text-2xl font-bold text-success-600">
                    {{ (customer.tickets_count || 0) - (customer.open_tickets || 0) }}
                  </div>
                  <div class="text-sm text-gray-500">Resolved</div>
                </div>
                <div>
                  <div class="text-2xl font-bold text-primary-600">
                    {{ formatDuration(customer.created_at) }}
                  </div>
                  <div class="text-sm text-gray-500">Customer Since</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Account Details -->
          <div class="grid grid-cols-2 gap-6">
            <div class="card">
              <div class="card-header">
                <h4 class="text-md font-medium text-gray-900">Account Details</h4>
              </div>
              <div class="card-body space-y-3">
                <div class="flex justify-between">
                  <span class="text-sm text-gray-500">Customer ID</span>
                  <span class="text-sm text-gray-900">#{{ customer.id }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-sm text-gray-500">Created Date</span>
                  <span class="text-sm text-gray-900">{{ formatDate(customer.created_at) }}</span>
                </div>
                <div v-if="customer.last_activity" class="flex justify-between">
                  <span class="text-sm text-gray-500">Last Activity</span>
                  <span class="text-sm text-gray-900">{{ formatTime(customer.last_activity) }}</span>
                </div>
                <div v-if="customer.notes" class="pt-2 border-t">
                  <span class="text-sm text-gray-500">Notes</span>
                  <p class="text-sm text-gray-900 mt-1">{{ customer.notes }}</p>
                </div>
              </div>
            </div>

            <div class="card">
              <div class="card-header">
                <h4 class="text-md font-medium text-gray-900">Quick Actions</h4>
              </div>
              <div class="card-body space-y-3">
                <button
                  @click="createTicket"
                  class="w-full btn-primary btn-sm text-left"
                >
                  <PlusIcon class="w-4 h-4 mr-2" />
                  Create New Ticket
                </button>
                
                <button
                  @click="sendEmail"
                  class="w-full btn-secondary btn-sm text-left"
                >
                  <EnvelopeIcon class="w-4 h-4 mr-2" />
                  Send Email
                </button>
                
                <button
                  @click="callCustomer"
                  class="w-full btn-secondary btn-sm text-left"
                >
                  <PhoneIcon class="w-4 h-4 mr-2" />
                  Call Customer
                </button>

                <button
                  @click="viewLocation"
                  class="w-full btn-secondary btn-sm text-left"
                  :disabled="!customer.address"
                >
                  <MapPinIcon class="w-4 h-4 mr-2" />
                  View Location
                </button>
              </div>
            </div>
          </div>

          <!-- Recent Tickets Preview -->
          <div v-if="recentTickets.length > 0" class="card">
            <div class="card-header">
              <div class="flex items-center justify-between">
                <h4 class="text-md font-medium text-gray-900">Recent Tickets</h4>
                <button
                  @click="viewAllTickets"
                  class="text-sm text-primary-600 hover:text-primary-700"
                >
                  View All
                </button>
              </div>
            </div>
            <div class="card-body p-0">
              <div class="divide-y divide-gray-200">
                <div 
                  v-for="ticket in recentTickets.slice(0, 3)" 
                  :key="ticket.id"
                  class="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                  @click="viewTicket(ticket)"
                >
                  <div class="flex items-center justify-between">
                    <div>
                      <h5 class="text-sm font-medium text-gray-900">
                        #{{ ticket.id }} - {{ ticket.subject }}
                      </h5>
                      <p class="text-xs text-gray-500 mt-1">
                        {{ ticket.problem_type }} • {{ formatTime(ticket.created_at) }}
                      </p>
                    </div>
                    <div class="flex items-center space-x-2">
                      <span :class="getTicketStatusBadge(ticket.status)" class="badge text-xs">
                        {{ getTicketStatusText(ticket.status) }}
                      </span>
                      <ChevronRightIcon class="w-4 h-4 text-gray-400" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div v-if="customer.mock_data" class="flex items-center text-xs text-blue-600">
            <InformationCircleIcon class="w-3 h-3 mr-1" />
            Mock Data
          </div>
        </div>
        <div class="flex items-center space-x-3">
          <button
            @click="close"
            class="btn-secondary"
          >
            Close
          </button>
          <button
            @click="createTicket"
            class="btn-primary"
          >
            <PlusIcon class="w-4 h-4 mr-2" />
            Create Ticket
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { formatDistanceToNow, format } from 'date-fns'
import api from '@/services/api'
import {
  XMarkIcon,
  InformationCircleIcon,
  EnvelopeIcon,
  PhoneIcon,
  MapPinIcon,
  PlusIcon,
  ChevronRightIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  customer: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'create-ticket'])
const toast = useToast()

// Reactive state
const recentTickets = ref([])
const loading = ref(false)

// Methods
const close = () => {
  emit('close')
}

const createTicket = () => {
  emit('create-ticket', props.customer)
}

const sendEmail = () => {
  window.location.href = `mailto:${props.customer.email}`
}

const callCustomer = () => {
  window.location.href = `tel:${props.customer.phone}`
}

const viewLocation = () => {
  if (props.customer.address) {
    const encodedAddress = encodeURIComponent(props.customer.address)
    window.open(`https://maps.google.com/maps?q=${encodedAddress}`, '_blank')
  }
}

const viewAllTickets = () => {
  // In a real app, this would navigate to tickets filtered by customer
  toast.info(`Would show all tickets for ${props.customer.business_name}`)
}

const viewTicket = (ticket) => {
  // In a real app, this would open the ticket detail modal
  toast.info(`Would open ticket #${ticket.id}`)
}

const loadRecentTickets = async () => {
  loading.value = true
  try {
    // Mock recent tickets for this customer
    const allTicketsResponse = await api.syncro.listTickets({ limit: 100 })
    const allTickets = allTicketsResponse.data.tickets || []
    
    // Filter tickets for this customer
    recentTickets.value = allTickets
      .filter(ticket => ticket.customer_id === props.customer.id)
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      .slice(0, 5)
  } catch (error) {
    console.warn('Failed to load recent tickets:', error)
  } finally {
    loading.value = false
  }
}

// Utility methods
const getInitials = (name) => {
  if (!name) return '?'
  return name
    .split(' ')
    .map(word => word.charAt(0))
    .join('')
    .substring(0, 2)
    .toUpperCase()
}

const formatTime = (timestamp) => {
  return formatDistanceToNow(new Date(timestamp), { addSuffix: true })
}

const formatDate = (timestamp) => {
  return format(new Date(timestamp), 'MMM d, yyyy')
}

const formatDuration = (timestamp) => {
  const years = Math.floor(formatDistanceToNow(new Date(timestamp)).match(/\d+/)?.[0] || 0)
  return years > 0 ? `${years}y` : 'New'
}

const getAccountStatusBadge = (status) => {
  switch (status?.toLowerCase()) {
    case 'active': return 'badge-success'
    case 'inactive': return 'badge-gray'
    case 'suspended': return 'badge-warning'
    case 'terminated': return 'badge-danger'
    default: return 'badge-success'
  }
}

const getTicketStatusBadge = (status) => {
  switch (status) {
    case 'open': return 'badge-warning'
    case 'in_progress': return 'badge-primary'
    case 'completed': return 'badge-success'
    case 'urgent': return 'badge-danger'
    default: return 'badge-gray'
  }
}

const getTicketStatusText = (status) => {
  switch (status) {
    case 'open': return 'Open'
    case 'in_progress': return 'In Progress'
    case 'completed': return 'Completed'
    case 'urgent': return 'Urgent'
    default: return status
  }
}

// Initialize
onMounted(() => {
  loadRecentTickets()
})
</script> 