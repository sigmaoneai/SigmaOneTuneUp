<template>
  <div class="card h-full">
    <div class="card-header">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-medium text-gray-900">Prompt Editor</h3>
        <div class="flex items-center space-x-2">
          <button 
            @click="savePrompt"
            :disabled="!selectedAgent || !promptModified"
            class="btn-sm btn-primary"
          >
            <DocumentCheckIcon class="w-3 h-3 mr-1" />
            Save
          </button>
          <button @click="resetPrompt" class="btn-sm btn-secondary">
            <ArrowPathIcon class="w-3 h-3 mr-1" />
            Reset
          </button>
        </div>
      </div>
    </div>
    <div class="card-body p-0">
      <div v-if="!selectedAgent" class="p-4 text-center py-12">
        <DocumentTextIcon class="w-12 h-12 text-gray-300 mx-auto mb-4" />
        <p class="text-gray-500">Select an agent to edit its prompt</p>
      </div>
      
      <div v-else class="p-4 space-y-4">
        <!-- Agent Selection -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Selected Agent</label>
          <select v-model="selectedAgent" class="form-select w-full">
            <option value="">Choose an agent...</option>
            <option v-for="agent in agents" :key="agent.id" :value="agent">
              {{ agent.name }}
            </option>
          </select>
        </div>

        <!-- System Prompt -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            System Prompt
            <span v-if="promptModified" class="text-orange-600 text-xs ml-1">• Modified</span>
          </label>
          <textarea 
            v-model="editedPrompt"
            rows="8"
            class="form-input w-full font-mono text-sm"
            placeholder="Enter the system prompt for this agent..."
            @input="onPromptEdit"
          ></textarea>
          <p class="text-xs text-gray-500 mt-1">
            This prompt defines the agent's personality, knowledge, and behavior
          </p>
        </div>

        <!-- Context Prompts -->
        <div>
          <div class="flex items-center justify-between mb-2">
            <label class="block text-sm font-medium text-gray-700">Context Prompts</label>
            <button @click="addContextPrompt" class="btn-sm btn-secondary text-xs">
              <PlusIcon class="w-3 h-3 mr-1" />
              Add Context
            </button>
          </div>
          
          <div v-if="contextPrompts.length === 0" class="text-center py-4 border-2 border-dashed border-gray-200 rounded">
            <p class="text-sm text-gray-500">No context prompts defined</p>
            <button @click="addContextPrompt" class="text-blue-600 hover:text-blue-800 text-sm">
              Add your first context prompt
            </button>
          </div>

          <div v-else class="space-y-3">
            <div 
              v-for="(context, index) in contextPrompts" 
              :key="index"
              class="border rounded-lg p-3 bg-gray-50"
            >
              <div class="flex items-center justify-between mb-2">
                <input 
                  v-model="context.name"
                  type="text"
                  placeholder="Context name (e.g., 'business_hours')"
                  class="form-input text-sm flex-1 mr-2"
                  @input="onPromptEdit"
                />
                <button 
                  @click="removeContextPrompt(index)"
                  class="text-red-600 hover:text-red-800"
                >
                  <TrashIcon class="w-4 h-4" />
                </button>
              </div>
              <textarea 
                v-model="context.prompt"
                rows="3"
                class="form-input w-full font-mono text-xs"
                placeholder="Context prompt content..."
                @input="onPromptEdit"
              ></textarea>
            </div>
          </div>
        </div>

        <!-- Prompt Statistics -->
        <div class="bg-gray-50 rounded-lg p-3">
          <div class="text-sm font-medium text-gray-700 mb-2">Prompt Statistics</div>
          <div class="grid grid-cols-2 gap-4 text-xs text-gray-600">
            <div>
              <div class="font-medium">System Prompt</div>
              <div>{{ editedPrompt?.length || 0 }} characters</div>
              <div>~{{ Math.ceil((editedPrompt?.length || 0) / 4) }} tokens</div>
            </div>
            <div>
              <div class="font-medium">Context Prompts</div>
              <div>{{ contextPrompts.length }} prompts</div>
              <div>{{ totalContextLength }} characters</div>
            </div>
          </div>
          <div class="mt-2 pt-2 border-t border-gray-200">
            <div class="text-xs text-gray-500">
              Total estimated tokens: ~{{ Math.ceil(((editedPrompt?.length || 0) + totalContextLength) / 4) }}
            </div>
          </div>
        </div>

        <!-- Test Prompt Button -->
        <div class="pt-2">
          <button 
            @click="testPrompt"
            :disabled="!selectedAgent || !editedPrompt"
            class="btn-primary w-full"
          >
            <ChatBubbleLeftRightIcon class="w-4 h-4 mr-2" />
            Test This Prompt
          </button>
          <p class="text-xs text-gray-500 mt-1 text-center">
            Start a call to test how this agent responds with the current prompt
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { 
  DocumentCheckIcon, 
  ArrowPathIcon, 
  DocumentTextIcon,
  PlusIcon,
  TrashIcon,
  ChatBubbleLeftRightIcon
} from '@heroicons/vue/24/outline'

