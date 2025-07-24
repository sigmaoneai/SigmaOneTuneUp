<template>
  <div class="space-y-6">
    <!-- Search Bar -->
    <div class="flex flex-col sm:flex-row gap-4">
      <div class="flex-1">
        <div class="relative">
          <MagnifyingGlassIcon class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search customers by name, business, or email..."
            class="form-input pl-10"
            @input="debouncedSearch"
          />
        </div>
      </div>
      <div class="flex space-x-3">
        <button
          @click="refreshCustomers"
          :disabled="refreshing"
          class="btn-secondary"
        >
          <ArrowPathIcon 
            :class="['w-4 h-4 mr-2', refreshing ? 'animate-spin' : '']" 
          />
          Refresh
        </button>
      </div>
    </div>

    <!-- Customers Grid -->
    <div class="card">
      <div class="card-header">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-lg font-medium text-gray-900">Customers</h3>
            <p class="text-sm text-gray-500">
              {{ filteredCustomers.length }} customers found
            </p>
          </div>
        </div>
      </div>

      <div class="card-body p-0">
        <template v-if="loading">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
            <div v-for="i in 6" :key="i" class="animate-pulse">
              <div class="border border-gray-200 rounded-lg p-4">
                <div class="flex items-center space-x-3">
                  <div class="w-12 h-12 bg-gray-200 rounded-full"></div>
                  <div class="flex-1">
                    <div class="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                    <div class="h-3 bg-gray-100 rounded w-1/2"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>

        <template v-else-if="filteredCustomers.length === 0">
          <div class="text-center py-12">
            <BuildingOffice2Icon class="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 class="text-lg font-medium text-gray-900 mb-2">No customers found</h3>
            <p class="text-gray-600 mb-6">
              {{ searchQuery 
                ? "Try adjusting your search terms" 
                : "No customers available in your SyncroMSP account" }}
            </p>
            <button
              v-if="searchQuery"
              @click="clearSearch"
              class="btn-secondary"
            >
              Clear Search
            </button>
          </div>
        </template>

        <template v-else>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
            <div
              v-for="customer in paginatedCustomers"
              :key="customer.id"
              class="border border-gray-200 rounded-lg p-4 hover:border-primary-300 hover:shadow-sm cursor-pointer transition-all duration-200"
              @click="viewCustomer(customer)"
            >
              <!-- Customer Header -->
              <div class="flex items-center space-x-3 mb-3">
                <div class="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                  <span class="text-primary-600 font-semibold text-lg">
                    {{ getInitials(customer.business_name || customer.contact_name) }}
                  </span>
                </div>
                <div class="flex-1 min-w-0">
                  <h4 class="text-sm font-semibold text-gray-900 truncate">
                    {{ customer.business_name }}
                  </h4>
                  <p class="text-xs text-gray-500 truncate">
                    {{ customer.contact_name }}
                  </p>
                </div>
              </div>

              <!-- Customer Details -->
              <div class="space-y-2">
                <div class="flex items-center text-xs text-gray-600">
                  <EnvelopeIcon class="w-3 h-3 mr-2 flex-shrink-0" />
                  <span class="truncate">{{ customer.email }}</span>
                </div>
                <div class="flex items-center text-xs text-gray-600">
                  <PhoneIcon class="w-3 h-3 mr-2 flex-shrink-0" />
                  <span>{{ customer.phone }}</span>
                </div>
                <div v-if="customer.address" class="flex items-start text-xs text-gray-600">
                  <MapPinIcon class="w-3 h-3 mr-2 flex-shrink-0 mt-0.5" />
                  <span class="line-clamp-2">{{ customer.address }}</span>
                </div>
              </div>

              <!-- Customer Stats (if available) -->
              <div v-if="customer.tickets_count !== undefined" class="mt-4 pt-3 border-t border-gray-100">
                <div class="flex items-center justify-between text-xs">
                  <div class="text-center">
                    <div class="font-semibold text-gray-900">{{ customer.tickets_count || 0 }}</div>
                    <div class="text-gray-500">Total Tickets</div>
                  </div>
                  <div class="text-center">
                    <div class="font-semibold text-warning-600">{{ customer.open_tickets || 0 }}</div>
                    <div class="text-gray-500">Open</div>
                  </div>
                  <div class="text-center">
                    <div class="font-semibold text-success-600">{{ customer.account_status || 'Active' }}</div>
                    <div class="text-gray-500">Status</div>
                  </div>
                </div>
              </div>

              <!-- Last Activity -->
              <div v-if="customer.last_activity" class="mt-3 pt-2 border-t border-gray-100">
                <p class="text-xs text-gray-500">
                  Last activity: {{ formatTime(customer.last_activity) }}
                </p>
              </div>

              <!-- Customer Since -->
              <div class="mt-2">
                <p class="text-xs text-gray-400">
                  Customer since {{ formatDate(customer.created_at) }}
                </p>
              </div>
            </div>
          </div>

          <!-- Pagination -->
          <div v-if="totalPages > 1" class="px-6 py-3 border-t border-gray-200 bg-gray-50">
            <div class="flex items-center justify-between">
              <div class="text-sm text-gray-500">
                Showing {{ (currentPage - 1) * pageSize + 1 }} to {{ Math.min(currentPage * pageSize, filteredCustomers.length) }} 
                of {{ filteredCustomers.length }} customers
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

    <!-- Customer Detail Modal -->
    <CustomerDetailModal
      v-if="showDetailModal && selectedCustomer"
      :customer="selectedCustomer"
      @close="showDetailModal = false"
      @create-ticket="handleCreateTicket"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { format, formatDistanceToNow } from 'date-fns'
