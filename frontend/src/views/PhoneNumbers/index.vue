<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Page Header -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Phone Numbers</h1>
          <p class="mt-2 text-gray-600">Manage your RetellAI phone numbers and routing</p>
        </div>
        <button @click="purchaseNumber" class="btn-primary">
          <PlusIcon class="w-4 h-4 mr-2" />
          Purchase Number
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <div class="card">
        <div class="card-body text-center">
          <PhoneIcon class="w-8 h-8 text-primary-600 mx-auto mb-2" />
          <div class="text-2xl font-bold text-gray-900">{{ stats.totalNumbers }}</div>
          <div class="text-sm text-gray-500">Total Numbers</div>
        </div>
      </div>
      <div class="card">
        <div class="card-body text-center">
          <CheckCircleIcon class="w-8 h-8 text-success-600 mx-auto mb-2" />
          <div class="text-2xl font-bold text-gray-900">{{ stats.activeNumbers }}</div>
          <div class="text-sm text-gray-500">Active Numbers</div>
        </div>
      </div>
      <div class="card">
        <div class="card-body text-center">
          <ArrowDownLeftIcon class="w-8 h-8 text-blue-600 mx-auto mb-2" />
          <div class="text-2xl font-bold text-gray-900">{{ stats.inboundCalls }}</div>
          <div class="text-sm text-gray-500">Inbound Today</div>
        </div>
      </div>
      <div class="card">
        <div class="card-body text-center">
          <ArrowUpRightIcon class="w-8 h-8 text-green-600 mx-auto mb-2" />
          <div class="text-2xl font-bold text-gray-900">{{ stats.outboundCalls }}</div>
          <div class="text-sm text-gray-500">Outbound Today</div>
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
                placeholder="Search phone numbers..."
                class="form-input pl-10"
              />
            </div>
            
            <select v-model="statusFilter" class="form-select">
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>

            <select v-model="countryFilter" class="form-select">
              <option value="">All Countries</option>
              <option value="US">United States</option>
              <option value="CA">Canada</option>
              <option value="GB">United Kingdom</option>
            </select>
          </div>

          <button
            @click="refreshNumbers"
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

    <!-- Phone Numbers Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="number in filteredNumbers"
        :key="number.id"
        class="card hover:shadow-lg transition-shadow cursor-pointer"
        @click="viewNumber(number)"
      >
        <div class="card-body">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center">
              <div class="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                <PhoneIcon class="w-5 h-5 text-primary-600" />
              </div>
              <div class="ml-3">
                <h3 class="text-lg font-medium text-gray-900">{{ number.phone_number }}</h3>
                <p class="text-sm text-gray-500">{{ number.country }} • {{ number.region }}</p>
              </div>
            </div>
            <span :class="getStatusBadge(number.status)" class="badge">
              {{ number.status }}
            </span>
          </div>

          <div class="space-y-3">
            <div class="flex justify-between text-sm">
              <span class="text-gray-500">Agent:</span>
              <span class="text-gray-900">{{ number.agent_name || 'Not assigned' }}</span>
            </div>
            
            <div class="flex justify-between text-sm">
              <span class="text-gray-500">Type:</span>
              <span class="text-gray-900">{{ number.capabilities.join(', ') }}</span>
            </div>

            <div class="flex justify-between text-sm">
              <span class="text-gray-500">Calls Today:</span>
              <span class="text-gray-900">{{ number.calls_today || 0 }}</span>
            </div>

            <div class="flex justify-between text-sm">
              <span class="text-gray-500">Monthly Cost:</span>
              <span class="text-gray-900">${{ number.monthly_cost }}</span>
            </div>
          </div>

          <div class="mt-4 pt-4 border-t flex items-center justify-between">
            <div class="text-xs text-gray-500">
              Created {{ formatTime(number.created_at) }}
            </div>
            <div class="flex items-center space-x-2">
              <button
                @click.stop="testNumber(number)"
                class="text-blue-600 hover:text-blue-800 text-sm"
              >
                Test
              </button>
              <button
                @click.stop="configureNumber(number)"
                class="text-primary-600 hover:text-primary-800 text-sm"
              >
                Configure
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="!loading && filteredNumbers.length === 0" class="col-span-full">
        <div class="text-center py-12">
          <PhoneIcon class="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p class="text-gray-500">No phone numbers found</p>
          <p class="text-sm text-gray-400 mt-2">
            {{ searchQuery || statusFilter || countryFilter ? 'Try adjusting your filters' : 'Purchase your first phone number to get started' }}
          </p>
          <button v-if="!searchQuery && !statusFilter && !countryFilter" @click="purchaseNumber" class="btn-primary mt-4">
            <PlusIcon class="w-4 h-4 mr-2" />
            Purchase Number
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="i in 6" :key="i" class="card">
        <div class="card-body animate-pulse">
          <div class="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
          <div class="space-y-2">
            <div class="h-3 bg-gray-200 rounded"></div>
            <div class="h-3 bg-gray-200 rounded w-2/3"></div>
            <div class="h-3 bg-gray-200 rounded w-1/2"></div>
          </div>
        </div>
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
  PhoneIcon,
  PlusIcon,
  CheckCircleIcon,
  ArrowDownLeftIcon,
  ArrowUpRightIcon,
  MagnifyingGlassIcon,
  ArrowPathIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const toast = useToast()

// Reactive state
const loading = ref(false)
const phoneNumbers = ref([])
const searchQuery = ref('')
const statusFilter = ref('')
const countryFilter = ref('')

const stats = ref({
  totalNumbers: 3,
  activeNumbers: 3,
  inboundCalls: 42,
  outboundCalls: 28
})

// Computed properties
const filteredNumbers = computed(() => {
  let filtered = phoneNumbers.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(number => 
      number.phone_number.includes(query) ||
      number.agent_name?.toLowerCase().includes(query)
    )
  }

  if (statusFilter.value) {
    filtered = filtered.filter(number => number.status === statusFilter.value)
  }

  if (countryFilter.value) {
    filtered = filtered.filter(number => number.country === countryFilter.value)
  }

  return filtered
})

// Methods
const loadPhoneNumbers = async () => {
  loading.value = true
  try {
    const response = await api.retell.listPhoneNumbers()
    phoneNumbers.value = response.data.phone_numbers || []
  } catch (error) {
    toast.error('Failed to load phone numbers')
  } finally {
    loading.value = false
  }
}

const refreshNumbers = () => {
  loadPhoneNumbers()
}

const viewNumber = (number) => {
  router.push(`/phone-numbers/${number.id}`)
}

const purchaseNumber = () => {
  toast.info('Phone number purchase would open purchase dialog')
}

const testNumber = (number) => {
  toast.success(`Test call initiated for ${number.phone_number}`)
}

const configureNumber = (number) => {
  toast.info(`Configuration for ${number.phone_number} would open settings`)
}

const formatTime = (timestamp) => {
  return formatDistanceToNow(new Date(timestamp), { addSuffix: true })
}

const getStatusBadge = (status) => {
  switch (status) {
    case 'active': return 'badge-success'
    case 'inactive': return 'badge-gray'
    case 'suspended': return 'badge-warning'
    default: return 'badge-gray'
  }
}

// Initialize
onMounted(() => {
  loadPhoneNumbers()
})
</script> 