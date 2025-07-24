<template>
  <div v-if="isOpen" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
      <div class="mt-3">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium text-gray-900">Start Agent-to-Agent Call</h3>
          <button @click="close" class="text-gray-400 hover:text-gray-600">
            <XMarkIcon class="w-6 h-6" />
          </button>
        </div>

        <form @submit.prevent="initiateCall" class="space-y-4">
          <!-- Caller Agent Selection -->
          <div>
            <label for="caller-agent" class="block text-sm font-medium text-gray-700 mb-1">
              Caller Agent
            </label>
            <select
              id="caller-agent"
              v-model="formData.caller_agent_id"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              required
            >
              <option value="">Select caller agent...</option>
              <option v-for="agent in agents" :key="agent.id" :value="agent.id">
                {{ agent.name }}
              </option>
            </select>
          </div>

          <!-- Inbound Agent Selection -->
          <div>
            <label for="inbound-agent" class="block text-sm font-medium text-gray-700 mb-1">
              Inbound Agent
            </label>
            <select
              id="inbound-agent"
              v-model="formData.inbound_agent_id"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              required
            >
              <option value="">Select inbound agent...</option>
              <option 
                v-for="agent in agents" 
                :key="agent.id" 
                :value="agent.id"
                :disabled="agent.id === formData.caller_agent_id"
              >
                {{ agent.name }}
              </option>
            </select>
          </div>

          <!-- Call Purpose/Notes -->
          <div>
            <label for="call-notes" class="block text-sm font-medium text-gray-700 mb-1">
              Call Purpose (Optional)
            </label>
            <textarea
              id="call-notes"
              v-model="formData.notes"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Enter the purpose or notes for this agent-to-agent call..."
            ></textarea>
          </div>

          <!-- Agent Information Display -->
          <div v-if="callerAgent && inboundAgent" class="bg-gray-50 p-3 rounded-md">
            <h4 class="text-sm font-medium text-gray-700 mb-2">Call Summary</h4>
            <div class="text-sm text-gray-600 space-y-1">
              <div class="flex justify-between">
                <span>Caller:</span>
                <span class="font-medium">{{ callerAgent.name }}</span>
              </div>
              <div class="flex justify-between">
                <span>Receiving:</span>
                <span class="font-medium">{{ inboundAgent.name }}</span>
              </div>
              <div v-if="callerPhone && inboundPhone" class="flex justify-between">
                <span>Connection:</span>
                <span class="font-medium">{{ callerPhone.phone_number }} → {{ inboundPhone.phone_number }}</span>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              @click="close"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="!formData.caller_agent_id || !formData.inbound_agent_id || loading"
              class="px-4 py-2 text-sm font-medium text-white bg-primary-600 border border-transparent rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="loading">Initiating...</span>
              <span v-else>Start Call</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import { useToast } from 'vue-toastification'
import api from '@/services/api'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'call-initiated'])

const toast = useToast()
const loading = ref(false)
const agents = ref([])
const phoneNumbers = ref([])

const formData = ref({
  caller_agent_id: '',
  inbound_agent_id: '',
  notes: ''
})

// Computed properties
const callerAgent = computed(() => 
  agents.value.find(agent => agent.id === formData.value.caller_agent_id)
)

const inboundAgent = computed(() => 
  agents.value.find(agent => agent.id === formData.value.inbound_agent_id)
)

const callerPhone = computed(() => 
  phoneNumbers.value.find(phone => phone.agent_id === formData.value.caller_agent_id)
)

const inboundPhone = computed(() => 
  phoneNumbers.value.find(phone => phone.agent_id === formData.value.inbound_agent_id)
)

// Methods
const close = () => {
  formData.value = {
    caller_agent_id: '',
    inbound_agent_id: '',
    notes: ''
  }
  emit('close')
}

const loadAgents = async () => {
  try {
    const response = await api.agents.list()
    agents.value = response.data || []
  } catch (error) {
    toast.error('Failed to load agents')
  }
}

const loadPhoneNumbers = async () => {
  try {
    const response = await api.phoneNumbers.list()
    phoneNumbers.value = response.data || []
  } catch (error) {
    toast.error('Failed to load phone numbers')
  }
}

const initiateCall = async () => {
  if (!formData.value.caller_agent_id || !formData.value.inbound_agent_id) {
    toast.error('Please select both caller and inbound agents')
    return
  }

  if (formData.value.caller_agent_id === formData.value.inbound_agent_id) {
    toast.error('Caller and inbound agents must be different')
    return
  }

  loading.value = true
  
  try {
    const callData = {
      caller_agent_id: formData.value.caller_agent_id,
      inbound_agent_id: formData.value.inbound_agent_id,
      call_type: 'agent_to_agent',
      metadata: {
        notes: formData.value.notes,
        caller_agent_name: callerAgent.value?.name,
        inbound_agent_name: inboundAgent.value?.name
      }
    }

    const response = await api.calls.createAgentToAgent(callData)
    
    toast.success(`Agent-to-agent call initiated between ${callerAgent.value.name} and ${inboundAgent.value.name}`)
    emit('call-initiated', response.data)
    close()
    
  } catch (error) {
    toast.error('Failed to initiate agent-to-agent call: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// Load data when component mounts
onMounted(() => {
  loadAgents()
  loadPhoneNumbers()
})

// Watch for modal open to refresh data
watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    loadAgents()
    loadPhoneNumbers()
  }
})
</script>

<style scoped>
.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style> 