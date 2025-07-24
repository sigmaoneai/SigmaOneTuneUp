<template>
  <div id="app">
    <!-- Loading Screen -->
    <div v-if="loading" class="fixed inset-0 bg-white z-50 flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
        <h2 class="text-xl font-semibold text-gray-900">Loading SigmaOne TuneUp</h2>
        <p class="text-gray-600">Initializing voice AI management platform...</p>
      </div>
    </div>

    <!-- Main App -->
    <div v-else class="min-h-screen bg-gray-50">
      <!-- Navigation -->
      <AppNavigation />
      
      <!-- Main Content -->
      <main class="lg:pl-64">
        <div class="py-6">
          <router-view :key="$route.fullPath" />
        </div>
      </main>
      
      <!-- Status Bar -->
      <StatusBar />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import AppNavigation from '@/components/layout/AppNavigation.vue'
import StatusBar from '@/components/layout/StatusBar.vue'

const loading = ref(true)
const appStore = useAppStore()

onMounted(async () => {
  try {
    // Initialize the application
    await appStore.initialize()
    
    // Add a small delay to show the loading screen
    setTimeout(() => {
      loading.value = false
    }, 1000)
  } catch (error) {
    console.error('Failed to initialize app:', error)
    loading.value = false
  }
})
</script>

<style>
#app {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style> 