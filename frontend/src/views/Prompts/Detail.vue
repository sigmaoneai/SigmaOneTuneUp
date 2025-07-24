<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Prompt Details</h1>
          <p class="mt-2 text-gray-600">View and manage prompt configuration</p>
        </div>
        <div class="flex items-center space-x-3">
          <button @click="editPrompt" class="btn-secondary">
            <PencilIcon class="w-4 h-4 mr-2" />
            Edit
          </button>
          <router-link to="/prompts" class="btn-secondary">
            <ArrowLeftIcon class="w-4 h-4 mr-2" />
            Back to Prompts
          </router-link>
        </div>
      </div>
    </div>

    <!-- Prompt Information -->
    <div class="space-y-8">
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-medium text-gray-900">Prompt Information</h3>
          <p class="text-sm text-gray-500">Basic prompt details and metadata</p>
        </div>
        <div class="card-body">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-500">Prompt Name</label>
              <p class="text-sm text-gray-900 mt-1">{{ promptName || 'Loading...' }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-500">Category</label>
              <p class="text-sm text-gray-900 mt-1">Customer Service</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-500">Created</label>
              <p class="text-sm text-gray-900 mt-1">{{ new Date().toLocaleDateString() }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-500">Last Modified</label>
              <p class="text-sm text-gray-900 mt-1">{{ new Date().toLocaleDateString() }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Prompt Content -->
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-medium text-gray-900">Prompt Content</h3>
          <p class="text-sm text-gray-500">The full prompt text used by AI agents</p>
        </div>
        <div class="card-body">
          <div class="bg-gray-50 rounded-lg p-4">
            <pre class="text-sm text-gray-900 whitespace-pre-wrap font-mono">{{ samplePrompt }}</pre>
          </div>
        </div>
      </div>

      <!-- Usage Stats -->
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-medium text-gray-900">Usage Statistics</h3>
          <p class="text-sm text-gray-500">How this prompt is being used across agents</p>
        </div>
        <div class="card-body">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
            <div>
              <div class="text-2xl font-bold text-gray-900">3</div>
              <div class="text-sm text-gray-500">Active Agents</div>
            </div>
            <div>
              <div class="text-2xl font-bold text-primary-600">127</div>
              <div class="text-sm text-gray-500">Total Calls</div>
            </div>
            <div>
              <div class="text-2xl font-bold text-success-600">4.2</div>
              <div class="text-sm text-gray-500">Avg Rating</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Test Prompt -->
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-medium text-gray-900">Test Prompt</h3>
          <p class="text-sm text-gray-500">Test how this prompt responds to different inputs</p>
        </div>
        <div class="card-body">
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
                placeholder="Enter a test message to see how the prompt would respond..."
              ></textarea>
            </div>
            
            <div class="flex justify-end">
              <button
                @click="testPrompt"
                :disabled="!testInput.trim() || testing"
                class="btn-primary"
              >
                <span v-if="testing">Testing...</span>
                <span v-else>Test Prompt</span>
              </button>
            </div>

            <div v-if="testResponse" class="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <h4 class="text-sm font-medium text-blue-900 mb-2">Test Response:</h4>
              <p class="text-sm text-blue-800">{{ testResponse }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from 'vue-toastification'
import { ArrowLeftIcon, PencilIcon } from '@heroicons/vue/24/outline'

const route = useRoute()
const toast = useToast()

// Reactive state
const promptName = ref(null)
const testInput = ref('')
const testResponse = ref('')
const testing = ref(false)

const samplePrompt = `You are a helpful customer service agent for SigmaOne TuneUp, a premium automotive service company. Your role is to:

1. Greet customers warmly and professionally
2. Listen carefully to their automotive service needs
3. Schedule appointments for tune-ups, oil changes, and repairs
4. Provide accurate pricing information
5. Answer questions about our services
6. Handle complaints with empathy and solutions

Always maintain a friendly, professional tone. If you cannot answer a technical question, offer to connect them with a technician. Keep responses concise but helpful.

Company Information:
- Hours: Monday-Friday 8AM-6PM, Saturday 9AM-4PM
- Services: Oil changes, tune-ups, brake service, tire rotation, engine diagnostics
- Location: 123 Main Street, Anytown USA
- Phone: (555) 123-4567`

const editPrompt = () => {
  toast.info('Edit functionality would open the prompt editor')
}

const testPrompt = async () => {
  if (!testInput.value.trim()) return

  testing.value = true
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    testResponse.value = `Thank you for contacting SigmaOne TuneUp! I'd be happy to help you with "${testInput.value}". This is a simulated response based on the prompt configuration. In a real implementation, this would process your input through the AI model and return an appropriate response.`
    
    toast.success('Prompt test completed')
  } catch (error) {
    toast.error('Failed to test prompt')
  } finally {
    testing.value = false
  }
}

onMounted(() => {
  promptName.value = route.params.name || 'Default Prompt'
})
</script> 