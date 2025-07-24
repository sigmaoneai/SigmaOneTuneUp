<template>
  <div class="w-full px-4 sm:px-6 lg:px-8">
    <!-- Page Header -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Business Onboarding</h1>
          <p class="mt-2 text-gray-600">Chat with our AI assistant to build your organization's SOPs and knowledge base</p>
        </div>
        <div class="flex items-center space-x-4">
          <!-- Connection Status -->
          <div class="flex items-center">
            <div :class="['w-3 h-3 rounded-full mr-2', connectionStatus === 'connected' ? 'bg-green-500' : 'bg-red-500']"></div>
            <span class="text-sm text-gray-600">{{ connectionStatus === 'connected' ? 'Connected' : 'Disconnected' }}</span>
          </div>
          
          <!-- WebSocket Status -->
          <div class="flex items-center">
            <div :class="['w-2 h-2 rounded-full mr-2', wsConnected ? 'bg-blue-500' : 'bg-gray-400']"></div>
            <span class="text-xs text-gray-500">{{ wsConnected ? 'Live' : 'Offline' }}</span>
          </div>
          
          <!-- Connected Users -->
          <div v-if="connectedUsers.length > 0" class="flex items-center space-x-2">
            <span class="text-xs text-gray-500">{{ connectedUsers.length + 1 }} active</span>
            <div class="flex -space-x-1">
              <!-- Current user -->
              <div class="w-6 h-6 rounded-full bg-primary-500 border-2 border-white flex items-center justify-center text-xs font-medium text-white" title="You">
                {{ userId.substring(0, 1).toUpperCase() }}
              </div>
              <!-- Other users -->
              <div v-for="user in connectedUsers.slice(0, 3)" :key="user.user_id" 
                   class="w-6 h-6 rounded-full bg-gray-500 border-2 border-white flex items-center justify-center text-xs font-medium text-white"
                   :title="user.user_info.name">
                {{ user.user_info.name.substring(0, 1).toUpperCase() }}
              </div>
              <div v-if="connectedUsers.length > 3" 
                   class="w-6 h-6 rounded-full bg-gray-300 border-2 border-white flex items-center justify-center text-xs font-medium text-gray-700"
                   :title="`+${connectedUsers.length - 3} more users`">
                +{{ connectedUsers.length - 3 }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Admin Section -->
    <div class="mb-6">
      <div class="card border-dashed border-2 border-gray-300">
        <div class="card-header bg-gray-50">
          <button 
            @click="showAdminSection = !showAdminSection"
            class="w-full flex items-center justify-between text-left"
          >
            <div class="flex items-center">
              <ShieldCheckIcon class="w-5 h-5 text-gray-600 mr-2" />
              <h3 class="text-lg font-medium text-gray-900">Admin Controls</h3>
              <span class="ml-2 text-xs bg-red-100 text-red-800 px-2 py-1 rounded-full">Admin Only</span>
            </div>
            <ChevronDownIcon 
              :class="['w-5 h-5 text-gray-400 transition-transform', showAdminSection ? 'rotate-180' : '']" 
            />
          </button>
        </div>
        
        <div v-if="showAdminSection" class="card-body border-t">
          <div class="space-y-6">
            <!-- Agent Management -->
            <div>
              <h4 class="text-md font-medium text-gray-900 mb-4">Onboarding Agent Management</h4>
              
              <!-- Current Agent Status -->
              <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                <div class="flex items-center justify-between">
                  <div>
                    <div class="text-sm font-medium text-blue-900">Current Onboarding Agent</div>
                    <div class="text-sm text-blue-700 mt-1">
                      {{ currentOnboardingAgent ? currentOnboardingAgent.name : 'No agent configured' }}
                    </div>
                  </div>
                  <div class="flex items-center">
                    <div :class="['w-3 h-3 rounded-full mr-2', currentOnboardingAgent ? 'bg-green-500' : 'bg-red-500']"></div>
                    <span class="text-sm text-blue-700">{{ currentOnboardingAgent ? 'Active' : 'Inactive' }}</span>
                  </div>
                </div>
              </div>

              <!-- Create New Agent Form -->
              <div class="border rounded-lg p-4">
                <h5 class="text-sm font-medium text-gray-900 mb-3">Create New Onboarding Agent</h5>
                
                <form @submit.prevent="createOnboardingAgent" class="space-y-4">
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">Agent Name</label>
                      <input 
                        v-model="newAgentForm.name"
                        type="text" 
                        required
                        class="form-input"
                        placeholder="e.g., SOP Builder Assistant"
                      />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">Voice</label>
                      <select v-model="newAgentForm.voiceId" class="form-select">
                        <option value="11labs-Adrian">Adrian (Professional)</option>
                        <option value="11labs-Sarah">Sarah (Friendly)</option>
                        <option value="11labs-Michael">Michael (Authoritative)</option>
                        <option value="openai-alloy">Alloy (OpenAI)</option>
                        <option value="openai-echo">Echo (OpenAI)</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">System Prompt</label>
                    <textarea 
                      v-model="newAgentForm.prompt"
                      rows="6"
                      class="form-input"
                      placeholder="Enter the system prompt for the onboarding agent..."
                    ></textarea>
                    <p class="text-xs text-gray-500 mt-1">This prompt will guide how the agent conducts onboarding sessions</p>
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Onboarding Focus Areas</label>
                    <div class="grid grid-cols-2 md:grid-cols-3 gap-2 mt-2">
                      <label v-for="area in focusAreas" :key="area.value" class="flex items-center">
                        <input 
                          type="checkbox" 
                          :value="area.value"
                          v-model="newAgentForm.focusAreas"
                          class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                        />
                        <span class="ml-2 text-sm text-gray-700">{{ area.label }}</span>
                      </label>
                    </div>
                  </div>

                  <div class="flex items-center justify-between pt-4 border-t">
                    <div class="flex items-center">
                      <input 
                        v-model="newAgentForm.setAsDefault"
                        type="checkbox"
                        class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                      />
                      <span class="ml-2 text-sm text-gray-700">Set as default onboarding agent</span>
                    </div>
                    <button 
                      type="submit" 
                      :disabled="creatingAgent"
                      class="btn-primary"
                    >
                      <UserPlusIcon class="w-4 h-4 mr-2" />
                      {{ creatingAgent ? 'Creating...' : 'Create Agent' }}
                    </button>
                  </div>
                </form>
              </div>

              <!-- Existing Agents List -->
              <div class="mt-6">
                <h5 class="text-sm font-medium text-gray-900 mb-3">Existing Onboarding Agents</h5>
                <div v-if="onboardingAgents.length === 0" class="text-center py-4 text-gray-500">
                  No onboarding agents found. Create one above to get started.
                </div>
                <div v-else class="space-y-2">
                  <div 
                    v-for="agent in onboardingAgents" 
                    :key="agent.id"
                    class="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
                  >
                    <div class="flex items-center space-x-3">
                      <div :class="['w-3 h-3 rounded-full', agent.active ? 'bg-green-500' : 'bg-gray-400']"></div>
                      <div>
                        <div class="text-sm font-medium text-gray-900">{{ agent.name }}</div>
                        <div class="text-xs text-gray-500">Voice: {{ agent.voice_id || 'Default' }}</div>
                      </div>
                    </div>
                    <div class="flex items-center space-x-2">
                      <button 
                        @click="setDefaultAgent(agent)"
                        :class="[
                          'text-xs px-2 py-1 rounded',
                          agent.is_default ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                        ]"
                      >
                        {{ agent.is_default ? 'Default' : 'Set Default' }}
                      </button>
                      <button 
                        @click="editAgent(agent)"
                        class="text-blue-600 hover:text-blue-800"
                        title="Edit agent"
                      >
                        <PencilIcon class="w-4 h-4" />
                      </button>
                      <button 
                        @click="deleteAgent(agent)"
                        class="text-red-600 hover:text-red-800"
                        title="Delete agent"
                      >
                        <TrashIcon class="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Session Management -->
            <div class="border-t pt-6">
              <h4 class="text-md font-medium text-gray-900 mb-4">Session Management</h4>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="bg-gray-50 rounded-lg p-4 text-center">
                  <div class="text-2xl font-bold text-gray-900">{{ sessionStats.totalSessions }}</div>
                  <div class="text-xs text-gray-500">Total Sessions</div>
                </div>
                <div class="bg-gray-50 rounded-lg p-4 text-center">
                  <div class="text-2xl font-bold text-green-600">{{ sessionStats.activeSessions }}</div>
                  <div class="text-xs text-gray-500">Active Sessions</div>
                </div>
                <div class="bg-gray-50 rounded-lg p-4 text-center">
                  <div class="text-2xl font-bold text-blue-600">{{ sessionStats.completedSessions }}</div>
                  <div class="text-xs text-gray-500">Completed</div>
                </div>
              </div>
              
              <div class="flex justify-center space-x-3 mt-4">
                <button @click="refreshSessions" class="btn-secondary btn-sm">
                  <ArrowPathIcon class="w-3 h-3 mr-1" />
                  Refresh Stats
                </button>
                <button @click="exportAllSessions" class="btn-primary btn-sm">
                  <DocumentArrowDownIcon class="w-3 h-3 mr-1" />
                  Export All Sessions
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Global Conflict Alert -->
    <div v-if="conflictAlerts.size > 0" class="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <ExclamationTriangleIcon class="w-5 h-5 text-yellow-600 mr-3" />
          <div>
            <div class="text-sm font-medium text-yellow-800">Editing Conflicts Detected</div>
            <div class="text-sm text-yellow-700">{{ conflictAlerts.size }} section(s) are being edited by other users</div>
          </div>
        </div>
        <button @click="clearAllConflicts" class="text-sm bg-yellow-200 hover:bg-yellow-300 text-yellow-800 px-3 py-1 rounded">
          Dismiss All
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-3 gap-8">
      <!-- Left Column: Call Interface -->
      <div class="xl:col-span-1 space-y-6">
        <!-- Call Controls -->
        <div class="card">
          <div class="card-header">
            <h3 class="text-lg font-medium text-gray-900">Onboarding Assistant</h3>
            <p class="text-sm text-gray-500">Start a conversation to build your SOPs</p>
          </div>
          <div class="card-body space-y-4">
            <!-- Agent Info -->
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div class="flex items-center space-x-3">
                <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                  <UserIcon class="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <div class="font-medium text-gray-900">SOP Builder Assistant</div>
                  <div class="text-sm text-gray-600">Expert in business process documentation</div>
                </div>
              </div>
            </div>

            <!-- Call Button -->
            <button 
              @click="startOnboardingCall"
              :disabled="currentCall"
              class="btn-primary w-full"
            >
              <PhoneIcon class="w-4 h-4 mr-2" />
              {{ currentCall ? 'Call Active' : 'Start Onboarding Call' }}
            </button>

            <!-- End Call Button (appears when call is active) -->
            <div v-if="currentCall" class="text-center">
              <button 
                @click="endCall"
                class="btn-danger"
              >
                <PhoneXMarkIcon class="w-4 h-4 mr-2" />
                End Call
              </button>
            </div>

            <!-- Call Stats -->
            <div v-if="currentCall" class="text-center py-4 border-t">
              <div class="text-2xl font-bold text-gray-900">{{ formatDuration(callDuration) }}</div>
              <div class="text-sm text-gray-500">Call Duration</div>
            </div>
          </div>
        </div>

        <!-- Progress Overview -->
        <div class="card">
          <div class="card-header">
            <h3 class="text-lg font-medium text-gray-900">SOP Progress</h3>
            <p class="text-sm text-gray-500">Areas covered in your conversation</p>
          </div>
          <div class="card-body space-y-3">
            <div v-for="area in sopAreas" :key="area.id" class="flex items-center justify-between p-2 rounded-lg bg-gray-50">
              <div class="flex items-center space-x-2">
                <component :is="area.icon" class="w-4 h-4 text-gray-600" />
                <span class="text-sm font-medium text-gray-900">{{ area.name }}</span>
              </div>
              <div class="flex items-center space-x-2">
                <span class="text-xs text-gray-500">{{ area.items.length }} items</span>
                <div :class="[
                  'w-2 h-2 rounded-full',
                  area.items.length > 0 ? 'bg-green-500' : 'bg-gray-300'
                ]"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="card">
          <div class="card-header">
            <h3 class="text-lg font-medium text-gray-900">Quick Actions</h3>
          </div>
          <div class="card-body space-y-2">
            <button @click="exportSOPs" class="btn-secondary w-full text-sm">
              <DocumentArrowDownIcon class="w-4 h-4 mr-2" />
              Export SOPs
            </button>
            <button @click="clearProgress" class="btn-secondary w-full text-sm">
              <TrashIcon class="w-4 h-4 mr-2" />
              Clear Progress
            </button>
          </div>
        </div>

        <!-- Activity Feed -->
        <div v-if="connectedUsers.length > 0" class="card">
          <div class="card-header">
            <h3 class="text-lg font-medium text-gray-900">Activity Feed</h3>
            <p class="text-sm text-gray-500">Real-time collaboration updates</p>
          </div>
          <div class="card-body">
            <div class="space-y-2 max-h-40 overflow-y-auto">
              <!-- Connected Users List -->
              <div v-for="user in connectedUsers" :key="user.user_id" class="flex items-center justify-between text-xs">
                <div class="flex items-center">
                  <div class="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                  <span class="font-medium">{{ user.user_info.name }}</span>
                </div>
                <div class="text-gray-500">
                  {{ user.editing ? `Editing ${user.editing}` : 'Online' }}
                </div>
              </div>
              
              <!-- Editing Activity -->
              <div v-for="[field, userInfo] of editingUsers" :key="`editing-${field}`" class="flex items-center text-xs text-orange-600">
                <div class="w-2 h-2 bg-orange-500 rounded-full animate-pulse mr-2"></div>
                <span>{{ userInfo.user_id }} is editing {{ field.replace('_', ' ') }}</span>
              </div>
              
              <!-- Typing Activity -->
              <div v-for="[field, userInfo] of typingUsers" :key="`typing-${field}`" class="flex items-center text-xs text-blue-600">
                <div class="w-2 h-2 bg-blue-500 rounded-full animate-pulse mr-2"></div>
                <span>{{ userInfo.user_id }} is typing in {{ field.replace('_', ' ') }}</span>
              </div>
              
              <div v-if="connectedUsers.length === 0 && editingUsers.size === 0 && typingUsers.size === 0" class="text-center py-4">
                <div class="text-xs text-gray-500">No recent activity</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Middle Column: Live Transcript -->
      <div class="xl:col-span-1">
        <div class="card h-full">
          <div class="card-header">
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <h3 class="text-lg font-medium text-gray-900">Conversation</h3>
                <!-- Live indicator -->
                <div v-if="wsConnected" class="ml-2 flex items-center text-xs text-green-600">
                  <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse mr-1"></div>
                  Live
                </div>
              </div>
              <div class="flex items-center space-x-2">
                <button @click="clearTranscript" class="btn-sm btn-secondary">
                  <TrashIcon class="w-3 h-3 mr-1" />
                  Clear
                </button>
                <button @click="toggleAutoScroll" :class="['btn-sm', autoScroll ? 'btn-primary' : 'btn-secondary']">
                  <ArrowDownIcon class="w-3 h-3 mr-1" />
                  Auto-scroll
                </button>
              </div>
            </div>
          </div>
          <div class="card-body p-0">
            <div 
              ref="transcriptContainer"
              class="h-96 overflow-y-auto p-4 space-y-3"
              :class="{ 'bg-gray-50': !currentCall }"
            >
              <div v-if="!currentCall && transcript.length === 0" class="text-center py-12">
                <ChatBubbleLeftRightIcon class="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <p class="text-gray-500">Start a call to begin your onboarding conversation</p>
                <p class="text-sm text-gray-400 mt-2">The assistant will help you document your business processes</p>
              </div>
              
              <div v-for="message in transcript" :key="message.id" class="transcript-message">
                <div class="flex items-start space-x-3">
                  <div class="flex-shrink-0">
                    <div :class="[
                      'w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium',
                      message.speaker === 'agent' ? 'bg-blue-100 text-blue-800' : 
                      message.speaker === 'system' ? 'bg-green-100 text-green-800' : 
                      'bg-gray-100 text-gray-800'
                    ]">
                      {{ message.speaker === 'agent' ? 'AI' : 
                           message.speaker === 'system' ? 'SYS' : 'YOU' }}
                    </div>
                  </div>
                  <div class="flex-1">
                    <div class="flex items-center space-x-2 mb-1">
                      <span class="text-sm font-medium capitalize">{{ 
                        message.speaker === 'agent' ? 'SOP Assistant' : 
                        message.speaker === 'system' ? 'System' : 'You' 
                      }}</span>
                      <span class="text-xs text-gray-500">{{ formatTime(message.timestamp) }}</span>
                      <span v-if="message.sop_update" class="badge badge-success text-xs">SOP Update</span>
                      <span v-if="message.system" class="badge badge-blue text-xs">System</span>
                    </div>
                    <div :class="[
                      'text-sm',
                      message.system ? 'text-green-700 italic' : 'text-gray-900'
                    ]">{{ message.content }}</div>
                    
                    <!-- SOP Update Details -->
                    <div v-if="message.sop_update" class="mt-2 p-3 bg-green-50 rounded-lg border border-green-200">
                      <div class="font-medium text-green-900 text-sm">📋 SOP Updated: {{ message.sop_update.area }}</div>
                      <div class="text-green-700 text-sm mt-1">{{ message.sop_update.description }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Live SOP Builder -->
      <div class="xl:col-span-1">
        <div class="space-y-6">
          <!-- Organization Overview -->
          <div class="card">
            <div class="card-header">
              <h3 class="text-lg font-medium text-gray-900 flex items-center">
                <BuildingOfficeIcon class="w-5 h-5 mr-2 text-blue-600" />
                Organization Profile
                <!-- Editing indicator -->
                <div v-if="editingUsers.has('organization')" class="ml-auto flex items-center text-xs text-orange-600">
                  <div class="w-2 h-2 bg-orange-500 rounded-full animate-pulse mr-1"></div>
                  {{ editingUsers.get('organization').user_id }} editing...
                </div>
              </h3>
            </div>
            <div class="card-body">
              <!-- Conflict Alert -->
              <div v-if="conflictAlerts.has('organization')" class="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div class="flex items-center justify-between">
                  <div class="flex items-center">
                    <ExclamationTriangleIcon class="w-4 h-4 text-yellow-600 mr-2" />
                    <span class="text-sm text-yellow-800">{{ conflictAlerts.get('organization').message }}</span>
                  </div>
                  <div class="flex space-x-2">
                    <button @click="resolveConflict('organization', 'wait')" class="text-xs bg-yellow-200 hover:bg-yellow-300 text-yellow-800 px-2 py-1 rounded">
                      Wait
                    </button>
                    <button @click="resolveConflict('organization', 'force')" class="text-xs bg-red-200 hover:bg-red-300 text-red-800 px-2 py-1 rounded">
                      Force Edit
                    </button>
                  </div>
                </div>
              </div>
              
              <div v-if="orgProfile.name || orgProfile.industry || orgProfile.size" class="space-y-3">
                <div v-if="orgProfile.name">
                  <div class="text-sm font-medium text-gray-700">Company Name</div>
                  <div class="text-sm text-gray-900">{{ orgProfile.name }}</div>
                </div>
                <div v-if="orgProfile.industry">
                  <div class="text-sm font-medium text-gray-700">Industry</div>
                  <div class="text-sm text-gray-900">{{ orgProfile.industry }}</div>
                </div>
                <div v-if="orgProfile.size">
                  <div class="text-sm font-medium text-gray-700">Company Size</div>
                  <div class="text-sm text-gray-900">{{ orgProfile.size }}</div>
                </div>
                <div v-if="orgProfile.description">
                  <div class="text-sm font-medium text-gray-700">Description</div>
                  <div class="text-sm text-gray-900">{{ orgProfile.description }}</div>
                </div>
              </div>
              <div v-else class="text-center py-4">
                <BuildingOfficeIcon class="w-8 h-8 text-gray-300 mx-auto mb-2" />
                <p class="text-sm text-gray-500">Organization details will appear here as you chat</p>
              </div>
            </div>
          </div>

          <!-- MSP Integration -->
          <div class="card">
            <div class="card-header">
              <h3 class="text-lg font-medium text-gray-900 flex items-center">
                <CogIcon class="w-5 h-5 mr-2 text-purple-600" />
                MSP Integration
                <!-- Editing indicator -->
                <div v-if="editingUsers.has('msp_integration')" class="ml-auto flex items-center text-xs text-orange-600">
                  <div class="w-2 h-2 bg-orange-500 rounded-full animate-pulse mr-1"></div>
                  {{ editingUsers.get('msp_integration').user_id }} editing...
                </div>
              </h3>
            </div>
            <div class="card-body">
              <div v-if="mspIntegration.platform || mspIntegration.workflows.length > 0" class="space-y-3">
                <div v-if="mspIntegration.platform">
                  <div class="text-sm font-medium text-gray-700">Platform</div>
                  <div class="text-sm text-gray-900">{{ mspIntegration.platform }}</div>
                </div>
                <div v-if="mspIntegration.workflows.length > 0">
                  <div class="text-sm font-medium text-gray-700">Key Workflows</div>
                  <ul class="text-sm text-gray-900 space-y-1">
                    <li v-for="workflow in mspIntegration.workflows" :key="workflow.id" class="flex items-center">
                      <CheckCircleIcon class="w-3 h-3 text-green-500 mr-2" />
                      {{ workflow.name }}
                    </li>
                  </ul>
                </div>
              </div>
              <div v-else class="text-center py-4">
                <CogIcon class="w-8 h-8 text-gray-300 mx-auto mb-2" />
                <p class="text-sm text-gray-500">MSP integration details will appear here</p>
              </div>
            </div>
          </div>

          <!-- Internal Policies -->
          <div class="card">
            <div class="card-header">
              <h3 class="text-lg font-medium text-gray-900 flex items-center">
                <ShieldCheckIcon class="w-5 h-5 mr-2 text-green-600" />
                Internal Policies
                <!-- Editing indicator -->
                <div v-if="editingUsers.has('policies')" class="ml-auto flex items-center text-xs text-orange-600">
                  <div class="w-2 h-2 bg-orange-500 rounded-full animate-pulse mr-1"></div>
                  {{ editingUsers.get('policies').user_id }} editing...
                </div>
              </h3>
            </div>
            <div class="card-body">
              <div v-if="internalPolicies.length > 0" class="space-y-2">
                <div v-for="policy in internalPolicies" :key="policy.id" class="p-2 bg-gray-50 rounded">
                  <div class="text-sm font-medium text-gray-900">{{ policy.category }}</div>
                  <div class="text-sm text-gray-600">{{ policy.description }}</div>
                </div>
              </div>
              <div v-else class="text-center py-4">
                <ShieldCheckIcon class="w-8 h-8 text-gray-300 mx-auto mb-2" />
                <p class="text-sm text-gray-500">Internal policies will be documented here</p>
              </div>
            </div>
          </div>

          <!-- Escalation Procedures -->
          <div class="card">
            <div class="card-header">
              <h3 class="text-lg font-medium text-gray-900 flex items-center">
                <ExclamationTriangleIcon class="w-5 h-5 mr-2 text-yellow-600" />
                Escalation Procedures
                <!-- Editing indicator -->
                <div v-if="editingUsers.has('escalations')" class="ml-auto flex items-center text-xs text-orange-600">
                  <div class="w-2 h-2 bg-orange-500 rounded-full animate-pulse mr-1"></div>
                  {{ editingUsers.get('escalations').user_id }} editing...
                </div>
              </h3>
            </div>
            <div class="card-body">
              <div v-if="escalationProcedures.length > 0" class="space-y-2">
                <div v-for="procedure in escalationProcedures" :key="procedure.id" class="p-2 bg-yellow-50 rounded border border-yellow-200">
                  <div class="text-sm font-medium text-yellow-900">{{ procedure.trigger }}</div>
                  <div class="text-sm text-yellow-700">{{ procedure.action }}</div>
                </div>
              </div>
              <div v-else class="text-center py-4">
                <ExclamationTriangleIcon class="w-8 h-8 text-gray-300 mx-auto mb-2" />
                <p class="text-sm text-gray-500">Escalation procedures will be defined here</p>
              </div>
            </div>
          </div>

          <!-- Business Hours & Availability -->
          <div class="card">
            <div class="card-header">
              <h3 class="text-lg font-medium text-gray-900 flex items-center">
                <ClockIcon class="w-5 h-5 mr-2 text-indigo-600" />
                Business Hours
                <!-- Editing indicator -->
                <div v-if="editingUsers.has('business_hours')" class="ml-auto flex items-center text-xs text-orange-600">
                  <div class="w-2 h-2 bg-orange-500 rounded-full animate-pulse mr-1"></div>
                  {{ editingUsers.get('business_hours').user_id }} editing...
                </div>
              </h3>
            </div>
            <div class="card-body">
              <div v-if="businessHours.standard || businessHours.emergency" class="space-y-3">
                <div v-if="businessHours.standard">
                  <div class="text-sm font-medium text-gray-700">Standard Hours</div>
                  <div class="text-sm text-gray-900">{{ businessHours.standard }}</div>
                </div>
                <div v-if="businessHours.emergency">
                  <div class="text-sm font-medium text-gray-700">Emergency Support</div>
                  <div class="text-sm text-gray-900">{{ businessHours.emergency }}</div>
                </div>
                <div v-if="businessHours.timezone">
                  <div class="text-sm font-medium text-gray-700">Timezone</div>
                  <div class="text-sm text-gray-900">{{ businessHours.timezone }}</div>
                </div>
              </div>
              <div v-else class="text-center py-4">
                <ClockIcon class="w-8 h-8 text-gray-300 mx-auto mb-2" />
                <p class="text-sm text-gray-500">Business hours will be configured here</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useToast } from 'vue-toastification'
