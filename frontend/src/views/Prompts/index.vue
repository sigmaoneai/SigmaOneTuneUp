<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="sm:flex sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Prompt Management</h1>
        <p class="mt-2 text-sm text-gray-700">
          Manage prompt templates and scenarios for your agents
        </p>
      </div>
      <div class="mt-4 sm:mt-0 sm:flex sm:space-x-3">
        <button
          @click="importTemplates"
          :disabled="importing"
          class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
        >
          <ArrowDownTrayIcon class="h-4 w-4 mr-2" />
          {{ importing ? 'Importing...' : 'Import Templates' }}
        </button>
        <button
          @click="showCreateTemplate = true"
          class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          <PlusIcon class="h-4 w-4 mr-2" />
          New Template
        </button>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-8">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="activeTab = tab.key"
          :class="[
            activeTab === tab.key
              ? 'border-indigo-500 text-indigo-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            'whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm'
          ]"
        >
          <component :is="tab.icon" class="h-5 w-5 mr-2 inline" />
          {{ tab.name }}
          <span
            v-if="tab.count !== undefined"
            :class="[
              activeTab === tab.key
                ? 'bg-indigo-100 text-indigo-600'
                : 'bg-gray-100 text-gray-900',
              'hidden ml-2 py-0.5 px-2.5 rounded-full text-xs font-medium md:inline-block'
            ]"
          >
            {{ tab.count }}
          </span>
        </button>
      </nav>
    </div>

    <!-- Templates Tab -->
    <div v-if="activeTab === 'templates'" class="space-y-6">
      <!-- Filters -->
      <div class="bg-white p-4 rounded-lg border border-gray-200">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Search</label>
            <input
              v-model="templateFilters.search"
              type="text"
              placeholder="Search templates..."
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Category</label>
            <select
              v-model="templateFilters.category"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            >
              <option value="">All Categories</option>
              <option v-for="category in categories" :key="category" :value="category">
                {{ category }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Status</label>
            <select
              v-model="templateFilters.is_active"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            >
              <option value="">All</option>
              <option :value="true">Active</option>
              <option :value="false">Inactive</option>
            </select>
          </div>
          <div class="flex items-end">
            <button
              @click="loadTemplates"
              class="w-full px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Apply Filters
            </button>
          </div>
        </div>
      </div>

      <!-- Templates List -->
      <div class="bg-white shadow overflow-hidden sm:rounded-md">
        <div v-if="loading" class="p-6 text-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
          <p class="mt-2 text-sm text-gray-500">Loading templates...</p>
        </div>
        <ul v-else-if="templates.length > 0" class="divide-y divide-gray-200">
          <li v-for="template in templates" :key="template.id" class="p-6 hover:bg-gray-50">
            <div class="flex items-center justify-between">
              <div class="flex-1 min-w-0">
                <div class="flex items-center space-x-3">
                  <h3 class="text-lg font-medium text-gray-900 truncate">
                    {{ template.title }}
                  </h3>
                  <span
                    :class="[
                      template.is_system_template
                        ? 'bg-purple-100 text-purple-800'
                        : 'bg-green-100 text-green-800',
                      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium'
                    ]"
                  >
                    {{ template.is_system_template ? 'System' : 'Custom' }}
                  </span>
                  <span
                    :class="[
                      template.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800',
                      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium'
                    ]"
                  >
                    {{ template.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </div>
                <p class="mt-1 text-sm text-gray-500">{{ template.description }}</p>
                <div class="mt-2 flex items-center space-x-4 text-sm text-gray-500">
                  <span class="flex items-center">
                    <TagIcon class="h-4 w-4 mr-1" />
                    {{ template.category }}
                  </span>
                  <span class="flex items-center">
                    <DocumentTextIcon class="h-4 w-4 mr-1" />
                    {{ template.scenario_count }} scenarios
                  </span>
                  <span class="flex items-center">
                    <CalendarIcon class="h-4 w-4 mr-1" />
                    {{ formatDate(template.created_at) }}
                  </span>
                </div>
              </div>
              <div class="flex items-center space-x-2">
                <button
                  @click="editTemplate(template)"
                  class="p-2 text-gray-400 hover:text-gray-600"
                  title="Edit Template"
                >
                  <PencilIcon class="h-5 w-5" />
                </button>
                <button
                  @click="createScenario(template)"
                  class="p-2 text-indigo-400 hover:text-indigo-600"
                  title="Create Scenario"
                >
                  <PlusCircleIcon class="h-5 w-5" />
                </button>
                <button
                  @click="viewScenarios(template)"
                  class="p-2 text-blue-400 hover:text-blue-600"
                  title="View Scenarios"
                >
                  <EyeIcon class="h-5 w-5" />
                </button>
                <button
                  v-if="!template.is_system_template"
                  @click="deleteTemplate(template)"
                  class="p-2 text-red-400 hover:text-red-600"
                  title="Delete Template"
                >
                  <TrashIcon class="h-5 w-5" />
                </button>
              </div>
            </div>
          </li>
        </ul>
        <div v-else class="p-6 text-center">
          <DocumentTextIcon class="mx-auto h-12 w-12 text-gray-400" />
          <h3 class="mt-2 text-sm font-medium text-gray-900">No templates found</h3>
          <p class="mt-1 text-sm text-gray-500">Get started by creating a new template or importing existing ones.</p>
        </div>
      </div>
    </div>

    <!-- Scenarios Tab -->
    <div v-if="activeTab === 'scenarios'" class="space-y-6">
      <!-- Scenarios filters and list will go here -->
      <ScenariosList
        @edit="editScenario"
        @delete="deleteScenario"
        @assign="assignScenario"
      />
    </div>

    <!-- Assignments Tab -->
    <div v-if="activeTab === 'assignments'" class="space-y-6">
      <!-- Assignments list will go here -->
      <AssignmentsList />
    </div>

    <!-- Create/Edit Template Modal -->
    <TemplateModal
      v-if="showCreateTemplate || editingTemplate"
      :template="editingTemplate"
      @close="closeTemplateModal"
      @saved="onTemplateSaved"
    />

    <!-- Create/Edit Scenario Modal -->
    <ScenarioModal
      v-if="showCreateScenario || editingScenario"
      :scenario="editingScenario"
      :template="selectedTemplate"
      @close="closeScenarioModal"
      @saved="onScenarioSaved"
    />

    <!-- Assignment Modal -->
    <AssignmentModal
      v-if="showAssignmentModal"
      :scenario="selectedScenario"
      @close="showAssignmentModal = false"
      @assigned="onAssignmentCreated"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useToast } from 'vue-toastification'
import {
  PlusIcon,
  PencilIcon,
  TrashIcon,
  EyeIcon,
  PlusCircleIcon,
  TagIcon,
  DocumentTextIcon,
  CalendarIcon,
  ArrowDownTrayIcon,
  CogIcon,
  UserGroupIcon
} from '@heroicons/vue/24/outline'
import api from '@/services/api'
import TemplateModal from '@/components/prompts/TemplateModal.vue'
import ScenarioModal from '@/components/prompts/ScenarioModal.vue'
import AssignmentModal from '@/components/prompts/AssignmentModal.vue'
import ScenariosList from '@/components/prompts/ScenariosList.vue'
import AssignmentsList from '@/components/prompts/AssignmentsList.vue'

const toast = useToast()

// Data
const activeTab = ref('templates')
const loading = ref(false)
const importing = ref(false)

// Templates
const templates = ref([])
const categories = ref([])
const templateFilters = ref({
  search: '',
  category: '',
  is_active: ''
})

// Modals
const showCreateTemplate = ref(false)
const showCreateScenario = ref(false)
const showAssignmentModal = ref(false)
const editingTemplate = ref(null)
const editingScenario = ref(null)
const selectedTemplate = ref(null)
const selectedScenario = ref(null)

// Computed
const tabs = computed(() => [
  {
    key: 'templates',
    name: 'Templates',
    icon: DocumentTextIcon,
    count: templates.value.length
  },
  {
    key: 'scenarios',
    name: 'Scenarios',
    icon: CogIcon
  },
  {
    key: 'assignments',
    name: 'Assignments',
    icon: UserGroupIcon
  }
])

// Methods
const loadTemplates = async () => {
  loading.value = true
  try {
    const params = {}
    if (templateFilters.value.search) params.search = templateFilters.value.search
    if (templateFilters.value.category) params.category = templateFilters.value.category
    if (templateFilters.value.is_active !== '') params.is_active = templateFilters.value.is_active
    
    const response = await api.prompts.list(params)
    templates.value = response.data
  } catch (error) {
    console.error('Error loading templates:', error)
    toast.error('Failed to load templates')
  } finally {
    loading.value = false
  }
}

const loadCategories = async () => {
  try {
    const response = await api.prompts.listCategories()
    categories.value = response.data.categories
  } catch (error) {
    console.error('Error loading categories:', error)
  }
}

const importTemplates = async () => {
  importing.value = true
  try {
    const response = await api.prompts.importFromFiles()
    toast.success(`Successfully imported ${response.data.imported_count} templates`)
    if (response.data.errors && response.data.errors.length > 0) {
      console.warn('Import errors:', response.data.errors)
    }
    await loadTemplates()
  } catch (error) {
    console.error('Error importing templates:', error)
    toast.error('Failed to import templates')
  } finally {
    importing.value = false
  }
}

const editTemplate = (template) => {
  editingTemplate.value = template
}

const deleteTemplate = async (template) => {
  if (!confirm(`Are you sure you want to delete the template "${template.title}"?`)) return
  
  try {
    await api.prompts.delete(template.id)
    toast.success('Template deleted successfully')
    await loadTemplates()
  } catch (error) {
    console.error('Error deleting template:', error)
    toast.error('Failed to delete template')
  }
}

const createScenario = (template) => {
  selectedTemplate.value = template
  showCreateScenario.value = true
}

const viewScenarios = (template) => {
  // Switch to scenarios tab and filter by template
  activeTab.value = 'scenarios'
  // The ScenariosList component will handle filtering
}

const editScenario = (scenario) => {
  editingScenario.value = scenario
}

const deleteScenario = async (scenario) => {
  if (!confirm(`Are you sure you want to delete the scenario "${scenario.name}"?`)) return
  
  try {
    await api.prompts.deleteScenario(scenario.id)
    toast.success('Scenario deleted successfully')
    // Refresh scenarios list
  } catch (error) {
    console.error('Error deleting scenario:', error)
    toast.error('Failed to delete scenario')
  }
}

const assignScenario = (scenario) => {
  selectedScenario.value = scenario
  showAssignmentModal.value = true
}

// Modal handlers
const closeTemplateModal = () => {
  showCreateTemplate.value = false
  editingTemplate.value = null
}

const closeScenarioModal = () => {
  showCreateScenario.value = false
  editingScenario.value = null
  selectedTemplate.value = null
}

const onTemplateSaved = () => {
  closeTemplateModal()
  loadTemplates()
  toast.success('Template saved successfully')
}

const onScenarioSaved = () => {
  closeScenarioModal()
  toast.success('Scenario saved successfully')
}

const onAssignmentCreated = () => {
  showAssignmentModal.value = false
  toast.success('Scenario assigned successfully')
}

// Utility functions
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString()
}

// Watchers
watch(() => templateFilters.value, () => {
  // Auto-apply filters after a delay
  setTimeout(loadTemplates, 300)
}, { deep: true })

// Lifecycle
onMounted(async () => {
  await Promise.all([
    loadTemplates(),
    loadCategories()
  ])
})
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style> 