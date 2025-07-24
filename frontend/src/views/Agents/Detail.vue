<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Agent Details</h1>
          <p class="mt-2 text-gray-600">View and manage RetellAI agent configuration</p>
        </div>
        <router-link to="/agents" class="btn-secondary">
          <ArrowLeftIcon class="w-4 h-4 mr-2" />
          Back to Agents
        </router-link>
      </div>
    </div>

    <!-- Agent Information -->
    <div class="space-y-8">
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-medium text-gray-900">Agent Information</h3>
          <p class="text-sm text-gray-500">Basic agent configuration and status</p>
        </div>
        <div class="card-body">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-500">Agent ID</label>
              <p class="text-sm text-gray-900 mt-1">{{ agentId || 'Loading...' }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-500">Status</label>
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 mt-1">
                Active
              </span>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-500">Agent Name</label>
              <p class="text-sm text-gray-900 mt-1">Customer Service Agent</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-500">Language</label>
              <p class="text-sm text-gray-900 mt-1">English (US)</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Configuration Placeholder -->
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-medium text-gray-900">Configuration</h3>
          <p class="text-sm text-gray-500">Agent behavior and response settings</p>
        </div>
        <div class="card-body">
          <div class="text-center py-12">
            <CogIcon class="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p class="text-gray-500">Agent configuration details will be displayed here</p>
            <p class="text-sm text-gray-400 mt-2">Connect to RetellAI API to view detailed settings</p>
          </div>
        </div>
      </div>

      <!-- Recent Activity Placeholder -->
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-medium text-gray-900">Recent Activity</h3>
          <p class="text-sm text-gray-500">Latest agent interactions and performance</p>
        </div>
        <div class="card-body">
          <div class="text-center py-12">
            <ClockIcon class="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p class="text-gray-500">Recent activity will be displayed here</p>
            <p class="text-sm text-gray-400 mt-2">Activity data will be available once calls are processed</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeftIcon, CogIcon, ClockIcon } from '@heroicons/vue/24/outline'

const route = useRoute()
const agentId = ref(null)

onMounted(() => {
  agentId.value = route.params.id
})
</script> 