<template>
  <div class="card hover:shadow-card-hover transition-shadow duration-200">
    <div class="card-body">
      <div class="flex items-center">
        <div class="flex-shrink-0">
          <div 
            :class="iconClasses"
            class="w-8 h-8 rounded-md flex items-center justify-center"
          >
            <component :is="iconComponent" class="w-5 h-5 text-white" />
          </div>
        </div>
        
        <div class="ml-5 w-0 flex-1">
          <dl>
            <dt class="text-sm font-medium text-gray-500 truncate">
              {{ title }}
            </dt>
            <dd class="flex items-baseline">
              <div 
                :class="[
                  'text-2xl font-semibold',
                  pulse ? 'animate-pulse-soft' : '',
                  loading ? 'text-gray-400' : 'text-gray-900'
                ]"
              >
                <template v-if="loading">
                  <div class="h-8 w-16 bg-gray-200 rounded animate-pulse"></div>
                </template>
                <template v-else>
                  {{ formattedValue }}
                </template>
              </div>
            </dd>
            
            <!-- Subtitle slot -->
            <div v-if="$slots.subtitle || loading" class="mt-1">
              <template v-if="loading">
                <div class="h-4 w-24 bg-gray-100 rounded animate-pulse"></div>
              </template>
              <template v-else>
                <p class="text-sm text-gray-600">
                  <slot name="subtitle" />
                </p>
              </template>
            </div>
          </dl>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  UserGroupIcon,
  PhoneIcon,
  PhoneArrowUpRightIcon,
  SignalIcon,
  ChartBarIcon,
  ClockIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [Number, String],
    default: 0
  },
  icon: {
    type: String,
    default: 'ChartBarIcon'
  },
  color: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'success', 'warning', 'danger'].includes(value)
  },
  loading: {
    type: Boolean,
    default: false
  },
  pulse: {
    type: Boolean,
    default: false
  }
})

// Icon mapping
const iconMap = {
  UserGroupIcon,
  PhoneIcon,
  PhoneArrowUpRightIcon,
  SignalIcon,
  ChartBarIcon,
  ClockIcon
}

const iconComponent = computed(() => {
  return iconMap[props.icon] || ChartBarIcon
})

const iconClasses = computed(() => {
  const colorClasses = {
    primary: 'bg-primary-500',
    success: 'bg-success-500',
    warning: 'bg-warning-500',
    danger: 'bg-danger-500'
  }
  return colorClasses[props.color] || colorClasses.primary
})

const formattedValue = computed(() => {
  if (typeof props.value === 'number') {
    return props.value.toLocaleString()
  }
  return props.value
})
</script> 