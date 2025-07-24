<template>
  <div class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="$emit('close')"></div>

      <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

      <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
        <form @submit.prevent="saveTemplate">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="w-full">
                <div class="flex items-center justify-between mb-6">
                  <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                    {{ isEditing ? 'Edit Template' : 'Create New Template' }}
                  </h3>
                  <button
                    type="button"
                    @click="$emit('close')"
                    class="text-gray-400 hover:text-gray-600"
                  >
                    <XMarkIcon class="h-6 w-6" />
                  </button>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <!-- Left Column -->
                  <div class="space-y-4">
                    <div>
                      <label for="name" class="block text-sm font-medium text-gray-700">Name *</label>
                      <input
                        id="name"
                        v-model="form.name"
                        type="text"
                        required
                        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        placeholder="template_name"
                      />
                    </div>

                    <div>
                      <label for="title" class="block text-sm font-medium text-gray-700">Title *</label>
                      <input
                        id="title"
                        v-model="form.title"
                        type="text"
                        required
                        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        placeholder="Human-readable title"
                      />
                    </div>

                    <div>
                      <label for="category" class="block text-sm font-medium text-gray-700">Category *</label>
                      <select
                        id="category"
                        v-model="form.category"
                        required
                        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      >
                        <option value="">Select a category</option>
                        <option value="support">IT Support</option>
                        <option value="sales">Sales</option>
                        <option value="appointment">Appointment Scheduling</option>
                        <option value="customer_service">Customer Service</option>
                        <option value="text_templates">Text Templates</option>
                        <option value="imported">Imported</option>
                        <option value="custom">Custom</option>
                      </select>
                    </div>

                    <div>
                      <label for="description" class="block text-sm font-medium text-gray-700">Description</label>
                      <textarea
                        id="description"
                        v-model="form.description"
                        rows="3"
                        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        placeholder="Describe what this template is for..."
                      ></textarea>
                    </div>

                    <!-- Variables Section -->
                    <div>
                      <div class="flex items-center justify-between">
                        <label class="block text-sm font-medium text-gray-700">Variables</label>
                        <button
                          type="button"
                          @click="addVariable"
                          class="inline-flex items-center px-2 py-1 border border-transparent text-xs font-medium rounded text-indigo-700 bg-indigo-100 hover:bg-indigo-200"
                        >
                          <PlusIcon class="h-3 w-3 mr-1" />
                          Add Variable
                        </button>
                      </div>
                      <div class="mt-2 space-y-2">
                        <div
                          v-for="(variable, index) in form.variables"
                          :key="index"
                          class="flex items-center space-x-2 p-2 border border-gray-200 rounded"
                        >
                          <input
                            v-model="variable.name"
                            type="text"
                            placeholder="Variable name"
                            class="flex-1 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                          />
                          <input
                            v-model="variable.description"
                            type="text"
                            placeholder="Description"
                            class="flex-1 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                          />
                          <input
                            v-model="variable.default"
                            type="text"
                            placeholder="Default value"
                            class="flex-1 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                          />
                          <button
                            type="button"
                            @click="removeVariable(index)"
                            class="text-red-500 hover:text-red-700"
                          >
                            <TrashIcon class="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Right Column -->
                  <div class="space-y-4">
                    <div>
                      <label for="template_content" class="block text-sm font-medium text-gray-700">Template Content *</label>
                      <textarea
                        id="template_content"
                        v-model="form.template_content"
                        rows="20"
                        required
                        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm font-mono text-sm"
                        placeholder="Enter your prompt template here. Use {variable_name} for variables..."
                      ></textarea>
                      <p class="mt-1 text-xs text-gray-500">
                        Use curly braces for variables: {company_name}, {user_name}, etc.
                      </p>
                    </div>

                    <!-- Preview Section -->
                    <div v-if="form.template_content && form.variables.length > 0">
                      <label class="block text-sm font-medium text-gray-700">Preview</label>
                      <div class="mt-1 p-3 bg-gray-50 border border-gray-200 rounded-md">
                        <div class="space-y-2 mb-3">
                          <div
                            v-for="variable in form.variables"
                            :key="variable.name"
                            class="flex items-center space-x-2"
                          >
                            <label class="text-xs text-gray-600 w-20">{{ variable.name }}:</label>
                            <input
                              v-model="previewValues[variable.name]"
                              type="text"
                              :placeholder="variable.default || 'Enter value'"
                              class="flex-1 text-xs rounded border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                            />
                          </div>
                        </div>
                        <div class="text-xs text-gray-700 bg-white p-2 rounded border">
                          {{ compiledPreview }}
                        </div>
                      </div>
                    </div>
                  </div>
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
              {{ saving ? 'Saving...' : (isEditing ? 'Update Template' : 'Create Template') }}
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
import { XMarkIcon, PlusIcon, TrashIcon } from '@heroicons/vue/24/outline'
import api from '@/services/api'

const props = defineProps({
  template: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'saved'])
const toast = useToast()

// Data
const saving = ref(false)
const previewValues = ref({})

const form = ref({
  name: '',
  title: '',
  description: '',
  category: '',
  template_content: '',
  variables: [],
  tools: []
})

// Computed
const isEditing = computed(() => !!props.template)

const compiledPreview = computed(() => {
  let compiled = form.value.template_content
  for (const [key, value] of Object.entries(previewValues.value)) {
    if (value) {
      compiled = compiled.replace(new RegExp(`{${key}}`, 'g'), value)
    }
  }
  return compiled
})

// Methods
const addVariable = () => {
  form.value.variables.push({
    name: '',
    description: '',
    type: 'string',
    required: true,
    default: ''
  })
}

const removeVariable = (index) => {
  form.value.variables.splice(index, 1)
}

const saveTemplate = async () => {
  saving.value = true
  try {
    const templateData = {
      name: form.value.name,
      title: form.value.title,
      description: form.value.description,
      category: form.value.category,
      template_content: form.value.template_content,
      variables: form.value.variables.filter(v => v.name), // Only include variables with names
      tools: form.value.tools
    }

    if (isEditing.value) {
      await api.put(`/prompts/templates/${props.template.id}`, templateData)
    } else {
      await api.post('/prompts/templates', templateData)
    }

    emit('saved')
  } catch (error) {
    console.error('Error saving template:', error)
    toast.error('Failed to save template')
  } finally {
    saving.value = false
  }
}

// Initialize preview values when variables change
watch(() => form.value.variables, (newVariables) => {
  const newPreviewValues = {}
  newVariables.forEach(variable => {
    if (variable.name) {
      newPreviewValues[variable.name] = previewValues.value[variable.name] || variable.default || ''
    }
  })
  previewValues.value = newPreviewValues
}, { deep: true })

// Lifecycle
onMounted(() => {
  if (props.template) {
    form.value = {
      name: props.template.name,
      title: props.template.title,
      description: props.template.description || '',
      category: props.template.category,
      template_content: props.template.template_content,
      variables: props.template.variables || [],
      tools: props.template.tools || []
    }

    // Initialize preview values
    const initialPreviewValues = {}
    if (props.template.variables) {
      props.template.variables.forEach(variable => {
        initialPreviewValues[variable.name] = variable.default || ''
      })
    }
    previewValues.value = initialPreviewValues
  }
})
</script> 