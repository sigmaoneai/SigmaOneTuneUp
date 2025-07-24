<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Create Agent</h1>
          <p class="mt-2 text-gray-600">Create a new RetellAI voice agent</p>
        </div>
        <router-link to="/agents" class="btn-secondary">
          <ArrowLeftIcon class="w-4 h-4 mr-2" />
          Back to Agents
        </router-link>
      </div>
    </div>

    <!-- Create Agent Form -->
    <div class="space-y-8">
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-medium text-gray-900">Agent Configuration</h3>
          <p class="text-sm text-gray-500">Configure your new AI voice agent</p>
        </div>
        <div class="card-body">
          <form @submit.prevent="createAgent" class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label for="agentName" class="block text-sm font-medium text-gray-700 mb-2">
                  Agent Name *
                </label>
                <input
                  id="agentName"
                  v-model="formData.name"
                  type="text"
                  required
                  class="form-input"
                  placeholder="Enter agent name"
                />
              </div>

              <div>
                <label for="language" class="block text-sm font-medium text-gray-700 mb-2">
                  Language
                </label>
                <select id="language" v-model="formData.language" class="form-select">
                  <option value="en-US">English (US)</option>
                  <option value="en-GB">English (UK)</option>
                  <option value="es-ES">Spanish</option>
                  <option value="fr-FR">French</option>
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
                rows="3"
                class="form-textarea"
                placeholder="Enter agent description"
              ></textarea>
            </div>

            <div>
              <label for="prompt" class="block text-sm font-medium text-gray-700 mb-2">
                System Prompt *
              </label>
              <textarea
                id="prompt"
                v-model="formData.prompt"
                rows="6"
                required
                class="form-textarea"
                placeholder="Enter the system prompt that defines the agent's behavior and personality"
              ></textarea>
              <p class="text-xs text-gray-500 mt-1">
                This prompt will guide how the agent responds to calls
              </p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label for="voice" class="block text-sm font-medium text-gray-700 mb-2">
                  Voice
                </label>
                <select id="voice" v-model="formData.voice" class="form-select">
                  <option value="alloy">Alloy</option>
                  <option value="echo">Echo</option>
                  <option value="fable">Fable</option>
                  <option value="onyx">Onyx</option>
                  <option value="nova">Nova</option>
                  <option value="shimmer">Shimmer</option>
                </select>
              </div>

              <div>
                <label for="responseLatency" class="block text-sm font-medium text-gray-700 mb-2">
                  Response Latency
                </label>
                <select id="responseLatency" v-model="formData.responseLatency" class="form-select">
                  <option value="low">Low (Faster)</option>
                  <option value="medium">Medium</option>
                  <option value="high">High (More Thoughtful)</option>
                </select>
              </div>
            </div>

            <!-- Advanced Settings -->
            <div class="border-t pt-6">
              <h4 class="text-md font-medium text-gray-900 mb-4">Advanced Settings</h4>
              
              <div class="space-y-4">
                <label class="flex items-center">
                  <input
                    v-model="formData.enableInterruption"
                    type="checkbox"
                    class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span class="ml-2 text-sm text-gray-700">Enable interruption handling</span>
                </label>

                <label class="flex items-center">
                  <input
                    v-model="formData.enableWebhook"
                    type="checkbox"
                    class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span class="ml-2 text-sm text-gray-700">Enable webhook notifications</span>
                </label>

                <div v-if="formData.enableWebhook">
                  <label for="webhookUrl" class="block text-sm font-medium text-gray-700 mb-2">
                    Webhook URL
                  </label>
                  <input
                    id="webhookUrl"
                    v-model="formData.webhookUrl"
                    type="url"
                    class="form-input"
                    placeholder="https://your-webhook-endpoint.com/webhook"
                  />
                </div>
              </div>
            </div>

            <!-- Form Actions -->
            <div class="flex justify-end space-x-3 pt-6 border-t">
              <router-link to="/agents" class="btn-secondary">
                Cancel
              </router-link>
              <button
                type="submit"
                :disabled="creating"
                class="btn-primary"
              >
                <span v-if="creating">Creating...</span>
                <span v-else>Create Agent</span>
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

const formData = reactive({
  name: '',
  description: '',
  prompt: '',
  language: 'en-US',
  voice: 'alloy',
  responseLatency: 'medium',
  enableInterruption: true,
  enableWebhook: false,
  webhookUrl: ''
})

const createAgent = async () => {
  creating.value = true
  
  try {
    // In a real app, this would call the API
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    toast.success('Agent created successfully (mock)')
    router.push('/agents')
  } catch (error) {
    toast.error('Failed to create agent')
  } finally {
    creating.value = false
  }
}
</script> 