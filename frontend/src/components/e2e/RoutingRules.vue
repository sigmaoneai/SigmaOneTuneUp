<template>
  <div class="card">
    <div class="card-header">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-lg font-medium text-gray-900">Routing Rules</h3>
          <p class="text-sm text-gray-500">Configure how requests are routed to agents</p>
        </div>
        <button @click="$emit('add-rule')" class="btn-sm btn-primary">
          <PlusIcon class="w-3 h-3 mr-1" />
          Add Rule
        </button>
      </div>
    </div>
    <div class="card-body">
      <!-- Test Request Type -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">Test Request Type</label>
        <select v-model="testRequestType" class="form-select w-full">
          <option value="sales">Sales Inquiry</option>
          <option value="support">Technical Support</option>
          <option value="billing">Billing Question</option>
          <option value="general">General Information</option>
          <option value="emergency">Emergency/Urgent</option>
        </select>
        <div class="mt-2 p-2 bg-blue-50 rounded text-sm">
          <div class="text-gray-600">Routes to:</div>
          <div class="font-medium">{{ getRoutingDestination(testRequestType) }}</div>
        </div>
      </div>

      <!-- Active Rules Summary -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <div class="text-sm font-medium text-gray-900">Active Rules ({{ activeRulesCount }})</div>
          <button 
            @click="$emit('load-defaults')" 
            class="text-xs text-blue-600 hover:text-blue-800"
            title="Load default routing rules with prompt configurations"
          >
            Load Defaults
          </button>
        </div>
        <div class="space-y-2">
          <div v-for="rule in displayRules" :key="rule.id" class="text-xs border rounded p-2 bg-gray-50">
            <div class="flex justify-between items-start mb-1">
              <span class="text-gray-600 truncate font-medium">{{ rule.name }}</span>
              <div class="flex items-center space-x-1">
                <span :class="getRequestTypeBadge(rule.requestType)" class="badge text-xs">{{ rule.requestType }}</span>
                <button 
                  @click="$emit('edit-rule', rule)"
                  class="text-blue-600 hover:text-blue-800"
                >
                  <PencilIcon class="w-3 h-3" />
                </button>
                <button 
                  @click="$emit('delete-rule', rule.id)"
                  class="text-red-600 hover:text-red-800"
                >
                  <TrashIcon class="w-3 h-3" />
                </button>
              </div>
            </div>
            <div class="text-gray-900 font-medium mb-1">{{ rule.targetAgent?.name || 'No agent' }}</div>
            <div v-if="rule.promptConfig" class="text-xs text-blue-600">
              <div class="flex items-center">
                <span class="w-2 h-2 bg-blue-400 rounded-full mr-1"></span>
                {{ rule.promptConfig.systemPrompt }}
              </div>
              <div class="text-gray-500 mt-1">
                {{ Object.keys(rule.promptConfig.contextPrompts || {}).length }} context prompts
              </div>
            </div>
            <div class="text-xs text-gray-500 mt-1 flex items-center justify-between">
              <span>Priority: {{ rule.priority }}</span>
              <span>{{ rule.timeCondition?.days?.join(', ') || 'No time limit' }}</span>
              <label class="flex items-center">
                <input 
                  type="checkbox" 
                  :checked="rule.active"
                  @change="$emit('toggle-rule', rule.id, $event.target.checked)"
                  class="form-checkbox h-3 w-3 mr-1"
                />
                Active
              </label>
            </div>
          </div>
          
          <div v-if="remainingRulesCount > 0" class="text-xs text-gray-500 text-center">
            +{{ remainingRulesCount }} more rules
            <button @click="showAllRules = !showAllRules" class="text-blue-600 hover:text-blue-800 ml-1">
              {{ showAllRules ? 'Show less' : 'Show all' }}
            </button>
          </div>
          
          <div v-if="activeRulesCount === 0" class="text-xs text-gray-500 text-center py-4">
            <div class="mb-2">No active rules</div>
            <button 
              @click="$emit('load-defaults')" 
              class="text-blue-600 hover:text-blue-800 font-medium"
            >
              Load Default Rules
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { PlusIcon, PencilIcon, TrashIcon } from '@heroicons/vue/24/outline'

export default {
  name: 'RoutingRules',
  components: {
    PlusIcon,
    PencilIcon,
    TrashIcon
  },
  props: {
    routingRules: {
      type: Array,
      default: () => []
    },
    testRequestType: {
      type: String,
      default: 'sales'
    }
  },
  emits: [
    'update:testRequestType',
    'add-rule',
    'edit-rule',
    'delete-rule',
    'toggle-rule',
    'load-defaults'
  ],
  setup(props, { emit }) {
    const showAllRules = ref(false)

    const testRequestType = computed({
      get: () => props.testRequestType,
      set: (value) => emit('update:testRequestType', value)
    })

    const activeRules = computed(() => 
      props.routingRules.filter(r => r.active)
    )

    const activeRulesCount = computed(() => activeRules.value.length)

    const displayRules = computed(() => {
      const rules = activeRules.value
      return showAllRules.value ? rules : rules.slice(0, 3)
    })

    const remainingRulesCount = computed(() => 
      Math.max(0, activeRulesCount.value - 3)
    )

    const getRoutingDestination = (requestType) => {
      const matchingRule = activeRules.value.find(rule => 
        rule.requestType === requestType && rule.active
      )
      return matchingRule ? matchingRule.targetAgent?.name || 'Unknown Agent' : 'No matching rule'
    }

    const getRequestTypeBadge = (requestType) => {
      const badges = {
        'sales': 'bg-green-100 text-green-800',
        'support': 'bg-blue-100 text-blue-800',
        'billing': 'bg-yellow-100 text-yellow-800',
        'general': 'bg-gray-100 text-gray-800',
        'emergency': 'bg-red-100 text-red-800'
      }
      return badges[requestType] || 'bg-gray-100 text-gray-800'
    }

    return {
      showAllRules,
      testRequestType,
      activeRulesCount,
      displayRules,
      remainingRulesCount,
      getRoutingDestination,
      getRequestTypeBadge
    }
  }
}
</script>

<style scoped>
.badge {
  @apply inline-flex items-center px-2 py-0.5 rounded text-xs font-medium;
}
</style> 