import api from '@/services/api'
import { useWebSocket } from '@/composables/useWebSocket'
import {
  PhoneIcon,
  PhoneXMarkIcon,
  UserIcon,
  ChatBubbleLeftRightIcon,
  TrashIcon,
  ArrowDownIcon,
  DocumentArrowDownIcon,
  BuildingOfficeIcon,
  CogIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  CheckCircleIcon,
  ChevronDownIcon,
  UserPlusIcon,
  PencilIcon,
  ArrowPathIcon
} from '@heroicons/vue/24/outline'

const toast = useToast()

// WebSocket setup
const {
  isConnected: wsConnected,
  connectionStatus: wsConnectionStatus,
  connect: connectWS,
  disconnect: disconnectWS,
  on: onWSMessage,
  startEditing,
  stopEditing,
  sendTyping,
  requestPresence
} = useWebSocket()

// Reactive state
const currentCall = ref(null)
const callDuration = ref(0)
const transcript = ref([])
const autoScroll = ref(true)
const connectionStatus = ref('disconnected')
const currentSession = ref(null)
const userId = ref('default-user') // In production, get from auth context

// Real-time collaboration state
const connectedUsers = ref([])
const editingUsers = ref(new Map()) // field -> user info
const typingUsers = ref(new Map()) // field -> user info
const lastActivity = ref(new Map()) // user_id -> timestamp
const conflictAlerts = ref(new Map()) // field -> conflict info

