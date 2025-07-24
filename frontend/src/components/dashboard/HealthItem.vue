<template>
  <div class="flex items-center justify-between py-2">
    <div class="flex items-center">
      <div :class="statusDot" class="w-2.5 h-2.5 rounded-full mr-3"></div>
      <div>
        <p class="text-sm font-medium text-gray-900">{{ title }}</p>
        <p class="text-xs text-gray-500">{{ description }}</p>
      </div>
    </div>
    <div>
      <span :class="statusBadge" class="badge text-xs">
        {{ statusText }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  status: {
    type: String,
    required: true,
    validator: (value) => ['healthy', 'degraded', 'unhealthy', 'unknown'].includes(value)
  },
  description: {
    type: String,
    default: ''
  }
})

const statusDot = computed(() => {
  switch (props.status) {
    case 'healthy': return 'bg-success-400'
    case 'degraded': return 'bg-warning-400'
    case 'unhealthy': return 'bg-danger-400'
    default: return 'bg-gray-400'
  }
})

const statusBadge = computed(() => {
  switch (props.status) {
    case 'healthy': return 'badge-success'
    case 'degraded': return 'badge-warning'
    case 'unhealthy': return 'badge-danger'
    default: return 'badge-gray'
  }
})

const statusText = computed(() => {
  switch (props.status) {
    case 'healthy': return 'Healthy'
    case 'degraded': return 'Degraded'
    case 'unhealthy': return 'Unhealthy'
    default: return 'Unknown'
  }
})
</script> 