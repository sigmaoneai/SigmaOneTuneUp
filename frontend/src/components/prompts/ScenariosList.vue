<template>
  <div class="space-y-4">
    <!-- Filters -->
    <div class="bg-white p-4 rounded-lg border border-gray-200">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Search</label>
          <input
            v-model="filters.search"
            type="text"
            placeholder="Search scenarios..."
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Template</label>
          <select
            v-model="filters.template_id"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          >
            <option value="">All Templates</option>
            <option v-for="template in templates" :key="template.id" :value="template.id">
              {{ template.title }}
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

    <!-- Scenarios List -->
    <div class="bg-white shadow overflow-hidden sm:rounded-md">
      <div v-if="loading" class="p-6 text-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
        <p class="mt-2 text-sm text-gray-500">Loading scenarios...</p>
      </div>
      <ul v-else-if="scenarios.length > 0" class="divide-y divide-gray-200">
        <li v-for="scenario in scenarios" :key="scenario.id" class="p-6 hover:bg-gray-50">
          <div class="flex items-center justify-between">
            <div class="flex-1 min-w-0">
              <div class="flex items-center space-x-3">
                <h3 class="text-lg font-medium text-gray-900 truncate">
                  {{ scenario.name }}
                </h3>
                <span
                  :class="[
                    scenario.is_active
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800',
                    'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium'
                  ]"
                >
                  {{ scenario.is_active ? 'Active' : 'Inactive' }}
                </span>
              </div>
              <p class="mt-1 text-sm text-gray-500">{{ scenario.description }}</p>
              <div class="mt-2 flex items-center space-x-4 text-sm text-gray-500">
                <span class="flex items-center" v-if="scenario.template">
                  <DocumentTextIcon class="h-4 w-4 mr-1" />
                  {{ scenario.template.title }}
                </span>
                <span class="flex items-center">
                  <CalendarIcon class="h-4 w-4 mr-1" />
                  {{ formatDate(scenario.created_at) }}
                </span>
              </div>
              <!-- Preview compiled prompt -->
              <div v-if="scenario.compiled_prompt" class="mt-3 p-2 bg-gray-50 rounded text-xs text-gray-600 max-h-20 overflow-y-auto">
                {{ scenario.compiled_prompt.substring(0, 200) }}{{ scenario.compiled_prompt.length > 200 ? '...' : '' }}
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <button
                @click="$emit('edit', scenario)"
                class="p-2 text-gray-400 hover:text-gray-600"
                title="Edit Scenario"
              >
                <PencilIcon class="h-5 w-5" />
              </button>
              <button
                @click="$emit('assign', scenario)"
                class="p-2 text-indigo-400 hover:text-indigo-600"
                title="Assign to Agents"
              >
                <UserGroupIcon class="h-5 w-5" />
              </button>
              <button
                @click="$emit('delete', scenario)"
                class="p-2 text-red-400 hover:text-red-600"
                title="Delete Scenario"
              >
                <TrashIcon class="h-5 w-5" />
              </button>
            </div>
          </div>
        </li>
      </ul>
      <div v-else class="p-6 text-center">
        <CogIcon class="mx-auto h-12 w-12 text-gray-400" />
        <h3 class="mt-2 text-sm font-medium text-gray-900">No scenarios found</h3>
        <p class="mt-1 text-sm text-gray-500">Create scenarios from your templates to get started.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import {
  DocumentTextIcon,
  CalendarIcon,
  PencilIcon,
  TrashIcon,
  UserGroupIcon,
  CogIcon
} from '@heroicons/vue/24/outline'
import api from '@/services/api'

const emit = defineEmits(['edit', 'delete', 'assign'])

// Data
const loading = ref(false)
const scenarios = ref([])
const templates = ref([])

const filters = ref({
  search: '',
  template_id: '',
  is_active: ''
})

// Methods
const loadScenarios = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (filters.value.search) params.append('search', filters.value.search)
    if (filters.value.template_id) params.append('template_id', filters.value.template_id)
    if (filters.value.is_active !== '') params.append('is_active', filters.value.is_active)
    
    const response = await api.get(`/prompts/scenarios?${params.toString()}`)
    scenarios.value = response.data
  } catch (error) {
    console.error('Error loading scenarios:', error)
  } finally {
    loading.value = false
  }
}

const loadTemplates = async () => {
  try {
    const response = await api.get('/prompts/templates?is_active=true')
    templates.value = response.data
  } catch (error) {
    console.error('Error loading templates:', error)
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString()
}

// Watchers
watch(() => filters.value, () => {
  setTimeout(loadScenarios, 300)
}, { deep: true })

// Lifecycle
onMounted(async () => {
  await Promise.all([
    loadScenarios(),
    loadTemplates()
  ])
})
</script> 