// Admin section state
const showAdminSection = ref(false)
const creatingAgent = ref(false)
const currentOnboardingAgent = ref(null)
const onboardingAgents = ref([])
const sessionStats = ref({
  totalSessions: 0,
  activeSessions: 0,
  completedSessions: 0
})

const newAgentForm = ref({
  name: '',
  voiceId: '11labs-Adrian',
  prompt: `You are an expert business process consultant helping organizations document their Standard Operating Procedures (SOPs). Your role is to:

1. Guide users through comprehensive business process discovery
2. Ask detailed questions about their operations, workflows, and procedures
3. Help identify gaps in current processes and suggest improvements
4. Document clear, actionable SOPs for different business areas
5. Understand organizational structure, roles, and responsibilities

Focus areas include:
- Customer service processes
- Sales and marketing workflows  
- IT support and technical procedures
- Administrative and operational tasks
- Emergency and escalation procedures
- MSP-specific workflows and tools

Be thorough, professional, and help create documentation that will improve their business operations.`,
  focusAreas: [],
  setAsDefault: false
})

const focusAreas = ref([
  { value: 'customer_service', label: 'Customer Service' },
  { value: 'sales_marketing', label: 'Sales & Marketing' },
  { value: 'it_support', label: 'IT Support' },
  { value: 'operations', label: 'Operations' },
  { value: 'emergency_procedures', label: 'Emergency Procedures' },
  { value: 'msp_workflows', label: 'MSP Workflows' },
  { value: 'compliance', label: 'Compliance' },
  { value: 'hr_processes', label: 'HR Processes' }
])

