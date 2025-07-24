<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Create Prompt</h1>
          <p class="mt-2 text-gray-600">Create a new AI prompt for your agents</p>
        </div>
        <router-link to="/prompts" class="btn-secondary">
          <ArrowLeftIcon class="w-4 h-4 mr-2" />
          Back to Prompts
        </router-link>
      </div>
    </div>

    <!-- Create Prompt Form -->
    <div class="space-y-8">
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-medium text-gray-900">Prompt Configuration</h3>
          <p class="text-sm text-gray-500">Configure your new AI prompt</p>
        </div>
        <div class="card-body">
          <form @submit.prevent="createPrompt" class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label for="promptName" class="block text-sm font-medium text-gray-700 mb-2">
                  Prompt Name *
                </label>
                <input
                  id="promptName"
                  v-model="formData.name"
                  type="text"
                  required
                  class="form-input"
                  placeholder="Enter prompt name"
                />
              </div>

              <div>
                <label for="category" class="block text-sm font-medium text-gray-700 mb-2">
                  Category
                </label>
                <select id="category" v-model="formData.category" class="form-select">
                  <option value="customer-service">Customer Service</option>
                  <option value="sales">Sales</option>
                  <option value="support">Technical Support</option>
                  <option value="appointment">Appointment Scheduling</option>
                  <option value="general">General</option>
                </select>
              </div>
            </div>

            <div>
              <label for="description" class="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <textarea
                id="description"
                v-model="formData.description"
                rows="2"
                class="form-textarea"
                placeholder="Brief description of what this prompt does"
              ></textarea>
            </div>

            <div>
              <label for="promptContent" class="block text-sm font-medium text-gray-700 mb-2">
                Prompt Content *
              </label>
              <textarea
                id="promptContent"
                v-model="formData.content"
                rows="12"
                required
                class="form-textarea font-mono"
                placeholder="Enter the full prompt content here..."
              ></textarea>
              <p class="text-xs text-gray-500 mt-1">
                This is the instruction that will guide the AI agent's behavior
              </p>
            </div>

            <!-- Prompt Settings -->
            <div class="border-t pt-6">
              <h4 class="text-md font-medium text-gray-900 mb-4">Settings</h4>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label for="temperature" class="block text-sm font-medium text-gray-700 mb-2">
                    Temperature (Creativity)
                  </label>
                  <input
                    id="temperature"
                    v-model.number="formData.temperature"
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    class="w-full"
                  />
                  <div class="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Focused (0.0)</span>
                    <span>{{ formData.temperature }}</span>
                    <span>Creative (1.0)</span>
                  </div>
                </div>

                <div>
                  <label for="maxTokens" class="block text-sm font-medium text-gray-700 mb-2">
                    Max Response Length
                  </label>
                  <select id="maxTokens" v-model="formData.maxTokens" class="form-select">
                    <option value="150">Short (150 tokens)</option>
                    <option value="300">Medium (300 tokens)</option>
                    <option value="500">Long (500 tokens)</option>
                    <option value="1000">Extended (1000 tokens)</option>
                  </select>
                </div>
              </div>

              <div class="mt-4 space-y-4">
                <label class="flex items-center">
                  <input
                    v-model="formData.isDefault"
                    type="checkbox"
                    class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span class="ml-2 text-sm text-gray-700">Set as default prompt for new agents</span>
                </label>

                <label class="flex items-center">
                  <input
                    v-model="formData.enableVersioning"
                    type="checkbox"
                    class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span class="ml-2 text-sm text-gray-700">Enable version history</span>
                </label>
              </div>
            </div>

            <!-- Test Prompt Section -->
            <div class="border-t pt-6">
              <h4 class="text-md font-medium text-gray-900 mb-4">Test Prompt</h4>
              
              <div class="space-y-4">
                <div>
                  <label for="testInput" class="block text-sm font-medium text-gray-700 mb-2">
                    Test Input
                  </label>
                  <textarea
                    id="testInput"
                    v-model="testInput"
                    rows="3"
                    class="form-textarea"
                    placeholder="Enter a test message to preview how this prompt would respond..."
                  ></textarea>
                </div>
                
                <button
                  type="button"
                  @click="testPrompt"
                  :disabled="!testInput.trim() || !formData.content.trim() || testing"
                  class="btn-secondary"
                >
                  <span v-if="testing">Testing...</span>
                  <span v-else>Test Prompt</span>
                </button>

                <div v-if="testResponse" class="p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <h5 class="text-sm font-medium text-blue-900 mb-2">Test Response:</h5>
                  <p class="text-sm text-blue-800">{{ testResponse }}</p>
                </div>
              </div>
            </div>

            <!-- Form Actions -->
            <div class="flex justify-end space-x-3 pt-6 border-t">
              <router-link to="/prompts" class="btn-secondary">
                Cancel
              </router-link>
              <button
                type="submit"
                :disabled="creating"
                class="btn-primary"
              >
                <span v-if="creating">Creating...</span>
                <span v-else>Create Prompt</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { ArrowLeftIcon } from '@heroicons/vue/24/outline'

const router = useRouter()
const toast = useToast()

// Reactive state
const creating = ref(false)
const testing = ref(false)
const testInput = ref('')
const testResponse = ref('')

const formData = reactive({
  name: '',
  description: '',
  content: '',
  category: 'customer-service',
  temperature: 0.7,
  maxTokens: '300',
  isDefault: false,
  enableVersioning: true
})

const testPrompt = async () => {
  if (!testInput.value.trim() || !formData.content.trim()) return

  testing.value = true
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    testResponse.value = `Based on your prompt configuration, the AI would respond to "${testInput.value}" using the instructions you provided. This is a simulated response - in production, this would process through the actual AI model with your custom prompt.`
    
    toast.success('Prompt test completed')
  } catch (error) {
    toast.error('Failed to test prompt')
  } finally {
    testing.value = false
  }
}

const createPrompt = async () => {
  creating.value = true
  
  try {
    // In a real app, this would call the API
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    toast.success('Prompt created successfully (mock)')
    router.push('/prompts')
  } catch (error) {
    toast.error('Failed to create prompt')
  } finally {
    creating.value = false
  }
}
</script> 