import api from '@/services/api'
import {
  MagnifyingGlassIcon,
  ArrowPathIcon,
  BuildingOffice2Icon,
  EnvelopeIcon,
  PhoneIcon,
  MapPinIcon
} from '@heroicons/vue/24/outline'

// Components
import CustomerDetailModal from './CustomerDetailModal.vue'

const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['refresh', 'customer-selected'])

const toast = useToast()

// Reactive state
const refreshing = ref(false)
const allCustomers = ref([])
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(12)

// Modal state
const showDetailModal = ref(false)
const selectedCustomer = ref(null)

// Computed properties
const filteredCustomers = computed(() => {
  let filtered = allCustomers.value

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(customer => 
      customer.business_name.toLowerCase().includes(query) ||
      customer.contact_name.toLowerCase().includes(query) ||
      customer.email.toLowerCase().includes(query) ||
      customer.phone.includes(query)
    )
  }

  return filtered
})

const paginatedCustomers = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredCustomers.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredCustomers.value.length / pageSize.value)
})

// Methods
const loadCustomers = async () => {
  try {
    const response = await api.syncro.listCustomers(200) // Load more customers
    allCustomers.value = response.data.customers || []
    
    // Load detailed info for each customer (mock data includes this)
    if (allCustomers.value.length > 0) {
      for (const customer of allCustomers.value) {
        try {
          const detailResponse = await api.syncro.getCustomer(customer.id)
          Object.assign(customer, detailResponse.data)
        } catch (error) {
          // Ignore errors for individual customers
          console.warn(`Failed to load details for customer ${customer.id}`)
        }
      }
    }
  } catch (error) {
    toast.error('Failed to load customers')
  }
}

const refreshCustomers = async () => {
  refreshing.value = true
  try {
    await loadCustomers()
    emit('refresh')
    toast.success('Customers refreshed')
  } catch (error) {
    toast.error('Failed to refresh customers')
  } finally {
    refreshing.value = false
  }
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

const clearSearch = () => {
  searchQuery.value = ''
  currentPage.value = 1
}

const viewCustomer = (customer) => {
  selectedCustomer.value = customer
  showDetailModal.value = true
  emit('customer-selected', customer)
}

const handleCreateTicket = (customer) => {
  // This would typically open a create ticket modal with customer pre-selected
  showDetailModal.value = false
  toast.info(`Create ticket functionality would open with ${customer.business_name} pre-selected`)
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

// Initialize
onMounted(() => {
  loadCustomers()
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