// SOP Data structures
const orgProfile = ref({
  name: '',
  industry: '',
  size: '',
  description: ''
})

const mspIntegration = ref({
  platform: '',
  workflows: []
})

const internalPolicies = ref([])

const escalationProcedures = ref([])

const businessHours = ref({
  standard: '',
  emergency: '',
  timezone: ''
})

// Computed properties for SOP areas
const organizationItems = computed(() => {
  const items = []
  if (orgProfile.value.name) items.push('Company Name')
  if (orgProfile.value.industry) items.push('Industry')
  if (orgProfile.value.size) items.push('Company Size')
  if (orgProfile.value.description) items.push('Description')
  return items
})

const mspItems = computed(() => {
  const items = []
  if (mspIntegration.value.platform) items.push('Platform')
  items.push(...mspIntegration.value.workflows.map(w => w.name))
  return items
})

const policiesItems = computed(() => internalPolicies.value.map(p => p.category))

const escalationItems = computed(() => escalationProcedures.value.map(p => p.trigger))

const businessHoursItems = computed(() => {
  const items = []
  if (businessHours.value.standard) items.push('Standard Hours')
  if (businessHours.value.emergency) items.push('Emergency Support')
  if (businessHours.value.timezone) items.push('Timezone')
  return items
})

// SOP Areas for progress tracking
const sopAreas = computed(() => [
  {
    id: 'organization',
    name: 'Organization',
    icon: BuildingOfficeIcon,
    items: organizationItems.value
  },
  {
    id: 'msp',
    name: 'MSP Integration',
    icon: CogIcon,
    items: mspItems.value
  },
  {
    id: 'policies',
    name: 'Internal Policies',
    icon: ShieldCheckIcon,
    items: policiesItems.value
  },
  {
    id: 'escalation',
    name: 'Escalation',
    icon: ExclamationTriangleIcon,
    items: escalationItems.value
  },
  {
    id: 'hours',
    name: 'Business Hours',
    icon: ClockIcon,
    items: businessHoursItems.value
  }
])

