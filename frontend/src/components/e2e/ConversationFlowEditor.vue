<template>
  <div class="card h-full">
    <div class="card-header">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-medium text-gray-900">Conversation Flow Editor</h3>
        <div class="flex items-center space-x-2">
          <button @click="loadFlows" class="btn-sm btn-secondary">
            <ArrowPathIcon class="w-3 h-3 mr-1" />
            Refresh
          </button>
                     <button @click="loadTemplate" class="btn-sm btn-secondary">
             <DocumentIcon class="w-3 h-3 mr-1" />
             Load Template
           </button>
           <button @click="createNewFlow" class="btn-sm btn-primary">
             <PlusIcon class="w-3 h-3 mr-1" />
             New Flow
           </button>
        </div>
      </div>
    </div>
    <div class="card-body">
      <!-- Flow Selection -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">Select Flow</label>
        <select v-model="selectedFlow" class="form-select w-full" @change="onFlowChange">
          <option :value="null">Create new flow...</option>
          <option v-for="flow in conversationFlows" :key="flow.conversation_flow_id" :value="flow">
            {{ flow.conversation_flow_id }} ({{ flow.nodes?.length || 0 }} nodes)
          </option>
        </select>
      </div>

      <!-- Flow Configuration -->
      <div v-if="currentFlowData" class="space-y-4">
        <!-- Basic Settings -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Global Prompt</label>
            <textarea 
              v-model="currentFlowData.global_prompt"
              rows="3"
              class="form-input w-full text-sm"
              placeholder="You are a helpful customer service agent."
            ></textarea>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Start Speaker</label>
            <select v-model="currentFlowData.start_speaker" class="form-select w-full">
              <option value="agent">Agent</option>
              <option value="user">User</option>
            </select>
          </div>
        </div>

        <!-- Model Configuration -->
        <div class="border rounded-lg p-4 bg-gray-50">
          <h4 class="text-sm font-medium text-gray-900 mb-3">Model Configuration</h4>
          <div class="grid grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Model Type</label>
              <select v-model="currentFlowData.model_choice.type" class="form-select w-full">
                <option value="cascading">Cascading</option>
                <option value="single">Single</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Model</label>
              <select v-model="currentFlowData.model_choice.model" class="form-select w-full">
                <optgroup label="OpenAI">
                  <option value="gpt-4o">GPT-4o</option>
                  <option value="gpt-4">GPT-4</option>
                  <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                </optgroup>
                <optgroup label="Anthropic">
                  <option value="claude-3-7-sonnet">Claude 3.7 Sonnet</option>
                  <option value="claude-3-5-sonnet">Claude 3.5 Sonnet</option>
                  <option value="claude-3-haiku">Claude 3 Haiku</option>
                  <option value="claude-3-opus">Claude 3 Opus</option>
                </optgroup>
                <optgroup label="Other">
                  <option value="retell-llm">Retell LLM</option>
                </optgroup>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Temperature</label>
              <input 
                v-model.number="currentFlowData.model_temperature"
                type="number"
                min="0"
                max="2"
                step="0.1"
                class="form-input w-full"
              />
            </div>
          </div>
        </div>

        <!-- Nodes Editor -->
        <div class="border rounded-lg p-4">
          <div class="flex items-center justify-between mb-3">
            <h4 class="text-sm font-medium text-gray-900">Conversation Nodes</h4>
            <button @click="addNode" class="btn-xs btn-primary">
              <PlusIcon class="w-3 h-3 mr-1" />
              Add Node
            </button>
          </div>
          
          <div v-if="currentFlowData.nodes.length === 0" class="text-center py-4 border-2 border-dashed border-gray-200 rounded">
            <p class="text-sm text-gray-500">No nodes defined</p>
            <button @click="addNode" class="text-blue-600 hover:text-blue-800 text-sm">
              Add your first node
            </button>
          </div>

          <div v-else class="space-y-3">
            <div 
              v-for="(node, index) in currentFlowData.nodes" 
              :key="node.id"
              class="border rounded-lg p-3 bg-white"
            >
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center space-x-2">
                  <input 
                    v-model="node.id"
                    type="text"
                    placeholder="Node ID (e.g., 'start', 'greeting')"
                    class="form-input text-sm"
                  />
                  <select v-model="node.type" class="form-select text-sm">
                    <option value="conversation">Conversation</option>
                    <option value="tool_call">Tool Call</option>
                    <option value="end">End</option>
                  </select>
                </div>
                <button 
                  @click="removeNode(index)"
                  class="text-red-600 hover:text-red-800"
                >
                  <TrashIcon class="w-4 h-4" />
                </button>
              </div>
              
              <!-- Node Instruction -->
              <div class="mb-2">
                <label class="block text-xs font-medium text-gray-700 mb-1">Instruction</label>
                <textarea 
                  v-model="node.instruction.text"
                  rows="2"
                  class="form-input w-full text-xs"
                  placeholder="What should the agent do at this node?"
                ></textarea>
              </div>

              <!-- Node Edges -->
              <div class="border-t pt-2">
                <div class="flex items-center justify-between mb-1">
                  <label class="block text-xs font-medium text-gray-700">Transitions</label>
                  <button @click="addEdge(node)" class="btn-xs bg-gray-500 text-white">
                    <PlusIcon class="w-2 h-2 mr-1" />
                    Add Transition
                  </button>
                </div>
                
                <div v-if="node.edges && node.edges.length > 0" class="space-y-1">
                  <div 
                    v-for="(edge, edgeIndex) in node.edges" 
                    :key="edge.id"
                    class="flex items-center space-x-2 text-xs"
                  >
                    <input 
                      v-model="edge.transition_condition.prompt"
                      type="text"
                      placeholder="Condition (e.g., 'Customer wants to book appointment')"
                      class="form-input flex-1 text-xs"
                    />
                    <input 
                      v-model="edge.destination_node_id"
                      type="text"
                      placeholder="Next node ID"
                      class="form-input w-24 text-xs"
                    />
                    <button 
                      @click="removeEdge(node, edgeIndex)"
                      class="text-red-600 hover:text-red-800"
                    >
                      <XMarkIcon class="w-3 h-3" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex items-center space-x-3 pt-4">
          <button 
            @click="saveFlow"
            :disabled="!currentFlowData.nodes.length || saving"
            class="btn-primary"
          >
            {{ saving ? 'Saving...' : selectedFlow ? 'Update Flow' : 'Create Flow' }}
          </button>
          
          <button 
            v-if="selectedFlow"
            @click="deleteFlow"
            :disabled="saving"
            class="btn-danger"
          >
            Delete Flow
          </button>
          
          <button @click="resetFlow" class="btn-secondary">
            Reset
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { 
  ArrowPathIcon,
  PlusIcon,
  TrashIcon,
  XMarkIcon,
  DocumentIcon
} from '@heroicons/vue/24/outline'

