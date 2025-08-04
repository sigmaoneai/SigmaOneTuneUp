<template>
  <div class="card">
    <div class="card-header">
      <h3 class="text-lg font-medium text-gray-900">Call Controls</h3>
      <p class="text-sm text-gray-500">Choose your call type and configure accordingly</p>
    </div>
    <div class="card-body space-y-6">
      
      <!-- Phone Call Section -->
      <div class="border rounded-lg p-4 bg-blue-50 border-blue-200">
        <h4 class="text-md font-medium text-gray-900 mb-3 flex items-center">
          <PhoneIcon class="w-4 h-4 mr-2 text-blue-600" />
          Phone Call
        </h4>
        <div class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Agent</label>
            <select v-model="phoneCallAgent" class="form-select w-full" :disabled="currentCall">
              <option value="">Choose an agent...</option>
              <option v-for="agent in agents" :key="agent.id" :value="agent">
                {{ agent.name }}
              </option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Phone Number to Call</label>
            <input 
              v-model="phoneNumber" 
              type="tel" 
              placeholder="+1 (555) 123-4567"
              class="form-input w-full"
              :disabled="currentCall"
            />
          </div>
          
          <button 
            @click="startPhoneCall"
            :disabled="!phoneCallAgent || !phoneNumber || currentCall"
            class="btn-primary w-full"
          >
            <PhoneIcon class="w-4 h-4 mr-2" />
            {{ currentCall ? 'Call Active' : 'Start Phone Call' }}
          </button>
        </div>
      </div>

      <!-- Agent-to-Agent Call Section -->
      <div class="border rounded-lg p-4 bg-purple-50 border-purple-200">
        <h4 class="text-md font-medium text-gray-900 mb-3 flex items-center">
          <ChatBubbleLeftRightIcon class="w-4 h-4 mr-2 text-purple-600" />
          Agent-to-Agent Call
        </h4>
        <div class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Receiving Agent (Inbound)</label>
            <select v-model="receivingAgent" class="form-select w-full" :disabled="currentCall">
              <option value="">Choose receiving agent...</option>
              <option v-for="agent in agents" :key="agent.id" :value="agent">
                {{ agent.name }}
              </option>
            </select>
            <p class="text-xs text-gray-500 mt-1">This agent will receive the call</p>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Calling Agent (Outbound)</label>
            <select v-model="callingAgent" class="form-select w-full" :disabled="currentCall">
              <option value="">Choose calling agent...</option>
              <option v-for="agent in agents.filter(a => a.id !== receivingAgent?.id)" :key="agent.id" :value="agent">
                {{ agent.name }}
              </option>
            </select>
            <p class="text-xs text-gray-500 mt-1">This agent will make the call</p>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Initial Message</label>
            <input 
              v-model="initialMessage" 
              type="text" 
              placeholder="Hello, I need help with..."
              class="form-input w-full"
              :disabled="currentCall"
            />
            <p class="text-xs text-gray-500 mt-1">What the calling agent will say first</p>
          </div>
          
          <button 
            @click="startAgentToAgentCall"
            :disabled="!receivingAgent || !callingAgent || currentCall"
            class="btn-primary w-full"
          >
            <ChatBubbleLeftRightIcon class="w-4 h-4 mr-2" />
            {{ currentCall ? 'Call Active' : 'Start Agent-to-Agent Call' }}
          </button>
        </div>
      </div>

      <!-- Active Call Info -->
      <div v-if="currentCall" class="border rounded-lg p-4 bg-green-50 border-green-200">
        <div class="flex items-center justify-between">
          <div>
            <h4 class="text-md font-medium text-gray-900 flex items-center">
              <div class="w-3 h-3 bg-green-500 rounded-full mr-2 animate-pulse"></div>
              Call Active
            </h4>
            <p class="text-sm text-gray-600 mt-1">
              {{ currentCall.type === 'phone' ? 
                  `Calling ${currentCall.phoneNumber} with ${currentCall.agent.name}` :
                  `${currentCall.callingAgent.name} → ${currentCall.receivingAgent.name}` 
              }}
            </p>
            <p class="text-xs text-gray-500">
              Started: {{ formatTime(currentCall.startTime) }} • 
              Duration: {{ formatDuration(Date.now() - new Date(currentCall.startTime).getTime()) }}
            </p>
          </div>
          <button 
            @click="endCall"
            class="btn-danger btn-sm"
          >
            <PhoneIcon class="w-4 h-4 mr-1" />
            End Call
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { PhoneIcon, ChatBubbleLeftRightIcon } from '@heroicons/vue/24/outline'

export default {
  name: 'CallControls',
  components: {
    PhoneIcon,
    ChatBubbleLeftRightIcon
  },
  props: {
    agents: {
      type: Array,
      default: () => []
    },
    currentCall: {
      type: Object,
      default: null
    }
  },
  emits: ['start-phone-call', 'start-agent-call', 'end-call'],
  setup(props, { emit }) {
    const phoneCallAgent = ref(null)
    const phoneNumber = ref('')
    const receivingAgent = ref(null)
    const callingAgent = ref(null)
    const initialMessage = ref('Hello, I have a question.')

    const startPhoneCall = () => {
      if (!phoneCallAgent.value || !phoneNumber.value) return
      
      emit('start-phone-call', {
        agent: phoneCallAgent.value,
        phoneNumber: phoneNumber.value
      })
    }

    const startAgentToAgentCall = () => {
      if (!receivingAgent.value || !callingAgent.value) return
      
      emit('start-agent-call', {
        receivingAgent: receivingAgent.value,
        callingAgent: callingAgent.value,
        initialMessage: initialMessage.value
      })
    }

    const endCall = () => {
      emit('end-call')
    }

    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleTimeString()
    }

    const formatDuration = (ms) => {
      const seconds = Math.floor(ms / 1000)
      const mins = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${mins}:${secs.toString().padStart(2, '0')}`
    }

    return {
      phoneCallAgent,
      phoneNumber,
      receivingAgent,
      callingAgent,
      initialMessage,
      startPhoneCall,
      startAgentToAgentCall,
      endCall,
      formatTime,
      formatDuration
    }
  }
}
</script> 