// UI refs
const transcriptContainer = ref(null)

// Call duration timer
let callTimer = null

// Methods
const startOnboardingCall = async () => {
  try {
    // Create or get existing session
    if (!currentSession.value) {
      const sessionResponse = await api.onboarding.createSession(userId.value)
      currentSession.value = sessionResponse.data
      loadSessionData(currentSession.value)
      
      // Connect to WebSocket for new session
      connectToSession()
    }
    
    // Start the call
    const callResponse = await api.onboarding.startCall(currentSession.value.id, userId.value)
    
    currentCall.value = {
      id: callResponse.data.call_id,
      type: 'onboarding',
      status: 'active',
      retell_call_id: callResponse.data.retell_call_id
    }
    
    callDuration.value = 0
    startCallTimer()
    connectionStatus.value = 'connected'
    
    // Add welcome message via API
    await api.onboarding.addTranscriptMessage(currentSession.value.id, {
      speaker: 'agent',
      content: "Hello! I'm your SOP building assistant. I'm here to help you document your business processes and create standard operating procedures. Let's start by learning about your organization. Can you tell me your company name and what industry you're in?",
      message_type: 'transcript'
    })
    
    // Refresh session data to get the new transcript message
    await refreshSessionData()
    
    // Start simulated conversation flow (in production, this would be real Retell AI)
    startSimulatedConversation()
    
    toast.success('Onboarding call started')
    
  } catch (error) {
    toast.error('Failed to start onboarding call: ' + error.message)
    console.error('Error starting onboarding call:', error)
  }
}

const endCall = async () => {
  if (currentCall.value && currentSession.value) {
    try {
      // End the call via API
      await api.onboarding.endCall(currentSession.value.id)
      
      currentCall.value = null
      stopCallTimer()
      connectionStatus.value = 'disconnected'
      
      // Refresh session data to get the final transcript message
      await refreshSessionData()
      
      toast.info('Call ended')
      
    } catch (error) {
      toast.error('Failed to end call: ' + error.message)
      console.error('Error ending call:', error)
    }
  }
}

