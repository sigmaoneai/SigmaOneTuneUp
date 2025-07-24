<template>
  <div class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="$emit('close')"></div>
      <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
      <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
        <form @submit.prevent="saveScenario">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-lg leading-6 font-medium text-gray-900">
                {{ isEditing ? 'Edit Scenario' : 'Create New Scenario' }}
              </h3>
              <button type="button" @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
                <XMarkIcon class="h-6 w-6" />
              </button>
            </div>

            <div class="space-y-4">
              <div>
                <label for="name" class="block text-sm font-medium text-gray-700">Name *</label>
                <input
                  id="name"
                  v-model="form.name"
                  type="text"
                  required
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  placeholder="Scenario name"
                />
              </div>

              <div>
                <label for="description" class="block text-sm font-medium text-gray-700">Description</label>
                <textarea
                  id="description"
                  v-model="form.description"
                  rows="3"
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  placeholder="Describe this scenario..."
                ></textarea>
              </div>

              <div v-if="!isEditing">
                <label for="template" class="block text-sm font-medium text-gray-700">Template *</label>
                <select
                  id="template"
                  v-model="form.template_id"
                  required
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                >
                  <option value="">Select a template</option>
                  <option v-for="template in templates" :key="template.id" :value="template.id">
                    {{ template.title }}
                  </option>
                </select>
              </div>

              <!-- Variable Values -->
              <div v-if="selectedTemplate && selectedTemplate.variables && selectedTemplate.variables.length > 0">
                <label class="block text-sm font-medium text-gray-700 mb-2">Variable Values</label>
                <div class="space-y-3">
                  <div v-for="variable in selectedTemplate.variables" :key="variable.name" class="grid grid-cols-3 gap-3">
                    <div class="text-sm text-gray-600">{{ variable.name }}</div>
                    <div class="text-xs text-gray-500">{{ variable.description }}</div>
                    <input
                      v-model="form.variable_values[variable.name]"
                      type="text"
                      :placeholder="variable.default || 'Enter value'"
                      class="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    />
                  </div>
                </div>
              </div>

              <!-- Preview -->
              <div v-if="compiledPreview">
                <label class="block text-sm font-medium text-gray-700">Preview</label>
                <div class="mt-1 p-3 bg-gray-50 border border-gray-200 rounded-md text-sm">
                  {{ compiledPreview }}
                </div>
              </div>
            </div>
          </div>

          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button
              type="submit"
              :disabled="saving"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50"
            >
              {{ saving ? 'Saving...' : (isEditing ? 'Update Scenario' : 'Create Scenario') }}
            </button>
            <button
              type="button"
              @click="$emit('close')"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import api from '@/services/api'

const props = defineProps({
  scenario: {
    type: Object,
    default: null
  },
  template: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'saved'])
const toast = useToast()

// Data
const saving = ref(false)
const templates = ref([])

const form = ref({
  name: '',
  description: '',
  template_id: '',
  variable_values: {}
})

// Computed
const isEditing = computed(() => !!props.scenario)

const selectedTemplate = computed(() => {
  if (props.template) return props.template
  return templates.value.find(t => t.id === form.value.template_id)
})

const compiledPreview = computed(() => {
  if (!selectedTemplate.value || !selectedTemplate.value.template_content) return ''
  
  let compiled = selectedTemplate.value.template_content
  for (const [key, value] of Object.entries(form.value.variable_values)) {
    if (value) {
      compiled = compiled.replace(new RegExp(`{${key}}`, 'g'), value)
    }
  }
  return compiled
})

// Methods
const loadTemplates = async () => {
  try {
    const response = await api.get('/prompts/templates?is_active=true')
    templates.value = response.data
  } catch (error) {
    console.error('Error loading templates:', error)
  }
}

const saveScenario = async () => {
  saving.value = true
  try {
    const scenarioData = {
      name: form.value.name,
      description: form.value.description,
      template_id: form.value.template_id,
      variable_values: form.value.variable_values
    }

    if (isEditing.value) {
      await api.put(`/prompts/scenarios/${props.scenario.id}`, scenarioData)
    } else {
      await api.post('/prompts/scenarios', scenarioData)
    }

    emit('saved')
  } catch (error) {
    console.error('Error saving scenario:', error)
    toast.error('Failed to save scenario')
  } finally {
    saving.value = false
  }
}

// Watchers
watch(() => selectedTemplate.value, (newTemplate) => {
  if (newTemplate && newTemplate.variables) {
    const newVariableValues = {}
    newTemplate.variables.forEach(variable => {
      newVariableValues[variable.name] = form.value.variable_values[variable.name] || variable.default || ''
    })
    form.value.variable_values = newVariableValues
  }
}, { immediate: true })

// Lifecycle
onMounted(async () => {
  if (!props.template) {
    await loadTemplates()
  }

  if (props.scenario) {
    form.value = {
      name: props.scenario.name,
      description: props.scenario.description || '',
      template_id: props.scenario.template_id,
      variable_values: props.scenario.variable_values || {}
    }
  } else if (props.template) {
    form.value.template_id = props.template.id
  }
})
</script> 