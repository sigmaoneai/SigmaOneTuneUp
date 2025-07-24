<template>
  <div class="w-full px-4 sm:px-6 lg:px-8">
    <!-- Page Header -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Knowledge Base</h1>
          <p class="mt-2 text-gray-600">Manage documentation and IT resources with ITGlue integration</p>
        </div>
        <div class="flex items-center space-x-4">
          <div class="flex items-center">
            <div :class="['w-3 h-3 rounded-full mr-2', connectionStatus === 'connected' ? 'bg-green-500' : 'bg-red-500']"></div>
            <span class="text-sm text-gray-600">ITGlue {{ connectionStatus === 'connected' ? 'Connected' : 'Disconnected' }}</span>
          </div>
          <button 
            @click="syncKnowledgeBase"
            :disabled="syncing"
            class="btn-primary"
          >
            <ArrowPathIcon :class="['w-4 h-4 mr-2', syncing ? 'animate-spin' : '']" />
            {{ syncing ? 'Syncing...' : 'Sync ITGlue' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <div class="card">
        <div class="card-body text-center">
          <div class="text-2xl font-bold text-primary-600">{{ stats.total_articles }}</div>
          <div class="text-sm text-gray-600">Total Articles</div>
        </div>
      </div>
      <div class="card">
        <div class="card-body text-center">
          <div class="text-2xl font-bold text-blue-600">{{ stats.total_categories }}</div>
          <div class="text-sm text-gray-600">Categories</div>
        </div>
      </div>
      <div class="card">
        <div class="card-body text-center">
          <div class="text-2xl font-bold text-green-600">{{ stats.recent_updates }}</div>
          <div class="text-sm text-gray-600">Recent Updates</div>
        </div>
      </div>
      <div class="card">
        <div class="card-body text-center">
          <div class="text-2xl font-bold text-purple-600">{{ stats.configurations }}</div>
          <div class="text-sm text-gray-600">Configurations</div>
        </div>
      </div>
    </div>

    <!-- Search Bar -->
    <div class="mb-6">
      <div class="flex flex-col sm:flex-row gap-4">
        <div class="flex-1">
          <div class="relative">
            <MagnifyingGlassIcon class="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search knowledge base articles, configurations, and documents..."
              class="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              @keyup.enter="performSearch"
            />
          </div>
        </div>
        <div class="flex gap-2">
          <select 
            v-model="selectedCategory"
            class="form-select"
            @change="filterByCategory"
          >
            <option value="">All Categories</option>
            <option v-for="category in categories" :key="category.id" :value="category.id">
              {{ category.name }}
            </option>
          </select>
          <button 
            @click="performSearch" 
            :disabled="loading"
            class="btn-primary px-6"
          >
            <MagnifyingGlassIcon class="w-4 h-4 mr-2" />
            Search
          </button>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="mb-6">
      <nav class="flex space-x-8">
        <button
          @click="activeTab = 'articles'"
          :class="[
            'py-2 px-1 border-b-2 font-medium text-sm',
            activeTab === 'articles'
              ? 'border-primary-500 text-primary-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          <DocumentTextIcon class="w-4 h-4 mr-2 inline" />
          Articles ({{ articles.length }})
        </button>
        <button
          @click="activeTab = 'configurations'"
          :class="[
            'py-2 px-1 border-b-2 font-medium text-sm',
            activeTab === 'configurations'
              ? 'border-primary-500 text-primary-600' 
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          <CogIcon class="w-4 h-4 mr-2 inline" />
          Configurations ({{ configurations.length }})
        </button>
        <button
          @click="activeTab = 'passwords'"
          :class="[
            'py-2 px-1 border-b-2 font-medium text-sm',
            activeTab === 'passwords'
              ? 'border-primary-500 text-primary-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          <KeyIcon class="w-4 h-4 mr-2 inline" />
          Passwords ({{ passwords.length }})
        </button>
        <button
          @click="activeTab = 'contacts'"
          :class="[
            'py-2 px-1 border-b-2 font-medium text-sm',
            activeTab === 'contacts'
              ? 'border-primary-500 text-primary-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          <UserIcon class="w-4 h-4 mr-2 inline" />
          Contacts ({{ contacts.length }})
        </button>
      </nav>
    </div>

    <!-- Articles Tab -->
    <div v-if="activeTab === 'articles'" class="space-y-6">
      <div class="card">
        <div class="card-header">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-medium text-gray-900">Knowledge Base Articles</h3>
            <button 
              @click="showCreateArticle = true"
              class="btn-primary btn-sm"
            >
              <PlusIcon class="w-3 h-3 mr-1" />
              New Article
            </button>
          </div>
        </div>
        
        <div class="card-body p-0">
          <div v-if="loading" class="p-8 text-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto mb-4"></div>
            <p class="text-gray-600">Loading articles...</p>
          </div>
          
          <div v-else-if="articles.length === 0" class="p-8 text-center">
            <DocumentTextIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 class="text-lg font-medium text-gray-900 mb-2">No articles found</h3>
            <p class="text-gray-600 mb-4">
              {{ searchQuery ? 'No articles match your search criteria.' : 'Start by syncing with ITGlue or creating your first article.' }}
            </p>
            <button @click="syncKnowledgeBase" class="btn-primary">
              <ArrowPathIcon class="w-4 h-4 mr-2" />
              Sync with ITGlue
            </button>
          </div>
          
          <div v-else class="divide-y divide-gray-200">
            <div 
              v-for="article in paginatedArticles"
              :key="article.id"
              class="p-6 hover:bg-gray-50 transition-colors cursor-pointer"
              @click="viewArticle(article)"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center space-x-3 mb-2">
                    <h4 class="text-lg font-medium text-gray-900 hover:text-primary-600">
                      {{ article.name }}
                    </h4>
                    <span v-if="article.category" class="badge badge-primary text-xs">
                      {{ article.category }}
                    </span>
                    <span v-if="article.organization" class="badge badge-gray text-xs">
                      {{ article.organization }}
                    </span>
                  </div>
                  
                  <p class="text-gray-600 text-sm mb-3 line-clamp-2">
                    {{ article.description || 'No description available' }}
                  </p>
                  
                  <div class="flex items-center space-x-4 text-xs text-gray-500">
                    <span class="flex items-center">
                      <CalendarIcon class="w-3 h-3 mr-1" />
                      Updated {{ formatDate(article.updated_at) }}
                    </span>
                    <span class="flex items-center">
                      <UserIcon class="w-3 h-3 mr-1" />
                      {{ article.author || 'Unknown' }}
                    </span>
                    <span v-if="article.tags && article.tags.length > 0" class="flex items-center">
                      <TagIcon class="w-3 h-3 mr-1" />
                      {{ article.tags.slice(0, 2).join(', ') }}{{ article.tags.length > 2 ? '...' : '' }}
                    </span>
                  </div>
                </div>
                
                <div class="flex items-center space-x-2 ml-4">
                  <button 
                    @click.stop="editArticle(article)"
                    class="text-gray-400 hover:text-primary-600"
                    title="Edit article"
                  >
                    <PencilIcon class="w-4 h-4" />
                  </button>
                  <button 
                    @click.stop="shareArticle(article)"
                    class="text-gray-400 hover:text-blue-600"
                    title="Share article"
                  >
                    <ShareIcon class="w-4 h-4" />
                  </button>
                  <button 
                    @click.stop="bookmarkArticle(article)"
                    :class="[
                      'w-4 h-4',
                      article.bookmarked ? 'text-yellow-500' : 'text-gray-400 hover:text-yellow-500'
                    ]"
                    title="Bookmark article"
                  >
                    <BookmarkIcon />
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Pagination -->
          <div v-if="articles.length > articlesPerPage" class="px-6 py-4 border-t bg-gray-50">
            <div class="flex items-center justify-between">
              <p class="text-sm text-gray-700">
                Showing {{ (currentPage - 1) * articlesPerPage + 1 }} to 
                {{ Math.min(currentPage * articlesPerPage, articles.length) }} of 
                {{ articles.length }} articles
              </p>
              <div class="flex space-x-2">
                <button 
                  @click="currentPage--"
                  :disabled="currentPage === 1"
                  class="btn-sm btn-secondary"
                >
                  Previous
                </button>
                <button 
                  @click="currentPage++"
                  :disabled="currentPage * articlesPerPage >= articles.length"
                  class="btn-sm btn-secondary"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Configurations Tab -->
    <div v-if="activeTab === 'configurations'" class="space-y-6">
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-medium text-gray-900">Configuration Items</h3>
        </div>
        <div class="card-body p-0">
          <div v-if="configurations.length === 0" class="p-8 text-center">
            <CogIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p class="text-gray-600">No configurations found. Sync with ITGlue to import configuration items.</p>
          </div>
          
          <div v-else class="divide-y divide-gray-200">
            <div 
              v-for="config in configurations"
              :key="config.id"
              class="p-4 hover:bg-gray-50"
            >
              <div class="flex items-start justify-between">
                <div>
                  <h4 class="text-md font-medium text-gray-900">{{ config.name }}</h4>
                  <p class="text-sm text-gray-600 mt-1">{{ config.description }}</p>
                  <div class="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                    <span>Type: {{ config.configuration_type_name }}</span>
                    <span>Organization: {{ config.organization_name }}</span>
                  </div>
                </div>
                <button 
                  @click="viewConfiguration(config)"
                  class="btn-sm btn-primary"
                >
                  View Details
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Passwords Tab -->
    <div v-if="activeTab === 'passwords'" class="space-y-6">
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-medium text-gray-900">Password Repository</h3>
        </div>
        <div class="card-body p-0">
          <div v-if="passwords.length === 0" class="p-8 text-center">
            <KeyIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p class="text-gray-600">No passwords found. Sync with ITGlue to access the password repository.</p>
          </div>
          
          <div v-else class="divide-y divide-gray-200">
            <div 
              v-for="password in passwords"
              :key="password.id"
              class="p-4 hover:bg-gray-50"
            >
              <div class="flex items-start justify-between">
                <div>
                  <h4 class="text-md font-medium text-gray-900">{{ password.name }}</h4>
                  <p class="text-sm text-gray-600 mt-1">{{ password.resource_name }}</p>
                  <div class="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                    <span>Username: {{ password.username || 'N/A' }}</span>
                    <span>Organization: {{ password.organization_name }}</span>
                  </div>
                </div>
                <div class="flex space-x-2">
                  <button 
                    @click="copyUsername(password)"
                    class="btn-sm btn-secondary"
                    title="Copy username"
                  >
                    <DocumentDuplicateIcon class="w-3 h-3" />
                  </button>
                  <button 
                    @click="viewPassword(password)"
                    class="btn-sm btn-primary"
                  >
                    <EyeIcon class="w-3 h-3 mr-1" />
                    View
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Contacts Tab -->
    <div v-if="activeTab === 'contacts'" class="space-y-6">
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-medium text-gray-900">Contact Directory</h3>
        </div>
        <div class="card-body p-0">
          <div v-if="contacts.length === 0" class="p-8 text-center">
            <UserIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p class="text-gray-600">No contacts found. Sync with ITGlue to import the contact directory.</p>
          </div>
          
          <div v-else class="divide-y divide-gray-200">
            <div 
              v-for="contact in contacts"
              :key="contact.id"
              class="p-4 hover:bg-gray-50"
            >
              <div class="flex items-start justify-between">
                <div>
                  <h4 class="text-md font-medium text-gray-900">{{ contact.name }}</h4>
                  <p class="text-sm text-gray-600 mt-1">{{ contact.title || 'No title' }}</p>
                  <div class="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                    <span v-if="contact.email">{{ contact.email }}</span>
                    <span v-if="contact.phone">{{ contact.phone }}</span>
                    <span>Organization: {{ contact.organization_name }}</span>
                  </div>
                </div>
                <button 
                  @click="viewContact(contact)"
                  class="btn-sm btn-primary"
                >
                  View Details
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Article Detail Modal -->
    <div v-if="showArticleModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-10 mx-auto p-5 border w-full max-w-4xl shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-xl font-bold text-gray-900">{{ selectedArticle?.name }}</h3>
            <button @click="closeArticleModal" class="text-gray-400 hover:text-gray-600">
              <XMarkIcon class="w-6 h-6" />
            </button>
          </div>
          
          <div v-if="selectedArticle" class="space-y-4">
            <div class="flex flex-wrap gap-2 mb-4">
              <span v-if="selectedArticle.category" class="badge badge-primary">
                {{ selectedArticle.category }}
              </span>
              <span v-if="selectedArticle.organization" class="badge badge-gray">
                {{ selectedArticle.organization }}
              </span>
              <span v-for="tag in (selectedArticle.tags || [])" :key="tag" class="badge badge-blue">
                {{ tag }}
              </span>
            </div>
            
            <div class="prose max-w-none" v-html="selectedArticle.content || selectedArticle.description">
            </div>
            
            <div class="flex items-center justify-between pt-4 border-t">
              <div class="text-sm text-gray-500">
                <p>Last updated: {{ formatDate(selectedArticle.updated_at) }}</p>
                <p v-if="selectedArticle.author">Author: {{ selectedArticle.author }}</p>
              </div>
              <div class="flex space-x-2">
                <button @click="editArticle(selectedArticle)" class="btn-secondary">
                  <PencilIcon class="w-4 h-4 mr-2" />
                  Edit
                </button>
                <button @click="shareArticle(selectedArticle)" class="btn-primary">
                  <ShareIcon class="w-4 h-4 mr-2" />
                  Share
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useToast } from 'vue-toastification'
import { formatDistanceToNow } from 'date-fns'
import api from '@/services/api'
import {
  DocumentTextIcon,
  CogIcon,
  KeyIcon,
  UserIcon,
  MagnifyingGlassIcon,
  PlusIcon,
  ArrowPathIcon,
  CalendarIcon,
  TagIcon,
  PencilIcon,
  ShareIcon,
  BookmarkIcon,
  EyeIcon,
  DocumentDuplicateIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'

const toast = useToast()

// Reactive state
const loading = ref(false)
const syncing = ref(false)
const connectionStatus = ref('connected')
const activeTab = ref('articles')
const searchQuery = ref('')
const selectedCategory = ref('')
const currentPage = ref(1)
const articlesPerPage = ref(10)

// Data
const stats = ref({
  total_articles: 0,
  total_categories: 0,
  recent_updates: 0,
  configurations: 0
})

const categories = ref([])
const articles = ref([])
const configurations = ref([])
const passwords = ref([])
const contacts = ref([])

// Modals
const showArticleModal = ref(false)
const showCreateArticle = ref(false)
const selectedArticle = ref(null)

// Computed properties
const paginatedArticles = computed(() => {
  const start = (currentPage.value - 1) * articlesPerPage.value
  const end = start + articlesPerPage.value
  return articles.value.slice(start, end)
})

// Methods
const loadKnowledgeBase = async () => {
  loading.value = true
  try {
    await Promise.all([
      loadStats(),
      loadCategories(),
      loadArticles(),
      loadConfigurations(),
      loadPasswords(),
      loadContacts()
    ])
  } catch (error) {
    toast.error('Failed to load knowledge base data')
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const response = await api.knowledgeBase.getStats()
    stats.value = response.data
  } catch (error) {
    console.error('Error loading stats:', error)
  }
}

const loadCategories = async () => {
  try {
    const response = await api.knowledgeBase.getCategories()
    categories.value = response.data
  } catch (error) {
    console.error('Error loading categories:', error)
  }
}

const loadArticles = async () => {
  try {
    const params = {}
    if (searchQuery.value) params.search = searchQuery.value
    if (selectedCategory.value) params.category = selectedCategory.value
    
    const response = await api.knowledgeBase.getArticles(params)
    articles.value = response.data
    stats.value.total_articles = articles.value.length
  } catch (error) {
    console.error('Error loading articles:', error)
  }
}

const loadConfigurations = async () => {
  try {
    const response = await api.knowledgeBase.getConfigurations()
    configurations.value = response.data
    stats.value.configurations = configurations.value.length
  } catch (error) {
    console.error('Error loading configurations:', error)
  }
}

const loadPasswords = async () => {
  try {
    const response = await api.knowledgeBase.getPasswords()
    passwords.value = response.data
  } catch (error) {
    console.error('Error loading passwords:', error)
  }
}

const loadContacts = async () => {
  try {
    const response = await api.knowledgeBase.getContacts()
    contacts.value = response.data
  } catch (error) {
    console.error('Error loading contacts:', error)
  }
}

const syncKnowledgeBase = async () => {
  syncing.value = true
  try {
    await api.knowledgeBase.syncWithITGlue()
    toast.success('Knowledge base synced successfully')
    
    // Reload data after sync
    await loadKnowledgeBase()
  } catch (error) {
    toast.error('Failed to sync with ITGlue: ' + (error.response?.data?.detail || error.message))
  } finally {
    syncing.value = false
  }
}

const performSearch = async () => {
  currentPage.value = 1
  await loadArticles()
}

const filterByCategory = async () => {
  currentPage.value = 1
  await loadArticles()
}

const viewArticle = (article) => {
  selectedArticle.value = article
  showArticleModal.value = true
}

const closeArticleModal = () => {
  showArticleModal.value = false
  selectedArticle.value = null
}

const editArticle = (article) => {
  toast.info(`Edit functionality for "${article.name}" coming soon`)
}

const shareArticle = (article) => {
  if (navigator.share) {
    navigator.share({
      title: article.name,
      text: article.description,
      url: window.location.href
    })
  } else {
    // Fallback: copy URL to clipboard
    navigator.clipboard.writeText(window.location.href)
    toast.success('Article URL copied to clipboard')
  }
}

const bookmarkArticle = (article) => {
  article.bookmarked = !article.bookmarked
  toast.success(article.bookmarked ? 'Article bookmarked' : 'Bookmark removed')
}

const viewConfiguration = (config) => {
  toast.info(`Configuration details for "${config.name}" coming soon`)
}

const copyUsername = async (password) => {
  if (password.username) {
    try {
      await navigator.clipboard.writeText(password.username)
      toast.success('Username copied to clipboard')
    } catch (error) {
      toast.error('Failed to copy username')
    }
  }
}

const viewPassword = (password) => {
  toast.info(`Password details for "${password.name}" coming soon`)
}

const viewContact = (contact) => {
  toast.info(`Contact details for "${contact.name}" coming soon`)
}

const formatDate = (dateString) => {
  return formatDistanceToNow(new Date(dateString), { addSuffix: true })
}

// Lifecycle
onMounted(() => {
  loadKnowledgeBase()
})
</script>

<style scoped>
.form-select {
  @apply block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm;
}

.btn-sm {
  @apply px-2.5 py-1.5 text-xs font-medium rounded;
}

.badge {
  @apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium;
}

.badge-primary {
  @apply bg-primary-100 text-primary-800;
}

.badge-gray {
  @apply bg-gray-100 text-gray-800;
}

.badge-blue {
  @apply bg-blue-100 text-blue-800;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style> 