<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Page Header -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">SyncroMSP Integration</h1>
          <p class="mt-2 text-gray-600">Manage tickets and customers from your SyncroMSP platform</p>
        </div>
        <div class="flex items-center space-x-3">
          <div class="flex items-center">
            <div :class="connectionStatus" class="w-3 h-3 rounded-full mr-2"></div>
            <span class="text-sm text-gray-600">{{ connectionText }}</span>
          </div>
          <button
            @click="syncData"
            :disabled="syncing"
            class="btn-secondary"
          >
            <ArrowPathIcon 
              :class="['w-4 h-4 mr-2', syncing ? 'animate-spin' : '']" 
            />
            {{ syncing ? 'Syncing...' : 'Sync Data' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Mock Data Notice -->
    <div class="mb-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
      <div class="flex">
        <ExclamationTriangleIcon class="w-5 h-5 text-yellow-600 mt-0.5 mr-3" />
        <div>
          <h3 class="text-sm font-medium text-yellow-800">Mock Data Mode</h3>
          <p class="text-sm text-yellow-700 mt-1">
            Currently running in dry-run mode with mock data. Real SyncroMSP operations are disabled for testing.
          </p>
        </div>
      </div>
    </div>

    <!-- Stats Overview -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <div class="card">
        <div class="card-body text-center">
          <div class="text-2xl font-bold text-primary-600">{{ stats.total_tickets }}</div>
          <div class="text-sm text-gray-600">Total Tickets</div>
        </div>
      </div>
      <div class="card">
        <div class="card-body text-center">
          <div class="text-2xl font-bold text-warning-600">{{ stats.open_tickets }}</div>
          <div class="text-sm text-gray-600">Open Tickets</div>
        </div>
      </div>
      <div class="card">
        <div class="card-body text-center">
          <div class="text-2xl font-bold text-success-600">{{ stats.customers }}</div>
          <div class="text-sm text-gray-600">Customers</div>
        </div>
      </div>
      <div class="card">
        <div class="card-body text-center">
          <div class="text-2xl font-bold text-danger-600">{{ stats.urgent_tickets }}</div>
          <div class="text-sm text-gray-600">Urgent</div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="mb-6">
      <nav class="flex space-x-8">
        <button
          @click="activeTab = 'tickets'"
          :class="[
            'py-2 px-1 border-b-2 font-medium text-sm',
            activeTab === 'tickets'
              ? 'border-primary-500 text-primary-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          Tickets
        </button>
        <button
          @click="activeTab = 'customers'"
          :class="[
            'py-2 px-1 border-b-2 font-medium text-sm',
            activeTab === 'customers'
              ? 'border-primary-500 text-primary-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          Customers
        </button>
      </nav>
    </div>

    <!-- Tickets Tab -->
    <div v-if="activeTab === 'tickets'">
      <TicketsView
        :loading="loading"
        @refresh="loadTickets"
        @ticket-updated="handleTicketUpdated"
      />
    </div>

    <!-- Customers Tab -->
    <div v-if="activeTab === 'customers'">
      <CustomersView
        :loading="loading"
        @refresh="loadCustomers"
        @customer-selected="handleCustomerSelected"
      />
    </div>

    <!-- Create Ticket Modal -->
    <CreateTicketModal
      v-if="showCreateModal"
      :customers="customers"
      @close="showCreateModal = false"
      @ticket-created="handleTicketCreated"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import api from '@/services/api'
import {
  ArrowPathIcon,
  ExclamationTriangleIcon
} from '@heroicons/vue/24/outline'

// Components
import TicketsView from '@/components/syncromsp/TicketsView.vue'
import CustomersView from '@/components/syncromsp/CustomersView.vue'
import CreateTicketModal from '@/components/syncromsp/CreateTicketModal.vue'

const toast = useToast()

// Reactive state
const loading = ref(true)
const syncing = ref(false)
const activeTab = ref('tickets')
const showCreateModal = ref(false)

const tickets = ref([])
const customers = ref([])
const lastSyncTime = ref(null)

// Mock connection status (always connected for demo)
const connected = ref(true)

// Computed properties
const connectionStatus = computed(() => {
  return connected.value ? 'bg-success-400' : 'bg-danger-400'
})

const connectionText = computed(() => {
  return connected.value ? 'Connected' : 'Disconnected'
})

const stats = computed(() => {
  const totalTickets = tickets.value.length
  const openTickets = tickets.value.filter(t => t.status === 'open').length
  const urgentTickets = tickets.value.filter(t => 
    t.priority === 'critical' || t.priority === 'high' || t.status === 'urgent'
  ).length
  
  return {
    total_tickets: totalTickets,
    open_tickets: openTickets,
    customers: customers.value.length,
    urgent_tickets: urgentTickets
  }
})

// Methods
const loadTickets = async () => {
  try {
    loading.value = true
    const response = await api.syncro.listTickets({ limit: 100 })
    tickets.value = response.data.tickets || []
  } catch (error) {
    toast.error('Failed to load tickets')
  } finally {
    loading.value = false
  }
}

const loadCustomers = async () => {
  try {
    loading.value = true
    const response = await api.syncro.listCustomers(100)
    customers.value = response.data.customers || []
  } catch (error) {
    toast.error('Failed to load customers')
  } finally {
    loading.value = false
  }
}

const syncData = async () => {
  syncing.value = true
  try {
    // Sync tickets
    const ticketSync = await api.syncro.syncTickets()
    
    // Reload data
    await Promise.all([loadTickets(), loadCustomers()])
    
    lastSyncTime.value = new Date()
    
    const syncResult = ticketSync.data
    toast.success(
      `Sync completed: ${syncResult.new_count} new, ${syncResult.updated_count} updated tickets`
    )
  } catch (error) {
    toast.error('Failed to sync data')
  } finally {
    syncing.value = false
  }
}

const handleTicketUpdated = (ticketId) => {
  // Refresh tickets after update
  loadTickets()
}

const handleCustomerSelected = (customer) => {
  // Handle customer selection (could filter tickets, show details, etc.)
  console.log('Customer selected:', customer)
}

const handleTicketCreated = (ticket) => {
  toast.success(`Mock ticket created: ${ticket.subject}`)
  showCreateModal.value = false
  loadTickets()
}

// Initialize
onMounted(async () => {
  await Promise.all([loadTickets(), loadCustomers()])
})
</script> 