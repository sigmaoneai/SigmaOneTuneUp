<template>
  <div class="card hover:shadow-card-hover transition-shadow duration-200">
    <!-- Card Header -->
    <div class="card-header">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <div :class="statusIndicator" class="w-3 h-3 rounded-full"></div>
          <h3 class="text-lg font-semibold text-gray-900 truncate">
            {{ agent.name }}
          </h3>
        </div>
        
        <!-- Actions Dropdown -->
        <div class="relative" ref="dropdownRef">
          <button
            @click="showDropdown = !showDropdown"
            class="p-1 rounded-md hover:bg-gray-100 transition-colors"
          >
            <EllipsisVerticalIcon class="w-5 h-5 text-gray-500" />
          </button>
          
          <!-- Dropdown Menu -->
          <div
            v-if="showDropdown"
            class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 z-10"
          >
            <div class="py-1">
              <router-link
                :to="`/agents/${agent.id}`"
                class="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                @click="showDropdown = false"
              >
                <EyeIcon class="w-4 h-4 mr-2" />
                View Details
              </router-link>
              
              <button
                @click="handleTestCall"
                class="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              >
                <PhoneIcon class="w-4 h-4 mr-2" />
                Test Call
              </button>
              
              <button
                @click="handleEdit"
                class="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              >
                <PencilIcon class="w-4 h-4 mr-2" />
                Edit
              </button>
              
              <div class="border-t border-gray-100"></div>
              
              <button
                @click="handleDelete"
                class="flex items-center w-full px-4 py-2 text-sm text-red-700 hover:bg-red-50"
              >
                <TrashIcon class="w-4 h-4 mr-2" />
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Card Body -->
    <div class="card-body">
      <!-- Status Badge -->
      <div class="flex items-center justify-between mb-4">
        <span :class="statusBadge" class="badge">
          {{ statusText }}
        </span>
        <span class="text-xs text-gray-500">
          {{ formatTime(agent.created_at) }}
        </span>
      </div>

      <!-- Prompt Preview -->
      <div class="mb-4">
        <p class="text-sm text-gray-600 line-clamp-3">
          {{ truncatedPrompt }}
        </p>
      </div>

      <!-- Agent Details -->
      <div class="space-y-2 text-xs">
        <div class="flex items-center justify-between">
          <span class="text-gray-500">Voice:</span>
          <span class="text-gray-900 font-medium">{{ agent.voice_id || 'Default' }}</span>
        </div>
        
        <div class="flex items-center justify-between">
          <span class="text-gray-500">RetellAI ID:</span>
          <span class="text-gray-900 font-mono text-xs truncate max-w-24">
            {{ agent.retell_agent_id }}
          </span>
        </div>
        
        <div v-if="agent.tools && agent.tools.length > 0" class="flex items-center justify-between">
          <span class="text-gray-500">Tools:</span>
          <span class="text-gray-900">{{ agent.tools.length }} configured</span>
        </div>
      </div>

      <!-- Quick Stats -->
      <div class="mt-4 pt-4 border-t border-gray-100">
        <div class="grid grid-cols-2 gap-4 text-center">
          <div>
            <div class="text-lg font-semibold text-gray-900">{{ callCount }}</div>
            <div class="text-xs text-gray-500">Calls</div>
          </div>
          <div>
            <div class="text-lg font-semibold text-gray-900">{{ successRate }}%</div>
            <div class="text-xs text-gray-500">Success</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Card Footer -->
    <div class="card-footer">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <!-- Phone Number Status -->
          <div class="flex items-center">
            <PhoneIcon class="w-4 h-4 text-gray-400 mr-1" />
            <span class="text-xs text-gray-600">
              {{ phoneNumberStatus }}
            </span>
          </div>
        </div>
        
        <div class="flex space-x-2">
          <button
            @click="handleTestCall"
            class="btn btn-sm bg-primary-50 text-primary-700 border-primary-200 hover:bg-primary-100"
          >
            Test Call
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { formatDistanceToNow } from 'date-fns'
import {
  EllipsisVerticalIcon,
  EyeIcon,
  PhoneIcon,
  PencilIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  agent: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['test-call', 'edit', 'delete'])

// Reactive state
const showDropdown = ref(false)
const dropdownRef = ref(null)

// Computed properties
const statusIndicator = computed(() => {
  return props.agent.is_active ? 'bg-success-400' : 'bg-gray-400'
})

const statusBadge = computed(() => {
  return props.agent.is_active ? 'badge-success' : 'badge-gray'
})

const statusText = computed(() => {
  return props.agent.is_active ? 'Active' : 'Inactive'
})

const truncatedPrompt = computed(() => {
  const maxLength = 150
  if (props.agent.prompt.length <= maxLength) {
    return props.agent.prompt
  }
  return props.agent.prompt.substring(0, maxLength) + '...'
})

const callCount = computed(() => {
  // This would come from actual call statistics
  return Math.floor(Math.random() * 100) // Placeholder
})

const successRate = computed(() => {
  // This would come from actual success rate calculation
  return Math.floor(Math.random() * 40) + 60 // Placeholder (60-100%)
})

const phoneNumberStatus = computed(() => {
  // This would come from actual phone number assignment data
  const hasPhone = Math.random() > 0.3 // Placeholder
  return hasPhone ? 'Phone assigned' : 'No phone number'
})

// Methods
const formatTime = (timestamp) => {
  return formatDistanceToNow(new Date(timestamp), { addSuffix: true })
}

const handleTestCall = () => {
  showDropdown.value = false
  emit('test-call', props.agent)
}

const handleEdit = () => {
  showDropdown.value = false
  emit('edit', props.agent)
}

const handleDelete = () => {
  showDropdown.value = false
  emit('delete', props.agent)
}

// Click outside handler
const handleClickOutside = (event) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    showDropdown.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style> 