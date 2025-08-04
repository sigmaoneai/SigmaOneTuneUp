<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
      <!-- Modal Header -->
      <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <div>
          <h3 class="text-lg font-semibold text-gray-900">Create Support Ticket</h3>
          <p class="text-sm text-gray-500 mt-1">Create tickets is disabled in read-only mode</p>
        </div>
        <button
          @click="close"
          class="text-gray-400 hover:text-gray-500 transition-colors"
        >
          <XMarkIcon class="w-6 h-6" />
        </button>
      </div>

      <!-- Read-Only Notice -->
      <div class="px-6 py-3 bg-red-50 border-b border-red-200">
        <div class="flex items-center">
          <ExclamationTriangleIcon class="w-5 h-5 text-red-600 mr-2" />
          <p class="text-sm text-red-800">
            Read-Only Mode: Ticket creation is disabled to prevent unintended modifications to SyncroMSP.
          </p>
        </div>
      </div>

      <!-- Modal Body -->
      <div class="px-6 py-4 overflow-y-auto max-h-[60vh]">
        <form @submit.prevent="createTicket" class="space-y-6">
          <!-- Customer Selection -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Customer *
            </label>
            <div class="relative">
              <input
                v-model="customerSearch"
                type="text"
                placeholder="Search for customer..."
                class="form-input pr-10"
                @input="searchCustomers"
                @focus="showCustomerDropdown = true"
              />
              <MagnifyingGlassIcon class="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            </div>
            
            <!-- Customer Dropdown -->
            <div
              v-if="showCustomerDropdown && filteredCustomers.length > 0"
              class="absolute z-10 mt-1 w-full bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto"
            >
              <div
                v-for="customer in filteredCustomers.slice(0, 10)"
                :key="customer.id"
                @click="selectCustomer(customer)"
                class="px-4 py-2 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0"
              >
                <div class="font-medium text-sm">{{ customer.business_name }}</div>
                <div class="text-xs text-gray-500">{{ customer.contact_name }} • {{ customer.email }}</div>
              </div>
            </div>

            <!-- Selected Customer -->
            <div v-if="selectedCustomer" class="mt-3 p-3 bg-gray-50 rounded-lg">
              <div class="flex items-center justify-between">
                <div>
                  <div class="font-medium text-sm">{{ selectedCustomer.business_name }}</div>
                  <div class="text-xs text-gray-500">{{ selectedCustomer.contact_name }} • {{ selectedCustomer.email }}</div>
                </div>
                <button
                  type="button"
                  @click="clearCustomer"
                  class="text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          <!-- Subject -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Subject *
            </label>
            <input
              v-model="form.subject"
              type="text"
              placeholder="Brief description of the issue"
              class="form-input"
              maxlength="255"
              required
            />
            <div class="mt-1 text-xs text-gray-500">
              {{ form.subject.length }}/255 characters
            </div>
          </div>

          <!-- Priority -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Priority
              </label>
              <select v-model="form.priority" class="form-select">
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Problem Type
              </label>
              <select v-model="form.problemType" class="form-select">
                <option value="Email Issues">Email Issues</option>
                <option value="Network Issues">Network Issues</option>
                <option value="Performance Issues">Performance Issues</option>
                <option value="Hardware Issues">Hardware Issues</option>
                <option value="Software Issues">Software Issues</option>
                <option value="Backup Issues">Backup Issues</option>
                <option value="Security Issues">Security Issues</option>
                <option value="New User Setup">New User Setup</option>
                <option value="General Support">General Support</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>

          <!-- Description -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Description *
            </label>
            <textarea
              v-model="form.description"
              rows="4"
              placeholder="Detailed description of the issue, including steps to reproduce, error messages, etc."
              class="form-textarea"
              maxlength="2000"
              required
            ></textarea>
            <div class="mt-1 text-xs text-gray-500">
              {{ form.description.length }}/2000 characters
            </div>
          </div>

          <!-- Additional Options -->
          <div class="bg-gray-50 p-4 rounded-lg">
            <h4 class="text-sm font-medium text-gray-900 mb-3">Additional Options</h4>
            <div class="space-y-3">
              <label class="flex items-center">
                <input
                  v-model="form.urgent"
                  type="checkbox"
                  class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span class="ml-2 text-sm text-gray-700">Mark as urgent</span>
              </label>
              
              <label class="flex items-center">
                <input
                  v-model="form.followUp"
                  type="checkbox"
                  class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span class="ml-2 text-sm text-gray-700">Schedule follow-up</span>
              </label>
            </div>
          </div>
        </form>
      </div>

      <!-- Modal Footer -->
      <div class="px-6 py-4 border-t border-gray-200 flex items-center justify-end space-x-3">
        <button
          type="button"
          @click="close"
          class="btn-secondary"
        >
          Cancel
        </button>
        <button
          @click="createTicket"
          :disabled="!canCreate || creating"
          class="btn-primary"
        >
          <span v-if="creating">Creating...</span>
          <span v-else>Create Ticket</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useToast } from 'vue-toastification'
import api from '@/services/api'
import {
  XMarkIcon,
  MagnifyingGlassIcon,
  ExclamationTriangleIcon
} from '@heroicons/vue/24/outline'

const emit = defineEmits(['close', 'ticket-created'])
const toast = useToast()

// Reactive state
const creating = ref(false)
const customers = ref([])
const selectedCustomer = ref(null)
const customerSearch = ref('')
const showCustomerDropdown = ref(false)

const form = ref({
  subject: '',
  description: '',
  priority: 'medium',
  problemType: 'General Support',
  urgent: false,
  followUp: false
})

// Computed properties
const filteredCustomers = computed(() => {
  if (!customerSearch.value) return customers.value
  
  const search = customerSearch.value.toLowerCase()
  return customers.value.filter(customer =>
    customer.business_name.toLowerCase().includes(search) ||
    customer.contact_name.toLowerCase().includes(search) ||
    customer.email.toLowerCase().includes(search)
  )
})

const canCreate = computed(() => {
  return (
    selectedCustomer.value &&
    form.value.subject.trim() &&
    form.value.description.trim()
  )
})

// Methods
const loadCustomers = async () => {
  try {
    const response = await api.syncro.listCustomers(100)
    customers.value = response.data.customers || []
  } catch (error) {
    toast.error('Failed to load customers')
  }
}

const searchCustomers = () => {
  showCustomerDropdown.value = true
}

const selectCustomer = (customer) => {
  selectedCustomer.value = customer
  customerSearch.value = customer.business_name
  showCustomerDropdown.value = false
}

const clearCustomer = () => {
  selectedCustomer.value = null
  customerSearch.value = ''
}

const createTicket = async () => {
  // Disabled in read-only mode
  toast.error('Ticket creation is disabled in read-only mode')
}

const close = () => {
  emit('close')
}

// Click outside handler
const handleClickOutside = (event) => {
  if (!event.target.closest('.bg-white')) {
    showCustomerDropdown.value = false
  }
}

onMounted(() => {
  loadCustomers()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script> 