<template>
  <div class="space-y-4">
    <!-- Filters -->
    <div class="bg-white p-4 rounded-lg border border-gray-200">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Agent</label>
          <select
            v-model="filters.agent_id"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          >
            <option value="">All Agents</option>
            <option v-for="agent in agents" :key="agent.id" :value="agent.id">
              {{ agent.name }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Scenario</label>
          <select
            v-model="filters.scenario_id"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          >
            <option value="">All Scenarios</option>
            <option v-for="scenario in scenarios" :key="scenario.id" :value="scenario.id">
              {{ scenario.name }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Status</label>
          <select
            v-model="filters.is_active"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          >
            <option value="">All</option>
            <option :value="true">Active</option>
            <option :value="false">Inactive</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Assignments List -->
    <div class="bg-white shadow overflow-hidden sm:rounded-md">
      <div v-if="loading" class="p-6 text-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
        <p class="mt-2 text-sm text-gray-500">Loading assignments...</p>
      </div>
      <ul v-else-if="assignments.length > 0" class="divide-y divide-gray-200">
        <li v-for="assignment in assignments" :key="assignment.id" class="p-6 hover:bg-gray-50">
          <div class="flex items-center justify-between">
            <div class="flex-1 min-w-0">
              <div class="flex items-center space-x-3">
                <h3 class="text-lg font-medium text-gray-900">
                  Agent: {{ getAgentName(assignment.agent_id) }}
                </h3>
                <span
                  :class="[
                    assignment.is_active
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800',
                    'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium'
                  ]"
                >
                  {{ assignment.is_active ? 'Active' : 'Inactive' }}
                </span>
              </div>
              <div v-if="assignment.scenario" class="mt-2">
                <p class="text-sm text-gray-600">
                  <strong>Scenario:</strong> {{ assignment.scenario.name }}
                </p>
                <p class="text-sm text-gray-500">{{ assignment.scenario.description }}</p>
              </div>
              <div class="mt-2 flex items-center space-x-4 text-sm text-gray-500">
                <span class="flex items-center">
                  <CalendarIcon class="h-4 w-4 mr-1" />
                  Assigned {{ formatDate(assignment.assigned_at) }}
                </span>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <button
                @click="removeAssignment(assignment)"
                class="p-2 text-red-400 hover:text-red-600"
                title="Remove Assignment"
              >
                <TrashIcon class="h-5 w-5" />
              </button>
            </div>
          </div>
        </li>
      </ul>
      <div v-else class="p-6 text-center">
        <UserGroupIcon class="mx-auto h-12 w-12 text-gray-400" />
        <h3 class="mt-2 text-sm font-medium text-gray-900">No assignments found</h3>
        <p class="mt-1 text-sm text-gray-500">Assign scenarios to agents to see them here.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import {
  CalendarIcon,
  TrashIcon,
  UserGroupIcon
} from '@heroicons/vue/24/outline'
import api from '@/services/api'

const toast = useToast()

// Data
const loading = ref(false)
const assignments = ref([])
const agents = ref([])
const scenarios = ref([])

const filters = ref({
  agent_id: '',
  scenario_id: '',
  is_active: ''
})

// Methods
const loadAssignments = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (filters.value.agent_id) params.append('agent_id', filters.value.agent_id)
    if (filters.value.scenario_id) params.append('scenario_id', filters.value.scenario_id)
    if (filters.value.is_active !== '') params.append('is_active', filters.value.is_active)
    
    const response = await api.get(`/prompts/assignments?${params.toString()}`)
    assignments.value = response.data
  } catch (error) {
    console.error('Error loading assignments:', error)
    toast.error('Failed to load assignments')
  } finally {
    loading.value = false
  }
}

const loadAgents = async () => {
  try {
    const response = await api.get('/agents')
    agents.value = response.data
  } catch (error) {
    console.error('Error loading agents:', error)
  }
}

const loadScenarios = async () => {
  try {
    const response = await api.get('/prompts/scenarios?is_active=true')
    scenarios.value = response.data
  } catch (error) {
    console.error('Error loading scenarios:', error)
  }
}

const removeAssignment = async (assignment) => {
  if (!confirm('Are you sure you want to remove this assignment?')) return

  try {
    await api.delete(`/prompts/assignments/${assignment.id}`)
    toast.success('Assignment removed successfully')
    await loadAssignments()
  } catch (error) {
    console.error('Error removing assignment:', error)
    toast.error('Failed to remove assignment')
  }
}

const getAgentName = (agentId) => {
  const agent = agents.value.find(a => a.id === agentId)
  return agent ? agent.name : 'Unknown Agent'
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString()
}

// Watchers
watch(() => filters.value, () => {
  setTimeout(loadAssignments, 300)
}, { deep: true })

// Lifecycle
onMounted(async () => {
  await Promise.all([
    loadAssignments(),
    loadAgents(),
    loadScenarios()
  ])
})
</script> 