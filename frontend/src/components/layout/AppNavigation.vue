<template>
  <div class="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg lg:block">
    <!-- Logo and header -->
    <div class="flex h-16 items-center justify-between px-4 border-b border-gray-200">
      <div class="flex items-center">
        <div class="flex-shrink-0">
          <div class="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
            <span class="text-white font-bold text-lg">Σ</span>
          </div>
        </div>
        <div class="ml-3">
          <h1 class="text-lg font-semibold text-gray-900">SigmaOne</h1>
          <p class="text-xs text-gray-500">TuneUp</p>
        </div>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="mt-4 px-3 space-y-1">
      <!-- Dashboard -->
      <router-link 
        to="/" 
        class="nav-link"
        :class="{ 'nav-link-active': $route.name === 'Dashboard' }"
      >
        <ChartBarIcon class="nav-icon" />
        Dashboard
      </router-link>

      <!-- Agents -->
      <router-link 
        to="/agents" 
        class="nav-link"
        :class="{ 'nav-link-active': $route.path.startsWith('/agents') }"
      >
        <UserGroupIcon class="nav-icon" />
        Voice Agents
        <span class="ml-auto badge badge-primary">{{ agentCount }}</span>
      </router-link>

      <!-- Phone Numbers -->
      <router-link 
        to="/phone-numbers" 
        class="nav-link"
        :class="{ 'nav-link-active': $route.name === 'PhoneNumbers' }"
      >
        <PhoneIcon class="nav-icon" />
        Phone Numbers
        <span class="ml-auto badge badge-gray">{{ phoneNumberCount }}</span>
      </router-link>

      <!-- Calls -->
      <router-link 
        to="/calls" 
        class="nav-link"
        :class="{ 'nav-link-active': $route.path.startsWith('/calls') }"
      >
        <PhoneArrowUpRightIcon class="nav-icon" />
        Call History
        <span v-if="activeCalls > 0" class="ml-auto badge badge-success animate-pulse">
          {{ activeCalls }} live
        </span>
      </router-link>

      <!-- Prompts -->
      <router-link 
        to="/prompts" 
        class="nav-link"
        :class="{ 'nav-link-active': $route.path.startsWith('/prompts') }"
      >
        <DocumentTextIcon class="nav-icon" />
        Prompt Library
      </router-link>

      <!-- Onboarding -->
      <router-link 
        to="/onboarding" 
        class="nav-link"
        :class="{ 'nav-link-active': $route.name === 'Onboarding' }"
      >
        <AcademicCapIcon class="nav-icon" />
        Onboarding
        <div class="ml-auto">
          <span class="badge badge-green text-xs">NEW</span>
        </div>
      </router-link>

      <!-- MSP Solution -->
      <router-link 
        to="/syncromsp" 
        class="nav-link"
        :class="{ 'nav-link-active': $route.name === 'SyncroMSP' }"
      >
        <BuildingOffice2Icon class="nav-icon" />
        MSP Solution
        <div class="ml-auto flex items-center">
          <div :class="syncroStatus" class="status-dot"></div>
        </div>
      </router-link>

      <!-- Knowledge Base -->
      <router-link 
        to="/knowledge-base" 
        class="nav-link"
        :class="{ 'nav-link-active': $route.name === 'KnowledgeBase' }"
      >
        <BookOpenIcon class="nav-icon" />
        Knowledge Base
        <div class="ml-auto">
          <span class="badge badge-green text-xs">ITGlue</span>
        </div>
      </router-link>

      <!-- E2E Tuning -->
      <router-link 
        to="/e2e-tuning" 
        class="nav-link"
        :class="{ 'nav-link-active': $route.name === 'E2ETuning' }"
      >
        <WrenchScrewdriverIcon class="nav-icon" />
        E2E Tuning
        <div class="ml-auto">
          <span class="badge badge-blue text-xs">DEV</span>
        </div>
      </router-link>

      <div class="border-t border-gray-200 my-4"></div>

      <!-- Settings -->
      <router-link 
        to="/settings" 
        class="nav-link"
        :class="{ 'nav-link-active': $route.name === 'Settings' }"
      >
        <CogIcon class="nav-icon" />
        Settings
      </router-link>
    </nav>

    <!-- System Status -->
    <div class="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 bg-gray-50">
      <div class="flex items-center justify-between text-sm">
        <span class="text-gray-600">System Status</span>
        <div class="flex items-center space-x-1">
          <div :class="overallHealthStatus" class="status-dot"></div>
          <span :class="overallHealthTextColor" class="text-xs font-medium">
            {{ overallHealthText }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAppStore } from '@/stores/app'
import {
  ChartBarIcon,
  UserGroupIcon,
  PhoneIcon,
  PhoneArrowUpRightIcon,
  DocumentTextIcon,
  BuildingOffice2Icon,
  CogIcon,
  WrenchScrewdriverIcon,
  AcademicCapIcon,
  BookOpenIcon
} from '@heroicons/vue/24/outline'

const appStore = useAppStore()

// Computed properties for navigation badges
const agentCount = computed(() => appStore.stats.total_agents || 0)
const phoneNumberCount = computed(() => appStore.stats.total_phone_numbers || 0)
const activeCalls = computed(() => appStore.stats.active_calls || 0)

// System health status
const syncroStatus = computed(() => {
  const status = appStore.systemHealth.syncro_msp
  switch (status) {
    case 'healthy': return 'status-online'
    case 'unhealthy': return 'status-error'
    default: return 'status-offline'
  }
})

const overallHealthStatus = computed(() => {
  const status = appStore.systemHealth.overall
  switch (status) {
    case 'healthy': return 'status-online'
    case 'degraded': return 'status-busy'
    case 'unhealthy': return 'status-error'
    default: return 'status-offline'
  }
})

const overallHealthText = computed(() => {
  const status = appStore.systemHealth.overall
  switch (status) {
    case 'healthy': return 'All Systems Healthy'
    case 'degraded': return 'Some Issues'
    case 'unhealthy': return 'System Issues'
    default: return 'Checking...'
  }
})

const overallHealthTextColor = computed(() => {
  const status = appStore.systemHealth.overall
  switch (status) {
    case 'healthy': return 'text-success-600'
    case 'degraded': return 'text-warning-600'
    case 'unhealthy': return 'text-danger-600'
    default: return 'text-gray-500'
  }
})
</script>

<style scoped>
.nav-link {
  @apply flex items-center px-3 py-2 text-sm font-medium text-gray-700 rounded-md hover:text-gray-900 hover:bg-gray-100 transition-colors duration-150;
}

.nav-link-active {
  @apply bg-primary-50 text-primary-700 border-r-2 border-primary-600;
}

.nav-icon {
  @apply w-5 h-5 mr-3 flex-shrink-0;
}
</style> 