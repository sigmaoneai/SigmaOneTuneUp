<template>
  <div class="space-y-4">
    <template v-if="loading">
      <div v-for="i in 3" :key="i" class="animate-pulse">
        <div class="flex items-center justify-between py-2">
          <div class="h-4 bg-gray-200 rounded w-1/3"></div>
          <div class="h-4 bg-gray-200 rounded w-1/4"></div>
        </div>
      </div>
    </template>
    
    <template v-else>
      <!-- Overall Status -->
      <div class="flex items-center justify-between p-3 rounded-lg border"
           :class="overallStatusClasses">
        <div class="flex items-center">
          <div :class="overallStatusDot" class="w-3 h-3 rounded-full mr-3"></div>
          <div>
            <p class="font-medium">Overall System</p>
            <p class="text-sm opacity-80">{{ overallStatusText }}</p>
          </div>
        </div>
        <div :class="overallStatusIcon">
          <component :is="overallIcon" class="w-5 h-5" />
        </div>
      </div>

      <!-- Individual Services -->
      <div class="space-y-3">
        <HealthItem
          title="Database"
          :status="health.database"
          description="PostgreSQL connection and queries"
        />
        
        <HealthItem
          title="RetellAI API"
          :status="health.retell_ai"
          description="Voice AI service integration"
        />
        
        <HealthItem
          title="SyncroMSP API"
          :status="health.syncro_msp"
          description="MSP platform integration"
        />
      </div>

      <!-- Last Updated -->
      <div v-if="health.timestamp" class="text-xs text-gray-500 text-center pt-2 border-t">
        Last checked: {{ formatTime(health.timestamp) }}
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { 
  CheckCircleIcon, 
  ExclamationTriangleIcon, 
  XCircleIcon,
  QuestionMarkCircleIcon 
} from '@heroicons/vue/24/outline'
import { formatDistanceToNow } from 'date-fns'
import HealthItem from './HealthItem.vue'

const props = defineProps({
  health: {
    type: Object,
    default: () => ({
      database: 'unknown',
      retell_ai: 'unknown',
      syncro_msp: 'unknown',
      overall: 'unknown'
    })
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// Overall status computed properties
const overallStatusClasses = computed(() => {
  const status = props.health.overall
  switch (status) {
    case 'healthy':
      return 'bg-success-50 border-success-200 text-success-900'
    case 'degraded':
      return 'bg-warning-50 border-warning-200 text-warning-900'
    case 'unhealthy':
      return 'bg-danger-50 border-danger-200 text-danger-900'
    default:
      return 'bg-gray-50 border-gray-200 text-gray-900'
  }
})

const overallStatusDot = computed(() => {
  const status = props.health.overall
  switch (status) {
    case 'healthy': return 'bg-success-400'
    case 'degraded': return 'bg-warning-400'
    case 'unhealthy': return 'bg-danger-400'
    default: return 'bg-gray-400'
  }
})

const overallStatusText = computed(() => {
  const status = props.health.overall
  switch (status) {
    case 'healthy': return 'All systems operational'
    case 'degraded': return 'Some issues detected'
    case 'unhealthy': return 'System issues present'
    default: return 'Status unknown'
  }
})

const overallIcon = computed(() => {
  const status = props.health.overall
  switch (status) {
    case 'healthy': return CheckCircleIcon
    case 'degraded': return ExclamationTriangleIcon
    case 'unhealthy': return XCircleIcon
    default: return QuestionMarkCircleIcon
  }
})

const overallStatusIcon = computed(() => {
  const status = props.health.overall
  switch (status) {
    case 'healthy': return 'text-success-600'
    case 'degraded': return 'text-warning-600'
    case 'unhealthy': return 'text-danger-600'
    default: return 'text-gray-600'
  }
})

const formatTime = (timestamp) => {
  return formatDistanceToNow(new Date(timestamp), { addSuffix: true })
}
</script> 