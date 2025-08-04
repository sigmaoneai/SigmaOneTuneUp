<template>
  <div class="card">
    <div class="card-header">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-medium text-gray-900">Test Scenarios</h3>
        <div class="flex items-center space-x-2">
          <button @click="$emit('load-defaults')" class="btn-sm btn-secondary">
            Load Defaults
          </button>
          <button @click="$emit('add-test')" class="btn-sm btn-primary">
            <PlusIcon class="w-3 h-3 mr-1" />
            Add Test
          </button>
        </div>
      </div>
    </div>
    <div class="card-body p-0">
      <div v-if="testScenarios.length === 0" class="text-center py-12">
        <ClipboardDocumentListIcon class="w-12 h-12 text-gray-300 mx-auto mb-4" />
        <p class="text-gray-500">No test scenarios yet</p>
        <button @click="$emit('load-defaults')" class="btn-primary btn-sm mt-4">
          Load Default Tests
        </button>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Test
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Category
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Last Tested
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Notes
              </th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="test in testScenarios" :key="test.id" class="hover:bg-gray-50">
              <td class="px-6 py-4">
                <div>
                  <div class="text-sm font-medium text-gray-900">{{ test.name }}</div>
                  <div class="text-sm text-gray-500">{{ test.description }}</div>
                </div>
              </td>
              <td class="px-6 py-4">
                <span :class="getCategoryBadge(test.category)" class="badge text-xs">
                  {{ test.category }}
                </span>
              </td>
              <td class="px-6 py-4">
                <select 
                  :value="test.status"
                  @change="$emit('update-test-status', test.id, $event.target.value)"
                  :class="getStatusBadge(test.status)"
                  class="text-xs rounded border-0 py-1 px-2 font-medium"
                >
                  <option value="not_started">Not Started</option>
                  <option value="in_progress">In Progress</option>
                  <option value="passed">Passed</option>
                  <option value="failed">Failed</option>
                </select>
              </td>
              <td class="px-6 py-4 text-sm text-gray-500">
                {{ test.lastTested ? formatDate(test.lastTested) : 'Never' }}
              </td>
              <td class="px-6 py-4">
                <div 
                  v-if="!editingNotes || editingNotes.id !== test.id"
                  @click="startEditingNotes(test)"
                  class="text-sm text-gray-900 max-w-xs truncate cursor-pointer hover:bg-gray-50 p-1 rounded"
                  :title="test.notes || 'Click to add notes'"
                >
                  {{ test.notes || 'No notes' }}
                </div>
                <div v-else class="max-w-xs">
                  <textarea
                    v-model="notesEditValue"
                    @blur="saveNotes(test)"
                    @keydown.enter.prevent="saveNotes(test)"
                    @keydown.esc="cancelEditingNotes"
                    class="w-full text-xs border rounded p-1 resize-none"
                    rows="2"
                    ref="notesInput"
                  ></textarea>
                </div>
              </td>
              <td class="px-6 py-4 text-right text-sm font-medium">
                <div class="flex items-center justify-end space-x-2">
                  <button 
                    @click="$emit('run-test', test)"
                    :disabled="!currentCall"
                    class="text-blue-600 hover:text-blue-900 disabled:text-gray-400"
                    title="Run test with current call"
                  >
                    <PlayIcon class="w-4 h-4" />
                  </button>
                  <button 
                    @click="$emit('edit-test', test)"
                    class="text-primary-600 hover:text-primary-900"
                  >
                    <PencilIcon class="w-4 h-4" />
                  </button>
                  <button 
                    @click="$emit('delete-test', test.id)"
                    class="text-red-600 hover:text-red-900"
                  >
                    <TrashIcon class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, nextTick } from 'vue'
import { 
  PlusIcon, 
  ClipboardDocumentListIcon,
  PlayIcon,
  PencilIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'

export default {
  name: 'TestScenarios',
  components: {
    PlusIcon,
    ClipboardDocumentListIcon,
    PlayIcon,
    PencilIcon,
    TrashIcon
  },
  props: {
    testScenarios: {
      type: Array,
      default: () => []
    },
    currentCall: {
      type: Object,
      default: null
    }
  },
  emits: [
    'add-test',
    'edit-test',
    'delete-test',
    'run-test',
    'update-test-status',
    'update-test-notes',
    'load-defaults'
  ],
  setup(props, { emit }) {
    const editingNotes = ref(null)
    const notesEditValue = ref('')
    const notesInput = ref(null)

    const getCategoryBadge = (category) => {
      const badges = {
        'conversation': 'bg-blue-100 text-blue-800',
        'tools': 'bg-green-100 text-green-800',
        'error_handling': 'bg-red-100 text-red-800',
        'integration': 'bg-purple-100 text-purple-800',
        'performance': 'bg-yellow-100 text-yellow-800',
        'edge_cases': 'bg-gray-100 text-gray-800'
      }
      return badges[category] || 'bg-gray-100 text-gray-800'
    }

    const getStatusBadge = (status) => {
      const badges = {
        'not_started': 'bg-gray-100 text-gray-800',
        'in_progress': 'bg-blue-100 text-blue-800',
        'passed': 'bg-green-100 text-green-800',
        'failed': 'bg-red-100 text-red-800'
      }
      return badges[status] || 'bg-gray-100 text-gray-800'
    }

    const formatDate = (date) => {
      return new Date(date).toLocaleDateString()
    }

    const startEditingNotes = (test) => {
      editingNotes.value = test
      notesEditValue.value = test.notes || ''
      nextTick(() => {
        if (notesInput.value) {
          notesInput.value.focus()
        }
      })
    }

    const saveNotes = (test) => {
      emit('update-test-notes', test.id, notesEditValue.value)
      editingNotes.value = null
      notesEditValue.value = ''
    }

    const cancelEditingNotes = () => {
      editingNotes.value = null
      notesEditValue.value = ''
    }

    return {
      editingNotes,
      notesEditValue,
      notesInput,
      getCategoryBadge,
      getStatusBadge,
      formatDate,
      startEditingNotes,
      saveNotes,
      cancelEditingNotes
    }
  }
}
</script>

<style scoped>
.badge {
  @apply inline-flex items-center px-2 py-0.5 rounded text-xs font-medium;
}
</style> 