const startCallTimer = () => {
  callTimer = setInterval(() => {
    callDuration.value++
  }, 1000)
}

const stopCallTimer = () => {
  if (callTimer) {
    clearInterval(callTimer)
    callTimer = null
  }
}

// Auto-scroll when transcript updates
watch(transcript, () => {
  if (autoScroll.value) {
    nextTick(() => {
      scrollToBottom()
    })
  }
}, { deep: true })

const scrollToBottom = () => {
  if (transcriptContainer.value) {
    transcriptContainer.value.scrollTop = transcriptContainer.value.scrollHeight
  }
}

const clearTranscript = () => {
  transcript.value = []
}

const toggleAutoScroll = () => {
  autoScroll.value = !autoScroll.value
  if (autoScroll.value) {
    nextTick(() => {
      scrollToBottom()
    })
  }
}

const formatDuration = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString()
}

// Session management methods
const loadSessionData = (sessionData) => {
  if (sessionData.organization) {
    orgProfile.value = { ...sessionData.organization }
  }
  if (sessionData.msp_integration) {
    mspIntegration.value = { ...sessionData.msp_integration }
  }
  if (sessionData.policies) {
    internalPolicies.value = [...sessionData.policies]
  }
  if (sessionData.escalations) {
    escalationProcedures.value = [...sessionData.escalations]
  }
  if (sessionData.business_hours) {
    businessHours.value = { ...sessionData.business_hours }
  }
  if (sessionData.transcript) {
    transcript.value = sessionData.transcript.map(msg => ({
      id: Date.now() + Math.random(),
      speaker: msg.speaker,
      content: msg.content,
      timestamp: new Date(msg.timestamp),
      system: msg.message_type === 'system',
      sop_update: msg.metadata?.sop_update,
      message_type: msg.message_type
    }))
  }
}

const refreshSessionData = async () => {
  if (currentSession.value) {
    try {
      const response = await api.onboarding.getSession(currentSession.value.id)
      currentSession.value = response.data
      loadSessionData(currentSession.value)
    } catch (error) {
      console.error('Error refreshing session data:', error)
    }
  }
}

const updateSOPData = async (area, data, description) => {
  if (currentSession.value) {
    try {
      // Check for editing conflicts before updating
      if (editingUsers.value.has(area)) {
        const editingUser = editingUsers.value.get(area)
        if (editingUser.user_id !== userId.value) {
          showConflictAlert(area, editingUser)
          return
        }
      }
      
      // Signal that we're editing this field
      startEditing(area)
      
      await api.onboarding.updateSOPData(currentSession.value.id, {
        area,
        data,
        description
      })
      
      // Refresh session data to get the updates
      await refreshSessionData()
      
      // Stop editing signal
      stopEditing()
      
    } catch (error) {
      console.error('Error updating SOP data:', error)
      stopEditing()
    }
  }
}

const showConflictAlert = (field, editingUser) => {
  conflictAlerts.value.set(field, {
    user_id: editingUser.user_id,
    timestamp: editingUser.timestamp,
    message: `${editingUser.user_id} is currently editing this section. Please wait or coordinate your changes.`
  })
  
  toast.warning(`Editing conflict: ${editingUser.user_id} is editing ${field}`)
  
  // Auto-clear conflict alert after 10 seconds
  setTimeout(() => {
    conflictAlerts.value.delete(field)
  }, 10000)
}

const resolveConflict = (field, action = 'wait') => {
  if (action === 'wait') {
    // Just clear the alert and let user try again later
    conflictAlerts.value.delete(field)
    toast.info('Please try editing again when the other user is finished')
  } else if (action === 'force') {
    // Force edit despite conflict (risky)
    conflictAlerts.value.delete(field)
    toast.warning('Forcing edit - this may overwrite changes from other users')
    startEditing(field)
  }
}

const clearAllConflicts = () => {
  conflictAlerts.value.clear()
}

// Simulated conversation flow
const startSimulatedConversation = () => {
  // Simulate user responses and SOP building
  const conversationFlow = [
    {
      delay: 8000,
      userMessage: "We're TechFix Solutions, a managed service provider specializing in IT support for small to medium businesses.",
      sopUpdate: {
        area: 'organization',
        data: {
          name: 'TechFix Solutions',
          industry: 'Managed Service Provider (MSP)',
          size: 'Small to Medium Business Focus'
        },
        description: 'Added company name and industry classification'
      }
    },
    {
      delay: 12000,
      agentMessage: "Great! TechFix Solutions it is. And I can see you focus on SMB clients. How many employees do you have, and what's your primary MSP platform - do you use ConnectWise, Syncro, or something else?"
    },
    {
      delay: 18000,
      userMessage: "We have about 15 employees and we use Syncro for our MSP management. We handle everything from help desk tickets to network monitoring.",
      sopUpdate: {
        area: 'organization',
        data: {
          name: 'TechFix Solutions',
          industry: 'Managed Service Provider (MSP)',
          size: '15 employees',
          description: 'IT support for small to medium businesses'
        },
        description: 'Updated company size and added description'
      },
      sopUpdate2: {
        area: 'msp_integration',
        data: {
          platform: 'Syncro',
          workflows: [
            { id: 1, name: 'Help Desk Ticketing', description: 'Customer support ticket management' },
            { id: 2, name: 'Network Monitoring', description: 'Proactive network monitoring and alerts' }
          ]
        },
        description: 'Documented Syncro platform usage and core services'
      }
    },
    {
      delay: 25000,
      agentMessage: "Perfect! Now let's talk about your business hours and escalation procedures. What are your standard support hours, and how do you handle after-hours emergencies?"
    },
    {
      delay: 32000,
      userMessage: "We're open Monday through Friday, 8 AM to 6 PM Eastern. For emergencies, we have an on-call rotation where critical issues get escalated to our senior techs within 15 minutes.",
      sopUpdate: {
        area: 'business_hours',
        data: {
          standard: 'Monday-Friday, 8 AM - 6 PM',
          emergency: 'On-call rotation for critical issues',
          timezone: 'Eastern Time'
        },
        description: 'Defined standard hours and emergency support'
      },
      sopUpdate2: {
        area: 'escalations',
        data: {
          escalations: [
            {
              trigger: 'Critical issues after hours',
              action: 'Escalate to senior tech within 15 minutes',
              priority: 'high'
            }
          ]
        },
        description: 'Added emergency escalation procedure'
      }
    }
  ]

  // Execute conversation flow
  conversationFlow.forEach((step, index) => {
    setTimeout(async () => {
      if (!currentCall.value || !currentSession.value) return // Stop if call was ended
      
      try {
        if (step.userMessage) {
          await api.onboarding.addTranscriptMessage(currentSession.value.id, {
            speaker: 'human',
            content: step.userMessage,
            message_type: 'transcript'
          })
        }
        
        if (step.agentMessage) {
          await api.onboarding.addTranscriptMessage(currentSession.value.id, {
            speaker: 'agent',
            content: step.agentMessage,
            message_type: 'transcript'
          })
        }
        
        // Update SOP data via API
        if (step.sopUpdate) {
          await updateSOPData(step.sopUpdate.area, step.sopUpdate.data, step.sopUpdate.description)
        }
        
        // Handle second SOP update if present (for the complex step)
        if (step.sopUpdate2) {
          await updateSOPData(step.sopUpdate2.area, step.sopUpdate2.data, step.sopUpdate2.description)
        }
        
        // Refresh session data to get updates
        await refreshSessionData()
        
      } catch (error) {
        console.error('Error in simulated conversation:', error)
      }
      
    }, step.delay)
  })
}

