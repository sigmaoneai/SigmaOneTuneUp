<template>
  <div class="space-y-4">
    <template v-if="loading">
      <div v-for="i in 3" :key="i" class="animate-pulse">
        <div class="flex items-center space-x-3 py-3">
          <div class="w-10 h-10 bg-gray-200 rounded-full"></div>
          <div class="flex-1">
            <div class="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div class="h-3 bg-gray-100 rounded w-1/2"></div>
          </div>
          <div class="h-4 bg-gray-200 rounded w-16"></div>
        </div>
      </div>
    </template>

    <template v-else-if="calls.length === 0">
      <div class="text-center py-8">
        <PhoneIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p class="text-gray-500">No recent calls</p>
        <p class="text-sm text-gray-400">Calls will appear here once agents start receiving them</p>
      </div>
    </template>

    <template v-else>
      <div class="space-y-3">
        <div
          v-for="call in calls"
          :key="call.id"
          class="flex items-center space-x-3 py-3 hover:bg-gray-50 rounded-lg px-3 -mx-3 transition-colors cursor-pointer"
          @click="viewCall(call)"
        >
          <!-- Status Indicator -->
          <div class="flex-shrink-0">
            <div class="w-10 h-10 rounded-full flex items-center justify-center"
                 :class="getCallStatusClasses(call.status)">
              <component :is="getCallStatusIcon(call.status)" class="w-5 h-5 text-white" />
            </div>
          </div>

          <!-- Call Details -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center justify-between">
              <p class="text-sm font-medium text-gray-900 truncate">
                {{ formatPhoneNumber(call.from_number) }} → {{ formatPhoneNumber(call.to_number) }}
              </p>
              <span :class="getStatusBadgeClass(call.status)" class="badge text-xs ml-2">
                {{ getStatusText(call.status) }}
              </span>
            </div>
            
            <div class="flex items-center justify-between text-xs text-gray-500 mt-1">
              <span>{{ formatTime(call.created_at) }}</span>
              <div class="flex items-center space-x-2">
                <span v-if="call.duration_ms">
                  {{ formatDuration(call.duration_ms) }}
                </span>
                <span>{{ call.direction }}</span>
              </div>
            </div>
          </div>

          <!-- Arrow Icon -->
          <div class="flex-shrink-0">
            <ChevronRightIcon class="w-4 h-4 text-gray-400" />
          </div>
        </div>
      </div>

      <!-- View All Link -->
      <div class="pt-4 border-t">
        <router-link
          to="/calls"
          class="text-sm text-primary-600 hover:text-primary-700 font-medium flex items-center"
        >
          View all calls
          <ArrowRightIcon class="w-4 h-4 ml-1" />
        </router-link>
      </div>
    </template>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { formatDistanceToNow } from 'date-fns'
import {
  PhoneIcon,
  PhoneArrowUpRightIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ChevronRightIcon,
  ArrowRightIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  calls: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const router = useRouter()

// Methods
const viewCall = (call) => {
  router.push(`/calls/${call.id}`)
}

const formatPhoneNumber = (phone) => {
  if (!phone) return 'Unknown'
  
  // Simple US phone number formatting
  const cleaned = phone.replace(/\D/g, '')
  if (cleaned.length === 11 && cleaned.startsWith('1')) {
    return `+1 (${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7)}`
  } else if (cleaned.length === 10) {
    return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`
  }
  return phone
}

const formatTime = (timestamp) => {
  return formatDistanceToNow(new Date(timestamp), { addSuffix: true })
}

const formatDuration = (ms) => {
  const seconds = Math.floor(ms / 1000)
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  
  if (minutes > 0) {
    return `${minutes}m ${remainingSeconds}s`
  }
  return `${seconds}s`
}

const getCallStatusClasses = (status) => {
  switch (status) {
    case 'ended':
      return 'bg-success-500'
    case 'ongoing':
      return 'bg-primary-500 animate-pulse'
    case 'registered':
      return 'bg-warning-500'
    default:
      return 'bg-gray-500'
  }
}

const getCallStatusIcon = (status) => {
  switch (status) {
    case 'ended':
      return CheckCircleIcon
    case 'ongoing':
      return PhoneIcon
    case 'registered':
      return ClockIcon
    default:
      return XCircleIcon
  }
}

const getStatusBadgeClass = (status) => {
  switch (status) {
    case 'ended':
      return 'badge-success'
    case 'ongoing':
      return 'badge-primary'
    case 'registered':
      return 'badge-warning'
    default:
      return 'badge-gray'
  }
}

const getStatusText = (status) => {
  switch (status) {
    case 'ended':
      return 'Completed'
    case 'ongoing':
      return 'Live'
    case 'registered':
      return 'Connecting'
    default:
      return 'Unknown'
  }
}
</script> 