<template>
  <div class="h-64">
    <template v-if="loading">
      <div class="flex items-center justify-center h-full">
        <div class="animate-pulse">
          <div class="h-4 bg-gray-200 rounded w-32 mb-2 mx-auto"></div>
          <div class="h-32 bg-gray-100 rounded"></div>
        </div>
      </div>
    </template>
    
    <template v-else-if="!hasData">
      <div class="flex items-center justify-center h-full">
        <div class="text-center">
          <ChartBarIcon class="w-12 h-12 text-gray-400 mx-auto mb-2" />
          <p class="text-gray-500">No call data available</p>
        </div>
      </div>
    </template>
    
    <template v-else>
      <Line
        :data="chartData"
        :options="chartOptions"
        class="h-full"
      />
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import { format } from 'date-fns'
import { ChartBarIcon } from '@heroicons/vue/24/outline'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const props = defineProps({
  data: {
    type: Object,
    default: () => ({
      hourly_activity: [],
      total_calls: 0
    })
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// Computed properties
const hasData = computed(() => {
  return props.data.hourly_activity && props.data.hourly_activity.length > 0
})

const chartData = computed(() => {
  if (!hasData.value) return { labels: [], datasets: [] }
  
  const labels = props.data.hourly_activity.map(item => {
    return format(new Date(item.hour), 'HH:mm')
  })
  
  const data = props.data.hourly_activity.map(item => item.count)
  
  return {
    labels,
    datasets: [
      {
        label: 'Calls per Hour',
        data,
        borderColor: 'rgb(59, 130, 246)', // primary-500
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.3,
        pointRadius: 4,
        pointHoverRadius: 6,
        pointBackgroundColor: 'rgb(59, 130, 246)',
        pointBorderColor: 'white',
        pointBorderWidth: 2
      }
    ]
  }
})

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    intersect: false,
    mode: 'index'
  },
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleColor: 'white',
      bodyColor: 'white',
      borderColor: 'rgb(59, 130, 246)',
      borderWidth: 1,
      cornerRadius: 8,
      displayColors: false,
      callbacks: {
        title: function(context) {
          const index = context[0].dataIndex
          const hour = props.data.hourly_activity[index]?.hour
          return hour ? format(new Date(hour), 'MMM d, HH:mm') : ''
        },
        label: function(context) {
          const count = context.parsed.y
          return `${count} call${count !== 1 ? 's' : ''}`
        }
      }
    }
  },
  scales: {
    x: {
      grid: {
        color: 'rgba(0, 0, 0, 0.05)'
      },
      ticks: {
        color: 'rgb(107, 114, 128)' // gray-500
      }
    },
    y: {
      beginAtZero: true,
      grid: {
        color: 'rgba(0, 0, 0, 0.05)'
      },
      ticks: {
        color: 'rgb(107, 114, 128)', // gray-500
        precision: 0
      }
    }
  }
}))
</script> 