export default {
  name: 'PromptEditor',
  components: {
    DocumentCheckIcon,
    ArrowPathIcon,
    DocumentTextIcon,
    PlusIcon,
    TrashIcon,
    ChatBubbleLeftRightIcon
  },
  props: {
    agents: {
      type: Array,
      default: () => []
    },
    selectedAgent: {
      type: Object,
      default: null
    }
  },
  emits: ['update:selectedAgent', 'save-prompt', 'test-prompt'],
  setup(props, { emit }) {
    const editedPrompt = ref('')
    const originalPrompt = ref('')
    const contextPrompts = ref([])
    const originalContextPrompts = ref([])

    const promptModified = computed(() => {
      return editedPrompt.value !== originalPrompt.value || 
             JSON.stringify(contextPrompts.value) !== JSON.stringify(originalContextPrompts.value)
    })

    const totalContextLength = computed(() => {
      return contextPrompts.value.reduce((total, context) => 
        total + (context.prompt?.length || 0), 0
      )
    })

    const selectedAgent = computed({
      get: () => props.selectedAgent,
      set: (value) => emit('update:selectedAgent', value)
    })

    // Watch for agent changes and load their prompt
    watch(() => props.selectedAgent, (newAgent) => {
      if (newAgent) {
        loadAgentPrompt(newAgent)
      }
    }, { immediate: true })

    const loadAgentPrompt = (agent) => {
      editedPrompt.value = agent.system_prompt || ''
      originalPrompt.value = agent.system_prompt || ''
      
      // Load context prompts if they exist
      contextPrompts.value = agent.context_prompts ? 
        Object.entries(agent.context_prompts).map(([name, prompt]) => ({ name, prompt })) : []
      originalContextPrompts.value = [...contextPrompts.value]
    }

    const onPromptEdit = () => {
      // This will trigger the promptModified computed property
    }

    const savePrompt = () => {
      if (!props.selectedAgent) return

      const contextPromptsObject = contextPrompts.value.reduce((obj, context) => {
        if (context.name && context.prompt) {
          obj[context.name] = context.prompt
        }
        return obj
      }, {})

      emit('save-prompt', {
        agent: props.selectedAgent,
        systemPrompt: editedPrompt.value,
        contextPrompts: contextPromptsObject
      })

      // Update originals after save
      originalPrompt.value = editedPrompt.value
      originalContextPrompts.value = [...contextPrompts.value]
    }

    const resetPrompt = () => {
      if (props.selectedAgent) {
        loadAgentPrompt(props.selectedAgent)
      }
    }

    const addContextPrompt = () => {
      contextPrompts.value.push({ name: '', prompt: '' })
    }

    const removeContextPrompt = (index) => {
      contextPrompts.value.splice(index, 1)
    }

    const testPrompt = () => {
      emit('test-prompt', {
        agent: props.selectedAgent,
        systemPrompt: editedPrompt.value,
        contextPrompts: contextPrompts.value
      })
    }

    return {
      editedPrompt,
      contextPrompts,
      promptModified,
      totalContextLength,
      selectedAgent,
      onPromptEdit,
      savePrompt,
      resetPrompt,
      addContextPrompt,
      removeContextPrompt,
      testPrompt
    }
  }
}
</script> 