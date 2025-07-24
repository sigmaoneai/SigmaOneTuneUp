<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Page Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900">Dashboard</h1>
      <p class="mt-2 text-gray-600">Voice AI management and observability overview</p>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <StatsCard
        title="Voice Agents"
        :value="stats.total_agents"
        icon="UserGroupIcon"
        color="primary"
        :loading="loading"
      >
        <template #subtitle>
          {{ activeAgentsCount }} active
        </template>
      </StatsCard>

      <StatsCard
        title="Phone Numbers"
        :value="stats.total_phone_numbers"
        icon="PhoneIcon"
        color="success"
        :loading="loading"
      >
        <template #subtitle>
          {{ assignedPhoneNumbers }} assigned
        </template>
      </StatsCard>

      <StatsCard
        title="Calls Today"
        :value="stats.total_calls_today"
        icon="PhoneArrowUpRightIcon"
        color="warning"
        :loading="loading"
      >
        <template #subtitle>
          {{ callsSuccessRate }}% success rate
        </template>
      </StatsCard>

      <StatsCard
        title="Active Calls"
        :value="stats.active_calls"
        icon="SignalIcon"
        color="danger"
        :loading="loading"
        :pulse="stats.active_calls > 0"
      >
        <template #subtitle>
          Live conversations
        </template>
      </StatsCard>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
      <!-- System Health -->
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-medium text-gray-900">System Health</h3>
          <p class="text-sm text-gray-500">Real-time status of all integrations</p>
        </div>
        <div class="card-body">
          <SystemHealth :health="systemHealth" :loading="loading" />
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-medium text-gray-900">Recent Calls</h3>
          <p class="text-sm text-gray-500">Latest voice AI interactions</p>
        </div>
        <div class="card-body">
          <RecentCalls :calls="recentCalls" :loading="loading" />
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
      <!-- Call Activity Chart -->
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-medium text-gray-900">Call Activity</h3>
          <p class="text-sm text-gray-500">Last 24 hours</p>
        </div>
        <div class="card-body">
          <CallActivityChart :data="callActivity" :loading="loading" />
        </div>
      </div>

      <!-- Agent Performance -->
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-medium text-gray-900">Agent Performance</h3>
          <p class="text-sm text-gray-500">Success rates and call volumes</p>
        </div>
        <div class="card-body">
          <AgentPerformanceChart :data="agentPerformance" :loading="loading" />
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="card">
      <div class="card-header">
        <h3 class="text-lg font-medium text-gray-900">Quick Actions</h3>
        <p class="text-sm text-gray-500">Common tasks and shortcuts</p>
      </div>
      <div class="card-body">
        <QuickActions />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAppStore } from '@/stores/app'
import api from '@/services/api'

// Components
import StatsCard from '@/components/dashboard/StatsCard.vue'
import SystemHealth from '@/components/dashboard/SystemHealth.vue'
import RecentCalls from '@/components/dashboard/RecentCalls.vue'
import CallActivityChart from '@/components/dashboard/CallActivityChart.vue'
import AgentPerformanceChart from '@/components/dashboard/AgentPerformanceChart.vue'
import QuickActions from '@/components/dashboard/QuickActions.vue'

// Reactive data
const loading = ref(true)
const stats = ref({
  total_agents: 0,
  total_phone_numbers: 0,
  total_calls_today: 0,
  active_calls: 0
})
const systemHealth = ref({})
const recentCalls = ref([])
const callActivity = ref([])
const agentPerformance = ref([])
const callsSuccessRate = ref(0)

const appStore = useAppStore()

// Computed properties
const activeAgentsCount = computed(() => {
  // This would be calculated from agents data
  return Math.floor(stats.value.total_agents * 0.8) // Placeholder
})

const assignedPhoneNumbers = computed(() => {
  // This would be calculated from phone numbers data
  return Math.floor(stats.value.total_phone_numbers * 0.6) // Placeholder
})

// Methods
async function loadDashboardData() {
  loading.value = true
  try {
    const [
      statsResponse,
      healthResponse,
      callActivityResponse,
      agentPerformanceResponse
    ] = await Promise.all([
      api.dashboard.getStats(),
      api.dashboard.healthCheck(),
      api.dashboard.getCallActivity(24),
      api.dashboard.getAgentPerformance(7)
    ])

    stats.value = statsResponse.data
    systemHealth.value = healthResponse.data
    callActivity.value = callActivityResponse.data
    agentPerformance.value = agentPerformanceResponse.data

    // Load recent calls
    const callsResponse = await api.calls.list({ limit: 5 })
    recentCalls.value = callsResponse.data

    // Calculate success rate
    const todayStatsResponse = await api.calls.getTodayStats()
    callsSuccessRate.value = todayStatsResponse.data.success_rate || 0

  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  } finally {
    loading.value = false
  }
}

// Auto-refresh dashboard
let refreshInterval = null

onMounted(() => {
  loadDashboardData()
  
  // Refresh every 30 seconds
  refreshInterval = setInterval(loadDashboardData, 30000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script> 