export default {
  name: 'ConversationFlowEditor',
  components: {
    ArrowPathIcon,
    PlusIcon,
    TrashIcon,
    XMarkIcon,
    DocumentIcon
  },
  emits: ['flow-created', 'flow-updated', 'flow-deleted'],
  setup(props, { emit }) {
    const conversationFlows = ref([])
    const selectedFlow = ref(null)
    const currentFlowData = ref(null)
    const saving = ref(false)

    const defaultFlowData = () => ({
      global_prompt: "You are a helpful customer service agent.",
      start_speaker: "agent",
      model_choice: {
        type: "cascading",
        model: "claude-3-7-sonnet"
      },
      model_temperature: 0.7,
      nodes: []
    })

    const defaultNode = () => ({
      id: `node_${Date.now()}`,
      type: "conversation",
      instruction: {
        type: "prompt",
        text: ""
      },
      edges: []
    })

    const defaultEdge = () => ({
      id: `edge_${Date.now()}`,
      transition_condition: {
        type: "prompt",
        prompt: ""
      },
      destination_node_id: ""
    })

    const loadFlows = async () => {
      try {
        const response = await fetch('/api/v1/retellai/conversation-flows')
        if (response.ok) {
          const result = await response.json()
          conversationFlows.value = result.data || []
        }
      } catch (error) {
        console.error('Error loading conversation flows:', error)
      }
    }

    const createNewFlow = () => {
      selectedFlow.value = null
      currentFlowData.value = defaultFlowData()
    }

    const loadTemplate = () => {
      selectedFlow.value = null
      currentFlowData.value = {
        global_prompt: "You are a helpful customer service agent for a technology company. Be friendly, professional, and helpful.",
        start_speaker: "agent",
        model_choice: {
          type: "cascading",
          model: "claude-3-7-sonnet"
        },
        model_temperature: 0.7,
        nodes: [
          {
            id: "start",
            type: "conversation",
            instruction: {
              type: "prompt",
              text: "Greet the customer warmly and ask how you can help them today."
            },
            edges: [
              {
                id: "edge_1",
                transition_condition: {
                  type: "prompt",
                  prompt: "Customer has a technical support question"
                },
                destination_node_id: "technical_support"
              },
              {
                id: "edge_2", 
                transition_condition: {
                  type: "prompt",
                  prompt: "Customer wants to make a purchase or ask about pricing"
                },
                destination_node_id: "sales"
              }
            ]
          },
          {
            id: "technical_support",
            type: "conversation",
            instruction: {
              type: "prompt", 
              text: "Help the customer with their technical issue. Ask clarifying questions and provide step-by-step solutions."
            },
            edges: [
              {
                id: "edge_3",
                transition_condition: {
                  type: "prompt",
                  prompt: "Issue is resolved"
                },
                destination_node_id: "resolution"
              }
            ]
          },
          {
            id: "sales",
            type: "conversation",
            instruction: {
              type: "prompt",
              text: "Assist the customer with their purchase inquiry. Provide pricing information and help them choose the right product."
            },
            edges: [
              {
                id: "edge_4",
                transition_condition: {
                  type: "prompt",
                  prompt: "Customer is ready to purchase"
                },
                destination_node_id: "closing"
              }
            ]
          },
          {
            id: "resolution",
            type: "conversation",
            instruction: {
              type: "prompt",
              text: "Confirm the issue is resolved and ask if there's anything else you can help with."
            },
            edges: []
          },
          {
            id: "closing",
            type: "conversation", 
            instruction: {
              type: "prompt",
              text: "Help complete the purchase and thank the customer for their business."
            },
            edges: []
          }
        ]
      }
    }

    const onFlowChange = () => {
      if (selectedFlow.value) {
        currentFlowData.value = { ...selectedFlow.value }
      } else {
        createNewFlow()
      }
    }

    const addNode = () => {
      if (!currentFlowData.value.nodes) {
        currentFlowData.value.nodes = []
      }
      currentFlowData.value.nodes.push(defaultNode())
    }

    const removeNode = (index) => {
      currentFlowData.value.nodes.splice(index, 1)
    }

    const addEdge = (node) => {
      if (!node.edges) {
        node.edges = []
      }
      node.edges.push(defaultEdge())
    }

    const removeEdge = (node, edgeIndex) => {
      node.edges.splice(edgeIndex, 1)
    }

    const saveFlow = async () => {
      if (!currentFlowData.value.nodes.length) {
        alert('Please add at least one node to the flow.')
        return
      }

      saving.value = true
      try {
        const endpoint = selectedFlow.value 
          ? `/api/v1/retellai/conversation-flows/${selectedFlow.value.conversation_flow_id}`
          : '/api/v1/retellai/conversation-flows'
        
        const method = selectedFlow.value ? 'PATCH' : 'POST'
        
        const response = await fetch(endpoint, {
          method,
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(currentFlowData.value)
        })

        if (response.ok) {
          const result = await response.json()
          
          if (selectedFlow.value) {
            emit('flow-updated', result)
            alert('Flow updated successfully!')
          } else {
            emit('flow-created', result)
            alert('Flow created successfully!')
            selectedFlow.value = result
          }
          
          await loadFlows()
        } else {
          throw new Error(`HTTP ${response.status}`)
        }
      } catch (error) {
        console.error('Error saving flow:', error)
        alert('Failed to save flow: ' + error.message)
      } finally {
        saving.value = false
      }
    }

    const deleteFlow = async () => {
      if (!selectedFlow.value || !confirm('Are you sure you want to delete this conversation flow?')) {
        return
      }

      saving.value = true
      try {
        const response = await fetch(`/api/v1/retellai/conversation-flows/${selectedFlow.value.conversation_flow_id}`, {
          method: 'DELETE'
        })

        if (response.ok) {
          emit('flow-deleted', selectedFlow.value)
          alert('Flow deleted successfully!')
          createNewFlow()
          await loadFlows()
        } else {
          throw new Error(`HTTP ${response.status}`)
        }
      } catch (error) {
        console.error('Error deleting flow:', error)
        alert('Failed to delete flow: ' + error.message)
      } finally {
        saving.value = false
      }
    }

    const resetFlow = () => {
      if (selectedFlow.value) {
        currentFlowData.value = { ...selectedFlow.value }
      } else {
        currentFlowData.value = defaultFlowData()
      }
    }

    onMounted(() => {
      loadFlows()
      createNewFlow()
    })

    return {
      conversationFlows,
      selectedFlow,
      currentFlowData,
      saving,
      loadFlows,
      createNewFlow,
      loadTemplate,
      onFlowChange,
      addNode,
      removeNode,
      addEdge,
      removeEdge,
      saveFlow,
      deleteFlow,
      resetFlow
    }
  }
}
</script> 