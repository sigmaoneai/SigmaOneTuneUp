<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
      <!-- Modal Header -->
      <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <div 
            :class="getPriorityClasses(ticket.priority, ticket.status)"
            class="w-10 h-10 rounded-lg flex items-center justify-center"
          >
            <component 
              :is="getPriorityIcon(ticket.priority, ticket.status)" 
              class="w-5 h-5 text-white" 
            />
          </div>
          <div>
            <h3 class="text-lg font-semibold text-gray-900">
              Ticket #{{ ticket.id }} - {{ ticket.subject }}
            </h3>
            <div class="flex items-center space-x-3 mt-1">
              <span :class="getStatusBadge(ticket.status)" class="badge text-xs">
                {{ getStatusText(ticket.status) }}
              </span>
              <span :class="getPriorityBadge(ticket.priority)" class="badge text-xs">
                {{ ticket.priority }} Priority
              </span>
              <span class="text-xs text-gray-500">
                {{ ticket.problem_type }}
              </span>
            </div>
          </div>
        </div>
        <button
          @click="close"
          class="text-gray-400 hover:text-gray-500 transition-colors"
        >
          <XMarkIcon class="w-6 h-6" />
        </button>
      </div>

      <!-- Mock Notice -->
      <div class="px-6 py-3 bg-blue-50 border-b border-blue-200">
        <div class="flex items-center">
          <InformationCircleIcon class="w-5 h-5 text-blue-600 mr-2" />
          <p class="text-sm text-blue-800">
            Mock Data: This ticket information is simulated for testing purposes.
          </p>
        </div>
      </div>

      <!-- Modal Body -->
      <div class="flex flex-1 overflow-hidden">
        <!-- Main Content -->
        <div class="flex-1 overflow-y-auto">
          <div class="p-6 space-y-6">
            <!-- Customer Information -->
            <div class="card">
              <div class="card-header">
                <h4 class="text-md font-medium text-gray-900">Customer Information</h4>
              </div>
              <div class="card-body">
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="text-sm font-medium text-gray-500">Business Name</label>
                    <p class="text-sm text-gray-900 mt-1">{{ getCustomerName() }}</p>
                  </div>
                  <div>
                    <label class="text-sm font-medium text-gray-500">Customer ID</label>
                    <p class="text-sm text-gray-900 mt-1">#{{ ticket.customer_id }}</p>
                  </div>
                  <div>
                    <label class="text-sm font-medium text-gray-500">Contact</label>
                    <p class="text-sm text-gray-900 mt-1">{{ getContactName() }}</p>
                  </div>
                  <div>
                    <label class="text-sm font-medium text-gray-500">Assignee</label>
                    <p class="text-sm text-gray-900 mt-1">{{ ticket.assignee || 'Unassigned' }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Ticket Details -->
            <div class="card">
              <div class="card-header">
                <h4 class="text-md font-medium text-gray-900">Ticket Details</h4>
              </div>
              <div class="card-body">
                <div class="space-y-4">
                  <div>
                    <label class="text-sm font-medium text-gray-500">Description</label>
                    <div class="mt-2 p-3 bg-gray-50 rounded-lg">
                      <p class="text-sm text-gray-900 whitespace-pre-wrap">{{ ticket.description }}</p>
                    </div>
                  </div>
                  
                  <div class="grid grid-cols-3 gap-4">
                    <div>
                      <label class="text-sm font-medium text-gray-500">Created</label>
                      <p class="text-sm text-gray-900 mt-1">{{ formatDateTime(ticket.created_at) }}</p>
                    </div>
                    <div>
                      <label class="text-sm font-medium text-gray-500">Last Updated</label>
                      <p class="text-sm text-gray-900 mt-1">{{ formatDateTime(ticket.updated_at) }}</p>
                    </div>
                    <div v-if="ticket.customer_satisfaction">
                      <label class="text-sm font-medium text-gray-500">Satisfaction</label>
                      <div class="flex items-center mt-1">
                        <div class="flex items-center">
                          <StarIcon 
                            v-for="i in 5" 
                            :key="i"
                            :class="i <= ticket.customer_satisfaction ? 'text-yellow-400' : 'text-gray-300'"
                            class="w-4 h-4"
                          />
                        </div>
                        <span class="text-xs text-gray-500 ml-2">{{ ticket.customer_satisfaction }}/5</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Time Entries (if available) -->
            <div v-if="ticket.time_entries && ticket.time_entries.length > 0" class="card">
              <div class="card-header">
                <h4 class="text-md font-medium text-gray-900">Time Entries</h4>
              </div>
              <div class="card-body p-0">
                <div class="overflow-x-auto">
                  <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                      <tr>
                        <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                        <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Technician</th>
                        <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                        <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Hours</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200">
                      <tr v-for="entry in ticket.time_entries" :key="entry.id">
                        <td class="px-4 py-2 text-sm text-gray-900">{{ entry.date }}</td>
                        <td class="px-4 py-2 text-sm text-gray-900">{{ entry.technician }}</td>
                        <td class="px-4 py-2 text-sm text-gray-900">{{ entry.description }}</td>
                        <td class="px-4 py-2 text-sm text-gray-900">{{ entry.hours }}h</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <!-- Assets (if available) -->
            <div v-if="ticket.assets && ticket.assets.length > 0" class="card">
              <div class="card-header">
                <h4 class="text-md font-medium text-gray-900">Related Assets</h4>
              </div>
              <div class="card-body">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div 
                    v-for="asset in ticket.assets" 
                    :key="asset.id"
                    class="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg"
                  >
                    <div class="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
                      <ComputerDesktopIcon class="w-4 h-4 text-primary-600" />
                    </div>
                    <div>
                      <p class="text-sm font-medium text-gray-900">{{ asset.name }}</p>
                      <p class="text-xs text-gray-500">{{ asset.type }} • {{ asset.location }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Resolution Notes (if available) -->
            <div v-if="ticket.resolution_notes" class="card">
              <div class="card-header">
                <h4 class="text-md font-medium text-gray-900">Resolution Notes</h4>
              </div>
              <div class="card-body">
                <div class="p-3 bg-green-50 rounded-lg border border-green-200">
                  <p class="text-sm text-green-900">{{ ticket.resolution_notes }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Comments Sidebar -->
        <div class="w-80 border-l border-gray-200 bg-gray-50">
          <div class="p-4 border-b border-gray-200 bg-white">
            <h4 class="text-md font-medium text-gray-900">Comments</h4>
            <p class="text-xs text-gray-500 mt-1">
              {{ (ticket.comments || []).length }} comment{{ (ticket.comments || []).length !== 1 ? 's' : '' }}
            </p>
          </div>
          
          <div class="flex-1 overflow-y-auto p-4">
            <!-- Comments List -->
            <div class="space-y-4">
              <div 
                v-for="comment in (ticket.comments || [])" 
                :key="comment.id"
                class="bg-white rounded-lg p-3 shadow-sm"
              >
                <div class="flex items-center justify-between mb-2">
                  <span class="text-sm font-medium text-gray-900">{{ comment.author }}</span>
                  <span class="text-xs text-gray-500">{{ formatTime(comment.created_at) }}</span>
                </div>
                <p class="text-sm text-gray-700">{{ comment.comment }}</p>
                <div v-if="comment.hidden" class="mt-2">
                  <span class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-yellow-100 text-yellow-800">
                    <EyeSlashIcon class="w-3 h-3 mr-1" />
                    Hidden
                  </span>
                </div>
                <div v-if="comment.mock_added" class="mt-2">
                  <span class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800">
                    Mock Comment
                  </span>
                </div>
              </div>

              <!-- No Comments -->
              <div v-if="!(ticket.comments || []).length" class="text-center py-8">
                <ChatBubbleLeftIcon class="w-12 h-12 text-gray-300 mx-auto mb-2" />
                <p class="text-sm text-gray-500">No comments yet</p>
              </div>
            </div>

            <!-- Add Comment Form -->
            <div class="mt-6 bg-white rounded-lg p-4 shadow-sm">
              <h5 class="text-sm font-medium text-gray-900 mb-3">Add Comment</h5>
              <div class="space-y-3">
                <textarea
                  v-model="newComment"
                  rows="3"
                  placeholder="Enter your comment..."
                  class="form-textarea text-sm"
                ></textarea>
                <div class="flex items-center justify-between">
                  <label class="flex items-center">
                    <input
                      v-model="commentHidden"
                      type="checkbox"
                      class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    />
                    <span class="ml-2 text-xs text-gray-600">Hidden comment</span>
                  </label>
                  <button
                    @click="addComment"
                    :disabled="!newComment.trim() || addingComment"
                    class="btn-primary btn-sm"
                  >
                    <span v-if="addingComment">Adding...</span>
                    <span v-else>Add Comment</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <span class="text-sm text-gray-500">
            Last updated {{ formatTime(ticket.updated_at) }}
          </span>
          <div v-if="ticket.mock_data" class="flex items-center text-xs text-blue-600">
            <InformationCircleIcon class="w-3 h-3 mr-1" />
            Mock Data
          </div>
        </div>
        <div class="flex items-center space-x-3">
          <button
            @click="close"
            class="btn-secondary"
          >
            Close
          </button>
          <button
            @click="refreshTicket"
            :disabled="refreshing"
            class="btn-primary"
          >
            <ArrowPathIcon 
              :class="['w-4 h-4 mr-2', refreshing ? 'animate-spin' : '']" 
            />
            Refresh
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useToast } from 'vue-toastification'
import { formatDistanceToNow, format } from 'date-fns'
import api from '@/services/api'
import {
  XMarkIcon,
  InformationCircleIcon,
  StarIcon,
  ComputerDesktopIcon,
  ChatBubbleLeftIcon,
  EyeSlashIcon,
  ArrowPathIcon,
  ExclamationTriangleIcon,
  ExclamationCircleIcon,
  CheckCircleIcon,
  ClockIcon,
  TicketIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  ticket: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'ticket-updated'])
const toast = useToast()

// Reactive state
const refreshing = ref(false)
const addingComment = ref(false)
const newComment = ref('')
const commentHidden = ref(false)

// Methods
const close = () => {
  emit('close')
}

const refreshTicket = async () => {
  refreshing.value = true
  try {
    // In a real app, this would fetch fresh ticket data
    await new Promise(resolve => setTimeout(resolve, 1000))
    toast.success('Ticket refreshed (mock)')
    emit('ticket-updated', props.ticket.id)
  } catch (error) {
    toast.error('Failed to refresh ticket')
  } finally {
    refreshing.value = false
  }
}

const addComment = async () => {
  if (!newComment.value.trim()) return

  addingComment.value = true
  try {
    const commentData = {
      comment: newComment.value.trim(),
      hidden: commentHidden.value
    }

    const response = await api.syncro.addTicketComment(props.ticket.id, commentData)
    
    // Add the comment to the local ticket data
    if (!props.ticket.comments) {
      props.ticket.comments = []
    }
    props.ticket.comments.push(response.data.comment)

    toast.success('Mock comment added successfully')
    newComment.value = ''
    commentHidden.value = false
    emit('ticket-updated', props.ticket.id)
  } catch (error) {
    toast.error('Failed to add comment')
  } finally {
    addingComment.value = false
  }
}

// Utility methods
const getCustomerName = () => {
  const parts = props.ticket.customer_business_then_name.split(' - ')
  return parts[0] || 'Unknown Customer'
}

const getContactName = () => {
  const parts = props.ticket.customer_business_then_name.split(' - ')
  return parts[1] || 'Unknown Contact'
}

const formatTime = (timestamp) => {
  return formatDistanceToNow(new Date(timestamp), { addSuffix: true })
}

const formatDateTime = (timestamp) => {
  return format(new Date(timestamp), 'MMM d, yyyy h:mm a')
}

const getPriorityClasses = (priority, status) => {
  if (status === 'urgent') return 'bg-red-500'
  
  switch (priority) {
    case 'critical': return 'bg-red-500'
    case 'high': return 'bg-orange-500'
    case 'medium': return 'bg-yellow-500'
    case 'low': return 'bg-green-500'
    default: return 'bg-gray-500'
  }
}

const getPriorityIcon = (priority, status) => {
  if (status === 'urgent') return ExclamationTriangleIcon
  if (status === 'completed') return CheckCircleIcon
  
  switch (priority) {
    case 'critical':
    case 'high':
      return ExclamationCircleIcon
    case 'medium':
      return ClockIcon
    case 'low':
      return CheckCircleIcon
    default:
      return TicketIcon
  }
}

const getStatusBadge = (status) => {
  switch (status) {
    case 'open': return 'badge-warning'
    case 'in_progress': return 'badge-primary'
    case 'completed': return 'badge-success'
    case 'urgent': return 'badge-danger'
    default: return 'badge-gray'
  }
}

const getStatusText = (status) => {
  switch (status) {
    case 'open': return 'Open'
    case 'in_progress': return 'In Progress'
    case 'completed': return 'Completed'
    case 'urgent': return 'Urgent'
    default: return status
  }
}

const getPriorityBadge = (priority) => {
  switch (priority) {
    case 'critical': return 'badge-danger'
    case 'high': return 'badge-warning'
    case 'medium': return 'badge-primary'
    case 'low': return 'badge-success'
    default: return 'badge-gray'
  }
}
</script> 