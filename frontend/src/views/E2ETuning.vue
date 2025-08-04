<template>
  <div class="w-full px-4 sm:px-6 lg:px-8">
    <!-- Page Header -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">E2E Agent Tuning</h1>
          <p class="mt-2 text-gray-600">Test agents live and tune prompts in real-time</p>
        </div>
        <div class="flex items-center space-x-4">
          <div class="flex items-center">
            <div :class="['w-3 h-3 rounded-full mr-2', connectionStatus === 'connected' ? 'bg-green-500' : 'bg-red-500']"></div>
            <span class="text-sm text-gray-600">{{ connectionStatus === 'connected' ? 'Connected' : 'Disconnected' }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Service Manager -->
    <ServiceManager class="mb-8" />

    <!-- Editor Tabs -->
    <div class="mb-4">
      <div class="border-b border-gray-200">
        <nav class="-mb-px flex space-x-8">
          <button
            @click="activeTab = 'editor'"
            :class="[
              'py-2 px-1 border-b-2 font-medium text-sm',
              activeTab === 'editor'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Prompt Editor
          </button>
          <button
            @click="activeTab = 'flows'"
            :class="[
              'py-2 px-1 border-b-2 font-medium text-sm',
              activeTab === 'flows'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Conversation Flows
          </button>
        </nav>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Left Column: Controls -->
      <div class="lg:col-span-1 space-y-6">
        <!-- Call Controls -->
        <CallControls 
          :agents="agents"
          :current-call="currentCall"
          @start-phone-call="handleStartPhoneCall"
          @start-agent-call="handleStartAgentCall"
          @end-call="handleEndCall"
        />

        <!-- Routing Rules -->
        <RoutingRules 
          :routing-rules="routingRules"
          v-model:test-request-type="testRequestType"
          @add-rule="showAddRoutingRule"
          @edit-rule="editRoutingRule"
          @delete-rule="deleteRoutingRule"
          @toggle-rule="toggleRoutingRule"
          @load-defaults="loadDefaultRoutingRules"
        />
      </div>

      <!-- Middle Column: Live Transcript -->
      <div class="lg:col-span-1">
        <LiveTranscript 
          :transcript="transcript"
          :interim-transcripts="interimTranscripts"
          :speech-detected="speechDetected"
          :current-call="currentCall"
          @clear-transcript="clearTranscript"
        />
      </div>

      <!-- Right Column: Tabbed Editor -->
      <div class="lg:col-span-1">
        <!-- Prompt Editor Tab -->
        <PromptEditor 
          v-show="activeTab === 'editor'"
          :agents="agents"
          v-model:selected-agent="selectedAgent"
          @save-prompt="handleSavePrompt"
          @test-prompt="handleTestPrompt"
        />

        <!-- Conversation Flow Editor Tab -->
        <ConversationFlowEditor 
          v-show="activeTab === 'flows'"
          @flow-created="handleFlowCreated"
          @flow-updated="handleFlowUpdated"
          @flow-deleted="handleFlowDeleted"
        />
      </div>
    </div>

    <!-- Test Scenarios Section -->
    <div class="mt-8">
      <TestScenarios 
        :test-scenarios="testScenarios"
        :current-call="currentCall"
        @add-test="showAddTest"
        @edit-test="editTest"
        @delete-test="deleteTest"
        @run-test="runTest"
        @update-test-status="updateTestStatus"
        @update-test-notes="updateTestNotes"
        @load-defaults="loadDefaultTests"
      />
    </div>

    <!-- Created Tickets Section -->
    <div v-if="createdTickets.length > 0" class="mt-8">
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-medium text-gray-900">Created Tickets</h3>
          <p class="text-sm text-gray-500">Tickets created during this session</p>
        </div>
        <div class="card-body">
          <div class="space-y-3">
            <div v-for="ticket in createdTickets" :key="ticket.id" class="border rounded-lg p-4 bg-gray-50">
              <div class="flex items-center justify-between mb-2">
                <h4 class="font-medium text-gray-900">{{ ticket.subject }}</h4>
                <span class="badge bg-green-100 text-green-800">{{ ticket.status }}</span>
              </div>
              <p class="text-sm text-gray-600 mb-2">{{ ticket.description }}</p>
              <div class="text-xs text-gray-500">
                Created: {{ formatTime(ticket.createdAt) }} | 
                <a :href="ticket.url" target="_blank" class="text-blue-600 hover:text-blue-800">
                  View Ticket →
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modals will be imported as needed -->
    <!-- Test Modal, Routing Modal, etc. can be separate components -->
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { useWebSocket } from '@/composables/useWebSocket'
import api from '@/services/api'

// Import our new modular components
import ServiceManager from '@/components/e2e/ServiceManager.vue'
import CallControls from '@/components/e2e/CallControls.vue'
import LiveTranscript from '@/components/e2e/LiveTranscript.vue'
import PromptEditor from '@/components/e2e/PromptEditor.vue'
import RoutingRules from '@/components/e2e/RoutingRules.vue'
import TestScenarios from '@/components/e2e/TestScenarios.vue'
import ConversationFlowEditor from '@/components/e2e/ConversationFlowEditor.vue'

export default {
  name: 'E2ETuning',
  components: {
    ServiceManager,
    CallControls,
    LiveTranscript,
    PromptEditor,
    RoutingRules,
    TestScenarios,
    ConversationFlowEditor
  },
  setup() {
    // Data
    const agents = ref([])
    const currentCall = ref(null)
    const selectedAgent = ref(null)
    const transcript = ref([])
    const interimTranscripts = ref(new Map())
    const speechDetected = ref(new Map())
    const routingRules = ref([])
    const testRequestType = ref('sales')
    const testScenarios = ref([])
    const createdTickets = ref([])
    const activeTab = ref('editor')

    // WebSocket connection
    const { connectionStatus, connect, disconnect } = useWebSocket()

    // Methods
    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleTimeString()
    }

    const clearTranscript = () => {
      transcript.value = []
      interimTranscripts.value.clear()
      speechDetected.value.clear()
    }

    const handleStartPhoneCall = async (callData) => {
      try {
        const response = await api.post('/calls/start-phone-call', {
          agent_id: callData.agent.id,
          phone_number: callData.phoneNumber
        })
        
        currentCall.value = {
          id: response.data.call_id,
          type: 'phone',
          agent: callData.agent,
          phoneNumber: callData.phoneNumber,
          startTime: new Date().toISOString()
        }

        // Connect to WebSocket for this call
        connect(`/ws/transcript/${currentCall.value.id}`)
      } catch (error) {
        console.error('Error starting phone call:', error)
        alert('Failed to start phone call: ' + (error.response?.data?.detail || error.message))
      }
    }

    const handleStartAgentCall = async (callData) => {
      try {
        const response = await api.post('/calls/start-agent-call', {
          receiving_agent_id: callData.receivingAgent.id,
          calling_agent_id: callData.callingAgent.id,
          initial_message: callData.initialMessage
        })
        
        currentCall.value = {
          id: response.data.call_id,
          type: 'agent',
          receivingAgent: callData.receivingAgent,
          callingAgent: callData.callingAgent,
          startTime: new Date().toISOString()
        }

        connect(`/ws/transcript/${currentCall.value.id}`)
      } catch (error) {
        console.error('Error starting agent call:', error)
        alert('Failed to start agent call: ' + (error.response?.data?.detail || error.message))
      }
    }

    const handleEndCall = async () => {
      if (!currentCall.value) return

      try {
        await api.post(`/calls/${currentCall.value.id}/end`)
        currentCall.value = null
        disconnect()
      } catch (error) {
        console.error('Error ending call:', error)
      }
    }

    const handleSavePrompt = async (promptData) => {
      try {
        await api.put(`/agents/${promptData.agent.id}`, {
          system_prompt: promptData.systemPrompt,
          context_prompts: promptData.contextPrompts
        })
        
        // Update local agent data
        const agentIndex = agents.value.findIndex(a => a.id === promptData.agent.id)
        if (agentIndex !== -1) {
          agents.value[agentIndex].system_prompt = promptData.systemPrompt
          agents.value[agentIndex].context_prompts = promptData.contextPrompts
        }

        alert('Prompt saved successfully!')
      } catch (error) {
        console.error('Error saving prompt:', error)
        alert('Failed to save prompt: ' + (error.response?.data?.detail || error.message))
      }
    }

    const handleTestPrompt = (promptData) => {
      // This would trigger a test call with the modified prompt
      selectedAgent.value = {
        ...promptData.agent,
        system_prompt: promptData.systemPrompt,
        context_prompts: promptData.contextPrompts
      }
      alert('Modified prompt ready for testing. Start a call to test.')
    }

    // Routing Rules
    const showAddRoutingRule = () => {
      // Would open routing rule modal
      console.log('Add routing rule')
    }

    const editRoutingRule = (rule) => {
      console.log('Edit routing rule:', rule)
    }

    const deleteRoutingRule = (ruleId) => {
      const index = routingRules.value.findIndex(r => r.id === ruleId)
      if (index !== -1) {
        routingRules.value.splice(index, 1)
      }
    }

    const toggleRoutingRule = (ruleId, active) => {
      const rule = routingRules.value.find(r => r.id === ruleId)
      if (rule) {
        rule.active = active
      }
    }

    const loadDefaultRoutingRules = () => {
      // Load default routing rules
      console.log('Loading default routing rules')
    }

    // Test Scenarios
    const showAddTest = () => {
      console.log('Add test scenario')
    }

    const editTest = (test) => {
      console.log('Edit test:', test)
    }

    const deleteTest = (testId) => {
      const index = testScenarios.value.findIndex(t => t.id === testId)
      if (index !== -1) {
        testScenarios.value.splice(index, 1)
      }
    }

    const runTest = (test) => {
      console.log('Run test:', test)
    }

    const updateTestStatus = (testId, status) => {
      const test = testScenarios.value.find(t => t.id === testId)
      if (test) {
        test.status = status
        test.lastTested = new Date().toISOString()
      }
    }

    const updateTestNotes = (testId, notes) => {
      const test = testScenarios.value.find(t => t.id === testId)
      if (test) {
        test.notes = notes
      }
    }

    const loadDefaultTests = () => {
      console.log('Loading default tests')
    }

    // Conversation Flow Handlers
    const handleFlowCreated = (flow) => {
      console.log('Flow created:', flow)
      // Could refresh agents list if flows are attached to agents
    }

    const handleFlowUpdated = (flow) => {
      console.log('Flow updated:', flow)
      // Could refresh agents list if flows are attached to agents
    }

    const handleFlowDeleted = (flow) => {
      console.log('Flow deleted:', flow)
      // Could refresh agents list if flows are attached to agents
    }

    // Load initial data
    const loadData = async () => {
      try {
        // Load agents
        const agentsResponse = await api.get('/agents')
        agents.value = agentsResponse.data

        // Load other data as needed
      } catch (error) {
        console.error('Error loading data:', error)
      }
    }

    // Lifecycle
    onMounted(() => {
      loadData()
    })

    onUnmounted(() => {
      disconnect()
    })

    return {
      // Data
      agents,
      currentCall,
      selectedAgent,
      transcript,
      interimTranscripts,
      speechDetected,
      routingRules,
      testRequestType,
      testScenarios,
      createdTickets,
      connectionStatus,
      activeTab,

      // Methods
      formatTime,
      clearTranscript,
      handleStartPhoneCall,
      handleStartAgentCall,
      handleEndCall,
      handleSavePrompt,
      handleTestPrompt,

      // Routing
      showAddRoutingRule,
      editRoutingRule,
      deleteRoutingRule,
      toggleRoutingRule,
      loadDefaultRoutingRules,

      // Tests
      showAddTest,
      editTest,
      deleteTest,
      runTest,
      updateTestStatus,
      updateTestNotes,
      loadDefaultTests,

      // Conversation Flows
      handleFlowCreated,
      handleFlowUpdated,
      handleFlowDeleted
    }
  }
}
</script>

<style scoped>
.badge {
  @apply inline-flex items-center px-2 py-0.5 rounded text-xs font-medium;
}
</style> 