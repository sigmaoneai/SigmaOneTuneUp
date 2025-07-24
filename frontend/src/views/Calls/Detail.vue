<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Call Details</h1>
          <p class="mt-2 text-gray-600">View detailed call information and transcript</p>
        </div>
        <router-link to="/calls" class="btn-secondary">
          <ArrowLeftIcon class="w-4 h-4 mr-2" />
          Back to Calls
        </router-link>
      </div>
    </div>

    <!-- Call Information -->
    <div class="space-y-8">
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-medium text-gray-900">Call Information</h3>
          <p class="text-sm text-gray-500">Basic call details and metadata</p>
        </div>
        <div class="card-body">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-500">Call ID</label>
              <p class="text-sm text-gray-900 mt-1">{{ callId || 'Loading...' }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-500">Status</label>
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 mt-1">
                Completed
              </span>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-500">Duration</label>
              <p class="text-sm text-gray-900 mt-1">5m 23s</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-500">Direction</label>
              <p class="text-sm text-gray-900 mt-1">Inbound</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-500">Phone Number</label>
              <p class="text-sm text-gray-900 mt-1">+1 (555) 123-4567</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-500">Agent</label>
              <p class="text-sm text-gray-900 mt-1">Customer Service Agent</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Transcript Placeholder -->
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-medium text-gray-900">Call Transcript</h3>
          <p class="text-sm text-gray-500">Full conversation transcript with timestamps</p>
        </div>
        <div class="card-body">
          <div class="text-center py-12">
            <ChatBubbleLeftRightIcon class="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p class="text-gray-500">Call transcript will be displayed here</p>
            <p class="text-sm text-gray-400 mt-2">Transcript data will be available once the call is processed</p>
          </div>
        </div>
      </div>

      <!-- Analytics Placeholder -->
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-medium text-gray-900">Call Analytics</h3>
          <p class="text-sm text-gray-500">Sentiment analysis and performance metrics</p>
        </div>
        <div class="card-body">
          <div class="text-center py-12">
            <ChartBarIcon class="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p class="text-gray-500">Call analytics will be displayed here</p>
            <p class="text-sm text-gray-400 mt-2">Analytics data will be available once the call is analyzed</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { 
  ArrowLeftIcon, 
  ChatBubbleLeftRightIcon, 
  ChartBarIcon 
} from '@heroicons/vue/24/outline'

const route = useRoute()
const callId = ref(null)

onMounted(() => {
  callId.value = route.params.id
})
</script> 