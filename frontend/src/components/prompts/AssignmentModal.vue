<template>
  <div class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="$emit('close')"></div>
      <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
      <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
        <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-lg leading-6 font-medium text-gray-900">
              Assign Scenario to Agents
            </h3>
            <button type="button" @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
              <XMarkIcon class="h-6 w-6" />
            </button>
          </div>

          <div class="space-y-4">
            <div class="p-3 bg-gray-50 rounded-md">
              <h4 class="font-medium text-gray-900">{{ scenario?.name }}</h4>
              <p class="text-sm text-gray-600">{{ scenario?.description }}</p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Select Agents</label>
              <div class="max-h-60 overflow-y-auto border border-gray-200 rounded-md">
                <div v-for="agent in agents" :key="agent.id" class="flex items-center p-3 hover:bg-gray-50">
                  <input
                    :id="`agent-${agent.id}`"
                    v-model="selectedAgents"
                    :value="agent.id"
                    type="checkbox"
                    class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                  />
                  <label :for="`agent-${agent.id}`" class="ml-3 flex-1 cursor-pointer">
                    <div class="text-sm font-medium text-gray-900">{{ agent.name }}</div>
                    <div class="text-sm text-gray-500">{{ agent.communication_channel }}</div>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
          <button
            @click="assignScenario"
            :disabled="assigning || selectedAgents.length === 0"
            class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50"
          >
            {{ assigning ? 'Assigning...' : `Assign to ${selectedAgents.length} Agent${selectedAgents.length !== 1 ? 's' : ''}` }}
          </button>
          <button
            type="button"
            @click="$emit('close')"
            class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import api from '@/services/api'

const props = defineProps({
  scenario: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'assigned'])
const toast = useToast()

// Data
const assigning = ref(false)
const agents = ref([])
const selectedAgents = ref([])

// Methods
const loadAgents = async () => {
  try {
    const response = await api.get('/agents')
    agents.value = response.data
  } catch (error) {
    console.error('Error loading agents:', error)
    toast.error('Failed to load agents')
  }
}

const assignScenario = async () => {
  if (selectedAgents.value.length === 0) return

  assigning.value = true
  try {
    await api.post('/prompts/assignments/bulk', {
      scenario_id: props.scenario.id,
      agent_ids: selectedAgents.value
    })

    emit('assigned')
  } catch (error) {
    console.error('Error assigning scenario:', error)
    toast.error('Failed to assign scenario')
  } finally {
    assigning.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadAgents()
})
</script> 