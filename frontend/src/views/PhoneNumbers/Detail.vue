<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Phone Number Details</h1>
          <p class="mt-2 text-gray-600">View and manage phone number configuration</p>
        </div>
        <router-link to="/phone-numbers" class="btn-secondary">
          <ArrowLeftIcon class="w-4 h-4 mr-2" />
          Back to Phone Numbers
        </router-link>
      </div>
    </div>

    <!-- Phone Number Information -->
    <div class="space-y-8">
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-medium text-gray-900">Phone Number Information</h3>
          <p class="text-sm text-gray-500">Basic phone number configuration and status</p>
        </div>
        <div class="card-body">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-500">Phone Number</label>
              <p class="text-sm text-gray-900 mt-1">{{ phoneNumberId || 'Loading...' }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-500">Status</label>
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 mt-1">
                Active
              </span>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-500">Provider</label>
              <p class="text-sm text-gray-900 mt-1">RetellAI</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-500">Type</label>
              <p class="text-sm text-gray-900 mt-1">Inbound/Outbound</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Configuration Placeholder -->
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-medium text-gray-900">Configuration</h3>
          <p class="text-sm text-gray-500">Phone number routing and behavior settings</p>
        </div>
        <div class="card-body">
          <div class="text-center py-12">
            <PhoneIcon class="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p class="text-gray-500">Phone number configuration details will be displayed here</p>
            <p class="text-sm text-gray-400 mt-2">Connect to RetellAI API to view detailed settings</p>
          </div>
        </div>
      </div>

      <!-- Call History Placeholder -->
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-medium text-gray-900">Recent Calls</h3>
          <p class="text-sm text-gray-500">Latest calls using this phone number</p>
        </div>
        <div class="card-body">
          <div class="text-center py-12">
            <ClockIcon class="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p class="text-gray-500">Recent calls will be displayed here</p>
            <p class="text-sm text-gray-400 mt-2">Call history will be available once calls are processed</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeftIcon, PhoneIcon, ClockIcon } from '@heroicons/vue/24/outline'

const route = useRoute()
const phoneNumberId = ref(null)

onMounted(() => {
  phoneNumberId.value = route.params.id
})
</script> 