const exportSOPs = async () => {
  if (!currentSession.value) {
    toast.error('No active session to export')
    return
  }
  
  try {
    const response = await api.onboarding.exportSOPs(currentSession.value.id)
    const sopDocument = response.data
    
    // Create and download JSON file
    const dataStr = JSON.stringify(sopDocument, null, 2)
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
    
    const exportFileDefaultName = `${sopDocument.organization?.name || 'organization'}-sops.json`
    
    const linkElement = document.createElement('a')
    linkElement.setAttribute('href', dataUri)
    linkElement.setAttribute('download', exportFileDefaultName)
    linkElement.click()
    
    toast.success('SOPs exported successfully')
    
  } catch (error) {
    toast.error('Failed to export SOPs: ' + error.message)
    console.error('Error exporting SOPs:', error)
  }
}

const clearProgress = async () => {
  if (confirm('Are you sure you want to clear all SOP progress? This cannot be undone.')) {
    try {
      if (currentSession.value) {
        // Delete the current session
        await api.onboarding.deleteSession(currentSession.value.id)
        currentSession.value = null
      }
      
      // Reset all local SOP data
      orgProfile.value = { name: '', industry: '', size: '', description: '' }
      mspIntegration.value = { platform: '', workflows: [] }
      internalPolicies.value = []
      escalationProcedures.value = []
      businessHours.value = { standard: '', emergency: '', timezone: '' }
      
      // Clear transcript
      transcript.value = []
      
      // End call if active
      if (currentCall.value) {
        currentCall.value = null
        stopCallTimer()
        connectionStatus.value = 'disconnected'
      }
      
      toast.success('All progress cleared')
      
    } catch (error) {
      toast.error('Failed to clear progress: ' + error.message)
      console.error('Error clearing progress:', error)
    }
  }
}

// WebSocket event handlers
const setupWebSocketHandlers = () => {
  // User presence events
  onWSMessage('user_connected', (data) => {
    console.log('User connected:', data.user_id)
    connectedUsers.value.push({
      user_id: data.user_id,
      user_info: data.user_info,
      connected_at: data.timestamp,
      editing: null
    })
    toast.info(`${data.user_info.name} joined the session`)
  })
  
  onWSMessage('user_disconnected', (data) => {
    console.log('User disconnected:', data.user_id)
    connectedUsers.value = connectedUsers.value.filter(u => u.user_id !== data.user_id)
    editingUsers.value.delete(data.user_id)
    typingUsers.value.delete(data.user_id)
    toast.info(`User ${data.user_id} left the session`)
  })
  
  onWSMessage('session_presence', (data) => {
    console.log('Session presence:', data.users)
    connectedUsers.value = data.users
  })
  
  // Editing and typing events
  onWSMessage('user_editing', (data) => {
    if (data.field) {
      editingUsers.value.set(data.field, {
        user_id: data.user_id,
        timestamp: data.timestamp
      })
    } else {
      // User stopped editing - remove from all fields
      for (const [field, userInfo] of editingUsers.value.entries()) {
        if (userInfo.user_id === data.user_id) {
          editingUsers.value.delete(field)
        }
      }
    }
  })
  
  onWSMessage('user_typing', (data) => {
    if (data.field) {
      typingUsers.value.set(data.field, {
        user_id: data.user_id,
        content: data.content,
        timestamp: data.timestamp
      })
      
      // Clear typing indicator after 3 seconds
      setTimeout(() => {
        const current = typingUsers.value.get(data.field)
        if (current && current.user_id === data.user_id && current.timestamp === data.timestamp) {
          typingUsers.value.delete(data.field)
        }
      }, 3000)
    }
  })
  
  // Real-time data updates
  onWSMessage('transcript_update', (data) => {
    console.log('Real-time transcript update:', data.message)
    const message = data.message
    transcript.value.push({
      id: message.id || Date.now() + Math.random(),
      speaker: message.speaker,
      content: message.content,
      timestamp: new Date(message.timestamp),
      system: message.system || message.message_type === 'system',
      sop_update: message.sop_update,
      message_type: message.message_type
    })
  })
  
  onWSMessage('sop_updated', (data) => {
    console.log('Real-time SOP update:', data)
    toast.success(`SOP Updated: ${data.description}`)
    
    // Refresh session data to get the latest updates
    refreshSessionData()
  })
  
  onWSMessage('call_started', (data) => {
    console.log('Real-time call started:', data)
    if (!currentCall.value) {
      currentCall.value = {
        id: data.call_id,
        type: 'onboarding',
        status: 'active',
        retell_call_id: data.retell_call_id
      }
      startCallTimer()
      connectionStatus.value = 'connected'
    }
  })
  
  onWSMessage('call_ended', (data) => {
    console.log('Real-time call ended:', data)
    if (currentCall.value) {
      stopCallTimer()
      currentCall.value = null
      connectionStatus.value = 'disconnected'
    }
  })
  
  onWSMessage('session_updated', (data) => {
    console.log('Real-time session update:', data)
    // Refresh session data
    refreshSessionData()
  })
}

// Connect to WebSocket when session is available
const connectToSession = () => {
  if (currentSession.value && !wsConnected.value) {
    const wsUrl = api.onboarding.getWebSocketUrl(currentSession.value.id)
    connectWS(wsUrl, userId.value)
    
    // Request current presence after connection
    setTimeout(() => {
      if (wsConnected.value) {
        requestPresence()
      }
    }, 1000)
  }
}

