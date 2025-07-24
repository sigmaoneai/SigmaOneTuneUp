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
          <UserGroupIcon class="w-12 h-12 text-gray-400 mx-auto mb-2" />
          <p class="text-gray-500">No agent performance data</p>
        </div>
      </div>
    </template>
    
    <template v-else>
      <Bar
        :data="chartData"
        :options="chartOptions"
        class="h-full"
      />
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import { UserGroupIcon } from '@heroicons/vue/24/outline'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

const props = defineProps({
  data: {
    type: Object,
    default: () => ({
      agent_performance: []
    })
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// Computed properties
const hasData = computed(() => {
  return props.data.agent_performance && props.data.agent_performance.length > 0
})

const chartData = computed(() => {
  if (!hasData.value) return { labels: [], datasets: [] }
  
  const agents = props.data.agent_performance.slice(0, 10) // Top 10 agents
  const labels = agents.map(agent => agent.name.length > 15 
    ? agent.name.substring(0, 15) + '...' 
    : agent.name
  )
  
  const callCounts = agents.map(agent => agent.total_calls)
  const successRates = agents.map(agent => agent.success_rate_percent)
  
  return {
    labels,
    datasets: [
      {
        label: 'Total Calls',
        data: callCounts,
        backgroundColor: 'rgba(59, 130, 246, 0.8)', // primary-500
        borderColor: 'rgb(59, 130, 246)',
        borderWidth: 1,
        yAxisID: 'y'
      },
      {
        label: 'Success Rate (%)',
        data: successRates,
        backgroundColor: 'rgba(34, 197, 94, 0.8)', // success-500
        borderColor: 'rgb(34, 197, 94)',
        borderWidth: 1,
        yAxisID: 'y1'
      }
    ]
  }
})

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index',
    intersect: false,
  },
  plugins: {
    legend: {
      position: 'top',
      labels: {
        usePointStyle: true,
        padding: 20
      }
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleColor: 'white',
      bodyColor: 'white',
      borderColor: 'rgb(59, 130, 246)',
      borderWidth: 1,
      cornerRadius: 8,
      callbacks: {
        afterLabel: function(context) {
          const index = context.dataIndex
          const agent = props.data.agent_performance[index]
          if (!agent) return ''
          
          return [
            `Completed: ${agent.completed_calls}`,
            `Avg Duration: ${Math.round(agent.average_duration_seconds / 60)}m`,
            `Total Time: ${agent.total_duration_minutes}m`
          ]
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
        color: 'rgb(107, 114, 128)',
        maxRotation: 45
      }
    },
    y: {
      type: 'linear',
      display: true,
      position: 'left',
      beginAtZero: true,
      grid: {
        color: 'rgba(0, 0, 0, 0.05)'
      },
      ticks: {
        color: 'rgb(107, 114, 128)',
        precision: 0
      },
      title: {
        display: true,
        text: 'Total Calls',
        color: 'rgb(59, 130, 246)'
      }
    },
    y1: {
      type: 'linear',
      display: true,
      position: 'right',
      beginAtZero: true,
      max: 100,
      grid: {
        drawOnChartArea: false,
      },
      ticks: {
        color: 'rgb(34, 197, 94)',
        callback: function(value) {
          return value + '%'
        }
      },
      title: {
        display: true,
        text: 'Success Rate (%)',
        color: 'rgb(34, 197, 94)'
      }
    }
  }
}))
</script> 