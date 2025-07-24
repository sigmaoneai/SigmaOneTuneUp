<template>
  <div class="bg-white rounded-lg shadow">
    <!-- Header -->
    <div class="px-6 py-4 border-b border-gray-200">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-lg font-medium text-gray-900">Evaluation Tests</h3>
          <p class="mt-1 text-sm text-gray-500">
            Detailed evaluation criteria for test scenarios ({{ totalEvalTests }} tests)
          </p>
        </div>
        <button
          @click="showAddEvalModal = true"
          class="btn-primary btn-sm"
          :disabled="!selectedScenario"
        >
          <PlusIcon class="w-4 h-4 mr-2" />
          Add Eval Test
        </button>
      </div>
    </div>

    <!-- Scenario Selector -->
    <div class="px-6 py-4 bg-gray-50 border-b border-gray-200">
      <div class="flex items-center space-x-4">
        <label class="text-sm font-medium text-gray-700">Test Scenario:</label>
        <select 
          v-model="selectedScenario"
          @change="loadEvalTests"
          class="form-select"
        >
          <option value="">Select a test scenario...</option>
          <option v-for="scenario in testScenarios" :key="scenario.id" :value="scenario.id">
            {{ scenario.name }}
          </option>
        </select>
        <div v-if="selectedScenario" class="text-sm text-gray-500">
          {{ currentScenarioEvals.length }} evaluation tests
        </div>
      </div>
    </div>

    <!-- Eval Tests List -->
    <div v-if="selectedScenario" class="divide-y divide-gray-200">
      <div v-if="currentScenarioEvals.length === 0" class="px-6 py-8 text-center">
        <DocumentCheckIcon class="mx-auto h-12 w-12 text-gray-400" />
        <h3 class="mt-2 text-sm font-medium text-gray-900">No evaluation tests</h3>
        <p class="mt-1 text-sm text-gray-500">Get started by creating an evaluation test for this scenario.</p>
        <div class="mt-6">
          <button @click="showAddEvalModal = true" class="btn-primary btn-sm">
            <PlusIcon class="w-4 h-4 mr-2" />
            Add First Eval Test
          </button>
        </div>
      </div>

      <div v-for="evalTest in currentScenarioEvals" :key="evalTest.id" class="px-6 py-4 hover:bg-gray-50">
        <div class="flex items-start justify-between">
          <div class="flex-1 min-w-0">
            <div class="flex items-center space-x-3">
              <h4 class="text-sm font-medium text-gray-900">{{ evalTest.name }}</h4>
              <span :class="getStatusBadge(evalTest.status)" class="badge text-xs">{{ evalTest.status }}</span>
              <span :class="getTypeBadge(evalTest.eval_type)" class="badge text-xs">{{ evalTest.eval_type }}</span>
              <span class="text-xs text-gray-500">Weight: {{ evalTest.weight }}</span>
            </div>
            
            <p v-if="evalTest.description" class="mt-1 text-sm text-gray-600">{{ evalTest.description }}</p>
            
            <div class="mt-2 text-sm text-gray-600">
              <div><strong>Criteria:</strong> {{ evalTest.eval_criteria }}</div>
              <div class="mt-1"><strong>Expected:</strong> {{ evalTest.expected_outcome }}</div>
            </div>
            
            <div v-if="evalTest.score !== null" class="mt-2 flex items-center space-x-4">
              <div class="flex items-center">
                <span class="text-sm font-medium text-gray-700">Score:</span>
                <div class="ml-2 flex items-center">
                  <div class="w-24 h-2 bg-gray-200 rounded-full">
                    <div 
                      :class="getScoreColor(evalTest.score)"
                      class="h-2 rounded-full transition-all duration-300"
                      :style="{ width: `${evalTest.score}%` }"
                    ></div>
                  </div>
                  <span class="ml-2 text-sm font-medium">{{ evalTest.score }}%</span>
                </div>
              </div>
              <div v-if="evalTest.last_evaluated" class="text-xs text-gray-500">
                Evaluated {{ formatTime(evalTest.last_evaluated) }}
              </div>
            </div>
            
            <div v-if="evalTest.notes" class="mt-2 text-sm text-gray-600">
              <strong>Notes:</strong> {{ evalTest.notes }}
            </div>
          </div>
          
          <div class="flex items-center space-x-2 ml-4">
            <button
              @click="evaluateTest(evalTest)"
              class="btn-secondary btn-sm"
              :title="evalTest.score ? 'Re-evaluate' : 'Evaluate'"
            >
              <CheckIcon class="w-4 h-4" />
            </button>
            <button
              @click="editEvalTest(evalTest)"
              class="btn-secondary btn-sm"
              title="Edit"
            >
              <PencilIcon class="w-4 h-4" />
            </button>
            <button
              @click="deleteEvalTest(evalTest.id)"
              class="btn-danger btn-sm"
              title="Delete"
            >
              <TrashIcon class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Eval Test Modal -->
    <div v-if="showAddEvalModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-medium text-gray-900">
              {{ editingEvalTest ? 'Edit' : 'Add' }} Evaluation Test
            </h3>
            <button @click="closeEvalModal" class="text-gray-400 hover:text-gray-600">
              <XMarkIcon class="w-6 h-6" />
            </button>
          </div>
          
          <form @submit.prevent="saveEvalTest">
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Test Name</label>
                <input 
                  v-model="evalForm.name"
                  type="text"
                  required
                  class="form-input w-full"
                  placeholder="e.g., Response Accuracy Check"
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea 
                  v-model="evalForm.description"
                  class="form-input w-full"
                  rows="2"
                  placeholder="Brief description of what this evaluation tests"
                ></textarea>
              </div>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Evaluation Type</label>
                  <select v-model="evalForm.eval_type" required class="form-select w-full">
                    <option value="accuracy">Accuracy</option>
                    <option value="latency">Latency</option>
                    <option value="tone">Tone</option>
                    <option value="completeness">Completeness</option>
                    <option value="relevance">Relevance</option>
                    <option value="tool_usage">Tool Usage</option>
                  </select>
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Weight (1-10)</label>
                  <input 
                    v-model.number="evalForm.weight"
                    type="number"
                    min="1"
                    max="10"
                    required
                    class="form-input w-full"
                  />
                </div>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Evaluation Criteria</label>
                <textarea 
                  v-model="evalForm.eval_criteria"
                  required
                  class="form-input w-full"
                  rows="3"
                  placeholder="What exactly should be evaluated? Be specific about the criteria..."
                ></textarea>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Expected Outcome</label>
                <textarea 
                  v-model="evalForm.expected_outcome"
                  required
                  class="form-input w-full"
                  rows="3"
                  placeholder="What should the ideal result look like?"
                ></textarea>
              </div>
            </div>
            
            <div class="flex justify-end space-x-3 pt-6 border-t mt-6">
              <button type="button" @click="closeEvalModal" class="btn-secondary">
                Cancel
              </button>
              <button type="submit" class="btn-primary">
                {{ editingEvalTest ? 'Update' : 'Create' }} Eval Test
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Evaluate Test Modal -->
    <div v-if="showEvaluateModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-full max-w-lg shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-medium text-gray-900">Evaluate Test</h3>
            <button @click="showEvaluateModal = false" class="text-gray-400 hover:text-gray-600">
              <XMarkIcon class="w-6 h-6" />
            </button>
          </div>
          
          <div v-if="evaluatingTest" class="space-y-4">
            <div class="bg-gray-50 p-4 rounded-lg">
              <h4 class="font-medium text-gray-900">{{ evaluatingTest.name }}</h4>
              <p class="text-sm text-gray-600 mt-1">{{ evaluatingTest.eval_criteria }}</p>
            </div>
            
            <form @submit.prevent="submitEvaluation">
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Score (0-100)
                  </label>
                  <input 
                    v-model.number="evaluationScore"
                    type="number"
                    min="0"
                    max="100"
                    required
                    class="form-input w-full"
                    placeholder="Enter score from 0 to 100"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                  <textarea 
                    v-model="evaluationNotes"
                    class="form-input w-full"
                    rows="3"
                    placeholder="Additional notes about the evaluation..."
                  ></textarea>
                </div>
              </div>
              
              <div class="flex justify-end space-x-3 pt-4 border-t mt-4">
                <button type="button" @click="showEvaluateModal = false" class="btn-secondary">
                  Cancel
                </button>
                <button type="submit" class="btn-primary">
                  Submit Evaluation
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useToast } from 'vue-toastification'
import { formatDistanceToNow } from 'date-fns'
import api from '@/services/api'
import {
  PlusIcon,
  DocumentCheckIcon,
  PencilIcon,
  TrashIcon,
  XMarkIcon,
  CheckIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  testScenarios: {
    type: Array,
    default: () => []
  }
})