// Initialize on component mount
// Admin Methods
const createOnboardingAgent = async () => {
  creatingAgent.value = true
  try {
    const agentData = {
      name: newAgentForm.value.name,
      voice_id: newAgentForm.value.voiceId,
      prompt: newAgentForm.value.prompt,
      focus_areas: newAgentForm.value.focusAreas,
      is_default: newAgentForm.value.setAsDefault,
      type: 'onboarding'
    }
    
    const response = await api.agents.create(agentData)
    
    // Add to local list
    onboardingAgents.value.push(response.data)
    
    // If set as default, update current agent
    if (newAgentForm.value.setAsDefault) {
      currentOnboardingAgent.value = response.data
      // Unset other agents as default
      onboardingAgents.value.forEach(agent => {
        if (agent.id !== response.data.id) {
          agent.is_default = false
        }
      })
    }
    
    // Reset form
    resetAgentForm()
    
    toast.success(`Onboarding agent "${response.data.name}" created successfully`)
    
  } catch (error) {
    toast.error('Failed to create onboarding agent: ' + (error.response?.data?.detail || error.message))
  } finally {
    creatingAgent.value = false
  }
}

const resetAgentForm = () => {
  newAgentForm.value = {
    name: '',
    voiceId: '11labs-Adrian',
    prompt: `You are an expert business process consultant helping organizations document their Standard Operating Procedures (SOPs). Your role is to:

1. Guide users through comprehensive business process discovery
2. Ask detailed questions about their operations, workflows, and procedures
3. Help identify gaps in current processes and suggest improvements
4. Document clear, actionable SOPs for different business areas
5. Understand organizational structure, roles, and responsibilities

Focus areas include:
- Customer service processes
- Sales and marketing workflows  
- IT support and technical procedures
- Administrative and operational tasks
- Emergency and escalation procedures
- MSP-specific workflows and tools

Be thorough, professional, and help create documentation that will improve their business operations.`,
    focusAreas: [],
    setAsDefault: false
  }
}

const setDefaultAgent = async (agent) => {
  try {
    // Update via API
    await api.agents.update(agent.id, { is_default: true })
    
    // Update local state
    onboardingAgents.value.forEach(a => {
      a.is_default = a.id === agent.id
    })
    
    currentOnboardingAgent.value = agent
    toast.success(`${agent.name} set as default onboarding agent`)
    
  } catch (error) {
    toast.error('Failed to set default agent: ' + (error.response?.data?.detail || error.message))
  }
}

const editAgent = (agent) => {
  // Populate form with agent data for editing
  newAgentForm.value = {
    name: agent.name,
    voiceId: agent.voice_id || '11labs-Adrian',
    prompt: agent.prompt || '',
    focusAreas: agent.focus_areas || [],
    setAsDefault: agent.is_default || false
  }
  
  // Scroll to form
  const form = document.querySelector('.card-body form')
  if (form) {
    form.scrollIntoView({ behavior: 'smooth' })
  }
  
  toast.info('Agent data loaded for editing')
}

const deleteAgent = async (agent) => {
  if (!confirm(`Are you sure you want to delete the agent "${agent.name}"?`)) {
    return
  }
  
  try {
    await api.agents.delete(agent.id)
    
    // Remove from local list
    onboardingAgents.value = onboardingAgents.value.filter(a => a.id !== agent.id)
    
    // If this was the current agent, clear it
    if (currentOnboardingAgent.value?.id === agent.id) {
      currentOnboardingAgent.value = null
    }
    
    toast.success(`Agent "${agent.name}" deleted successfully`)
    
  } catch (error) {
    toast.error('Failed to delete agent: ' + (error.response?.data?.detail || error.message))
  }
}

const loadOnboardingAgents = async () => {
  try {
    const response = await api.agents.list({ type: 'onboarding' })
    onboardingAgents.value = response.data
    
    // Find current default agent
    currentOnboardingAgent.value = onboardingAgents.value.find(agent => agent.is_default) || null
    
  } catch (error) {
    console.error('Failed to load onboarding agents:', error)
    // Use mock data for development
    onboardingAgents.value = [
      {
        id: 1,
        name: 'SOP Builder Assistant',
        voice_id: '11labs-Adrian',
        active: true,
        is_default: true,
        type: 'onboarding'
      }
    ]
    currentOnboardingAgent.value = onboardingAgents.value[0]
  }
}

const refreshSessions = async () => {
  try {
    const response = await api.onboarding.listSessions()
    const sessions = response.data
    
    sessionStats.value = {
      totalSessions: sessions.length,
      activeSessions: sessions.filter(s => s.status === 'active').length,
      completedSessions: sessions.filter(s => s.status === 'completed').length
    }
    
    toast.success('Session statistics refreshed')
    
  } catch (error) {
    console.error('Failed to refresh sessions:', error)
    // Use mock data
    sessionStats.value = {
      totalSessions: 12,
      activeSessions: 2,
      completedSessions: 10
    }
  }
}

const exportAllSessions = async () => {
  try {
    // In a real implementation, this would generate and download a comprehensive report
    toast.info('Export functionality coming soon - will include all session SOPs and transcripts')
    
  } catch (error) {
    toast.error('Failed to export sessions: ' + error.message)
  }
}

onMounted(async () => {
  connectionStatus.value = 'connected'
  
  // Load admin data
  await loadOnboardingAgents()
  await refreshSessions()
  
  // Setup WebSocket handlers
  setupWebSocketHandlers()
  
  // Try to load existing session for this user
  try {
    const sessionsResponse = await api.onboarding.listSessions({ 
      user_id: userId.value, 
      status: 'active', 
      limit: 1 
    })
    
    if (sessionsResponse.data.length > 0) {
      currentSession.value = sessionsResponse.data[0]
      loadSessionData(currentSession.value)
      
      // Connect to WebSocket
      connectToSession()
      
      // If there's an active call, restore call state
      if (currentSession.value.status === 'call_active') {
        currentCall.value = {
          id: currentSession.value.retell_call_id,
          type: 'onboarding',
          status: 'active',
          retell_call_id: currentSession.value.retell_call_id
        }
        startCallTimer()
      }
    }
  } catch (error) {
    console.error('Error loading existing session:', error)
    // Continue without existing session
  }
})

onUnmounted(() => {
  if (callTimer) {
    clearInterval(callTimer)
  }
  
  // Disconnect WebSocket
  disconnectWS()
})
</script>

<style scoped>
.transcript-message {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.form-input, .form-select {
  @apply block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm;
}

.btn-sm {
  @apply px-2.5 py-1.5 text-xs font-medium rounded;
}

.badge {
  @apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium;
}

.badge-success {
  @apply bg-green-100 text-green-800;
}

.badge-blue {
  @apply bg-blue-100 text-blue-800;
}
</style> 