const toast = useToast()

// Reactive state
const evalTests = ref([])
const selectedScenario = ref('')
const showAddEvalModal = ref(false)
const showEvaluateModal = ref(false)
const editingEvalTest = ref(null)
const evaluatingTest = ref(null)
const evaluationScore = ref(null)
const evaluationNotes = ref('')

const evalForm = ref({
  name: '',
  description: '',
  eval_criteria: '',
  expected_outcome: '',
  eval_type: 'accuracy',
  weight: 1
})

// Computed properties
const currentScenarioEvals = computed(() => {
  if (!selectedScenario.value) return []
  return evalTests.value.filter(test => test.test_scenario_id === selectedScenario.value)
})

const totalEvalTests = computed(() => evalTests.value.length)

// Methods
const loadEvalTests = async () => {
  try {
    const response = await api.evalTests.list(selectedScenario.value)
    evalTests.value = response.data
  } catch (error) {
    toast.error('Failed to load evaluation tests')
  }
}

const loadAllEvalTests = async () => {
  try {
    const response = await api.evalTests.list()
    evalTests.value = response.data
  } catch (error) {
    toast.error('Failed to load evaluation tests')
  }
}

const resetEvalForm = () => {
  evalForm.value = {
    name: '',
    description: '',
    eval_criteria: '',
    expected_outcome: '',
    eval_type: 'accuracy',
    weight: 1
  }
}

const closeEvalModal = () => {
  showAddEvalModal.value = false
  editingEvalTest.value = null
  resetEvalForm()
}

const editEvalTest = (evalTest) => {
  editingEvalTest.value = evalTest
  evalForm.value = {
    name: evalTest.name,
    description: evalTest.description || '',
    eval_criteria: evalTest.eval_criteria,
    expected_outcome: evalTest.expected_outcome,
    eval_type: evalTest.eval_type,
    weight: evalTest.weight
  }
  showAddEvalModal.value = true
}

const saveEvalTest = async () => {
  try {
    if (editingEvalTest.value) {
      await api.evalTests.update(editingEvalTest.value.id, evalForm.value)
      toast.success('Evaluation test updated')
    } else {
      const data = {
        ...evalForm.value,
        test_scenario_id: selectedScenario.value
      }
      await api.evalTests.create(data)
      toast.success('Evaluation test created')
    }
    
    closeEvalModal()
    loadEvalTests()
  } catch (error) {
    toast.error('Failed to save evaluation test')
  }
}

const deleteEvalTest = async (evalTestId) => {
  if (!confirm('Are you sure you want to delete this evaluation test?')) return
  
  try {
    await api.evalTests.delete(evalTestId)
    toast.success('Evaluation test deleted')
    loadEvalTests()
  } catch (error) {
    toast.error('Failed to delete evaluation test')
  }
}

const evaluateTest = (evalTest) => {
  evaluatingTest.value = evalTest
  evaluationScore.value = evalTest.score || null
  evaluationNotes.value = evalTest.notes || ''
  showEvaluateModal.value = true
}

const submitEvaluation = async () => {
  try {
    await api.evalTests.evaluate(
      evaluatingTest.value.id,
      evaluationScore.value,
      evaluationNotes.value
    )
    
    toast.success('Evaluation submitted')
    showEvaluateModal.value = false
    evaluatingTest.value = null
    evaluationScore.value = null
    evaluationNotes.value = ''
    loadEvalTests()
  } catch (error) {
    toast.error('Failed to submit evaluation')
  }
}

const getStatusBadge = (status) => {
  const badges = {
    pending: 'bg-gray-100 text-gray-800',
    passed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
    warning: 'bg-yellow-100 text-yellow-800'
  }
  return badges[status] || 'bg-gray-100 text-gray-800'
}

const getTypeBadge = (type) => {
  const badges = {
    accuracy: 'bg-blue-100 text-blue-800',
    latency: 'bg-purple-100 text-purple-800',
    tone: 'bg-pink-100 text-pink-800',
    completeness: 'bg-green-100 text-green-800',
    relevance: 'bg-yellow-100 text-yellow-800',
    tool_usage: 'bg-indigo-100 text-indigo-800'
  }
  return badges[type] || 'bg-gray-100 text-gray-800'
}

const getScoreColor = (score) => {
  if (score >= 80) return 'bg-green-500'
  if (score >= 60) return 'bg-yellow-500'
  return 'bg-red-500'
}

const formatTime = (timestamp) => {
  return formatDistanceToNow(new Date(timestamp), { addSuffix: true })
}

// Watch for scenario changes
watch(selectedScenario, (newScenario) => {
  if (newScenario) {
    loadEvalTests()
  }
})

// Initialize
onMounted(() => {
  loadAllEvalTests()
})
</script>

<style scoped>
.form-input, .form-select {
  @apply block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm;
}

.btn-sm {
  @apply px-2.5 py-1.5 text-xs font-medium rounded;
}

.badge {
  @apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium;
}

.btn-primary {
  @apply bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-md transition-colors;
}

.btn-secondary {
  @apply bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded-md transition-colors;
}

.btn-danger {
  @apply bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-md transition-colors;
}
</style> 