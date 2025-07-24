<template>
  <div class="w-full px-4 sm:px-6 lg:px-8">
    <!-- Page Header -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">E2E Agent Tuning</h1>
          <p class="mt-2 text-gray-600">Test agents live and tune prompts in real-time</p>
        </div>
        <div class="flex items-center space-x-4">
          <div class="flex items-center">
            <div :class="['w-3 h-3 rounded-full mr-2', connectionStatus === 'connected' ? 'bg-green-500' : 'bg-red-500']"></div>
            <span class="text-sm text-gray-600">{{ connectionStatus === 'connected' ? 'Connected' : 'Disconnected' }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Left Column: Controls -->
      <div class="lg:col-span-1 space-y-6">
        <!-- Call Controls -->
        <div class="card">
          <div class="card-header">
            <h3 class="text-lg font-medium text-gray-900">Call Controls</h3>
            <p class="text-sm text-gray-500">Choose your call type and configure accordingly</p>
          </div>
          <div class="card-body space-y-6">
            
            <!-- Phone Call Section -->
            <div class="border rounded-lg p-4 bg-blue-50 border-blue-200">
              <h4 class="text-md font-medium text-gray-900 mb-3 flex items-center">
                <PhoneIcon class="w-4 h-4 mr-2 text-blue-600" />
                Phone Call
              </h4>
              <div class="space-y-3">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Agent</label>
                  <select v-model="phoneCallAgent" class="form-select w-full" :disabled="currentCall">
                    <option value="">Choose an agent...</option>
                    <option v-for="agent in agents" :key="agent.id" :value="agent">
                      {{ agent.name }}
                    </option>
                  </select>
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Phone Number to Call</label>
                  <input 
                    v-model="phoneNumber" 
                    type="tel" 
                    placeholder="+1 (555) 123-4567"
                    class="form-input w-full"
                    :disabled="currentCall"
                  />
                </div>
                
                <button 
                  @click="startPhoneCall"
                  :disabled="!phoneCallAgent || !phoneNumber || currentCall"
                  class="btn-primary w-full"
                >
                  <PhoneIcon class="w-4 h-4 mr-2" />
                  {{ currentCall ? 'Call Active' : 'Start Phone Call' }}
                </button>
              </div>
            </div>

            <!-- Agent-to-Agent Call Section -->
            <div class="border rounded-lg p-4 bg-purple-50 border-purple-200">
              <h4 class="text-md font-medium text-gray-900 mb-3 flex items-center">
                <ChatBubbleLeftRightIcon class="w-4 h-4 mr-2 text-purple-600" />
                Agent-to-Agent Call
              </h4>
              <div class="space-y-3">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Receiving Agent (Inbound)</label>
                  <select v-model="receivingAgent" class="form-select w-full" :disabled="currentCall">
                    <option value="">Choose receiving agent...</option>
                    <option v-for="agent in agents" :key="agent.id" :value="agent">
                      {{ agent.name }}
                    </option>
                  </select>
                  <p class="text-xs text-gray-500 mt-1">This agent will receive the call</p>
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Calling Agent (Outbound)</label>
                  <select v-model="callingAgent" class="form-select w-full" :disabled="currentCall">
                    <option value="">Choose calling agent...</option>
                    <option v-for="agent in agents.filter(a => a.id !== receivingAgent?.id)" :key="agent.id" :value="agent">
                      {{ agent.name }}
                    </option>
                  </select>
                  <p class="text-xs text-gray-500 mt-1">This agent will make the call</p>
                </div>
                
                <button 
                  @click="startAgentToAgentCall"
                  :disabled="!receivingAgent || !callingAgent || currentCall"
                  class="btn-primary w-full"
                >
                  <ChatBubbleLeftRightIcon class="w-4 h-4 mr-2" />
                  {{ currentCall ? 'Call Active' : 'Start Agent Call' }}
                </button>
              </div>
            </div>

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
          </div>
        </div>

        <!-- Quick Stats -->
        <div class="card">
          <div class="card-header">
            <h3 class="text-lg font-medium text-gray-900">Session Stats</h3>
          </div>
          <div class="card-body">
            <div class="grid grid-cols-2 gap-4 text-center">
              <div>
                <div class="text-2xl font-bold text-gray-900">{{ sessionStats.totalCalls }}</div>
                <div class="text-xs text-gray-500">Total Calls</div>
              </div>
              <div>
                <div class="text-2xl font-bold text-gray-900">{{ sessionStats.avgDuration }}s</div>
                <div class="text-xs text-gray-500">Avg Duration</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Routing Rules -->
        <div class="card">
          <div class="card-header">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-medium text-gray-900">Routing Rules</h3>
              <button @click="showRoutingModal = true" class="btn-primary btn-sm">
                <PlusIcon class="w-3 h-3 mr-1" />
                Add
              </button>
            </div>
          </div>
          <div class="card-body">
            <!-- Current Status -->
            <div class="bg-gray-50 rounded-lg p-3 mb-4">
              <h4 class="text-sm font-medium text-gray-900 mb-2">Current Status</h4>
              <div class="space-y-1 text-xs">
                <div class="flex justify-between">
                  <span class="text-gray-600">Time:</span>
                  <span class="font-medium">{{ currentTime }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Hours:</span>
                  <span :class="isBusinessHours ? 'text-green-600' : 'text-red-600'" class="font-medium">
                    {{ isBusinessHours ? 'Open' : 'Closed' }}
                  </span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Active:</span>
                  <span class="font-medium">{{ activeRoutingRule?.name || 'Default' }}</span>
                </div>
                <div v-if="getCurrentActivePromptConfig()" class="mt-2 pt-2 border-t border-gray-200">
                  <div class="text-xs text-blue-600 font-medium mb-1">Current Prompt Config</div>
                  <div class="text-xs text-gray-700">
                    {{ getCurrentActivePromptConfig()?.promptConfig?.systemPrompt || 'Standard' }}
                  </div>
                  <div class="text-xs text-gray-500 mt-1">
                    {{ getCurrentActivePromptConfig()?.promptConfig?.promptPriority || 'default' }} priority
                  </div>
                </div>
              </div>
            </div>

            <!-- Quick Route Test -->
            <div class="space-y-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Test Routing</label>
                <select v-model="testRequestType" class="form-select w-full text-sm">
                  <option value="">Select request type...</option>
                  <option value="sales">Sales</option>
                  <option value="support">Support</option>
                  <option value="billing">Billing</option>
                  <option value="general">General</option>
                  <option value="emergency">Emergency</option>
                </select>
              </div>
              <div v-if="testRequestType" class="p-2 bg-blue-50 rounded border text-xs">
                <div class="text-gray-600">Routes to:</div>
                <div class="font-medium">{{ getRoutingDestination(testRequestType) }}</div>
              </div>
            </div>

            <!-- Active Rules Summary -->
            <div class="mt-4">
              <div class="flex items-center justify-between mb-2">
                <div class="text-sm font-medium text-gray-900">Active Rules ({{ routingRules.filter(r => r.active).length }})</div>
                <button 
                  @click="loadDefaultRoutingRules" 
                  class="text-xs text-blue-600 hover:text-blue-800"
                  title="Load default routing rules with prompt configurations"
                >
                  Load Defaults
                </button>
              </div>
              <div class="space-y-2">
                <div v-for="rule in routingRules.filter(r => r.active).slice(0, 3)" :key="rule.id" class="text-xs border rounded p-2 bg-gray-50">
                  <div class="flex justify-between items-start mb-1">
                    <span class="text-gray-600 truncate font-medium">{{ rule.name }}</span>
                    <span :class="getRequestTypeBadge(rule.requestType)" class="badge text-xs ml-1">{{ rule.requestType }}</span>
                  </div>
                  <div class="text-gray-900 font-medium mb-1">{{ rule.targetAgent.name }}</div>
                  <div v-if="rule.promptConfig" class="text-xs text-blue-600">
                    <div class="flex items-center">
                      <span class="w-2 h-2 bg-blue-400 rounded-full mr-1"></span>
                      {{ rule.promptConfig.systemPrompt }}
                    </div>
                    <div class="text-gray-500 mt-1">
                      {{ Object.keys(rule.promptConfig.contextPrompts || {}).length }} context prompts
                    </div>
                  </div>
                  <div class="text-xs text-gray-500 mt-1">
                    Priority: {{ rule.priority }} | {{ rule.timeCondition.days.join(', ') }}
                  </div>
                </div>
                <div v-if="routingRules.filter(r => r.active).length > 3" class="text-xs text-gray-500 text-center">
                  +{{ routingRules.filter(r => r.active).length - 3 }} more rules
                </div>
                <div v-if="routingRules.filter(r => r.active).length === 0" class="text-xs text-gray-500 text-center py-4">
                  <div class="mb-2">No active rules</div>
                  <button 
                    @click="loadDefaultRoutingRules" 
                    class="text-blue-600 hover:text-blue-800 font-medium"
                  >
                    Load Default Rules
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Middle Column: Live Transcript -->
      <div class="lg:col-span-1">
        <div class="card h-full">
          <div class="card-header">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-medium text-gray-900">Live Transcript</h3>
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
                <p class="text-gray-500">Start a call to see live transcript</p>
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
                           message.speaker === 'system' ? 'SYS' : 'H' }}
                    </div>
                  </div>
                  <div class="flex-1">
                    <div class="flex items-center space-x-2 mb-1">
                      <span class="text-sm font-medium capitalize">{{ message.speaker }}</span>
                      <span class="text-xs text-gray-500">{{ formatTime(message.timestamp) }}</span>
                      <span v-if="message.tool_call" class="badge badge-primary text-xs">Tool Call</span>
                      <span v-if="message.system" class="badge badge-success text-xs">System</span>
                      <span v-if="message.streaming" class="badge badge-blue text-xs">Live</span>
                    </div>
                    <div :class="[
                      'text-sm',
                      message.system ? 'text-green-700 italic' : 'text-gray-900'
                    ]">{{ message.content }}</div>
                    
                    <!-- Tool Call Details -->
                    <div v-if="message.tool_call" class="mt-2 p-2 bg-blue-50 rounded text-xs">
                      <div class="font-medium text-blue-900">{{ message.tool_call.function_name }}</div>
                      <div class="text-blue-700 mt-1">{{ JSON.stringify(message.tool_call.parameters, null, 2) }}</div>
                      <div v-if="message.tool_call.result" class="text-green-700 mt-1 pt-1 border-t border-blue-200">
                        <div class="font-medium">Result:</div>
                        <div>{{ JSON.stringify(message.tool_call.result, null, 2) }}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Interim Transcripts (Real-time partial transcripts) -->
              <div v-for="[speaker, interim] in interimTranscripts" :key="'interim-' + speaker" class="transcript-message interim">
                <div class="flex items-start space-x-3 opacity-60">
                  <div class="flex-shrink-0">
                    <div :class="[
                      'w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium border-2 border-dashed',
                      speaker === 'agent' ? 'bg-blue-50 text-blue-600 border-blue-300' : 
                      'bg-gray-50 text-gray-600 border-gray-300'
                    ]">
                      {{ speaker === 'agent' ? 'AI' : 'H' }}
                    </div>
                  </div>
                  <div class="flex-1">
                    <div class="flex items-center space-x-2 mb-1">
                      <span class="text-sm font-medium capitalize text-gray-500">{{ speaker }}</span>
                      <span class="text-xs text-gray-400">{{ formatTime(interim.timestamp) }}</span>
                      <span class="badge bg-yellow-100 text-yellow-800 text-xs">Interim</span>
                    </div>
                    <div class="text-sm text-gray-600 italic">{{ interim.content }}</div>
                  </div>
                </div>
              </div>
              
              <!-- Speech Detection Indicators -->
              <div v-for="[speaker, detected] in speechDetected" :key="'speech-' + speaker" class="transcript-message speech-indicator">
                <div class="flex items-start space-x-3">
                  <div class="flex-shrink-0">
                    <div :class="[
                      'w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium animate-pulse',
                      speaker === 'agent' ? 'bg-blue-200 text-blue-800' : 'bg-gray-200 text-gray-800'
                    ]">
                      {{ speaker === 'agent' ? 'AI' : 'H' }}
                    </div>
                  </div>
                  <div class="flex-1">
                    <div class="flex items-center space-x-2 mb-1">
                      <span class="text-sm font-medium capitalize">{{ speaker }}</span>
                      <span class="badge bg-orange-100 text-orange-800 text-xs">Speaking...</span>
                    </div>
                    <div class="flex space-x-1">
                      <div class="w-2 h-2 bg-orange-400 rounded-full animate-bounce"></div>
                      <div class="w-2 h-2 bg-orange-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                      <div class="w-2 h-2 bg-orange-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Prompt Editor -->
      <div class="lg:col-span-1">
        <div class="card h-full">
          <div class="card-header">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-medium text-gray-900">Prompt Editor</h3>
              <div class="flex items-center space-x-2">
                <button 
                  @click="savePrompt"
                  :disabled="!selectedAgent || !promptModified"
                  class="btn-sm btn-primary"
                >
                  <DocumentCheckIcon class="w-3 h-3 mr-1" />
                  Save
                </button>
                <button @click="resetPrompt" class="btn-sm btn-secondary">
                  <ArrowPathIcon class="w-3 h-3 mr-1" />
                  Reset
                </button>
              </div>
            </div>
          </div>
          <div class="card-body p-0">
            <div v-if="!selectedAgent" class="p-4 text-center py-12">
              <DocumentTextIcon class="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p class="text-gray-500">Select an agent to edit its prompt</p>
            </div>
            
            <div v-else class="h-96">
              <textarea
                v-model="editedPrompt"
                class="w-full h-full p-4 border-0 resize-none focus:ring-0 text-sm font-mono"
                placeholder="Enter your agent prompt here..."
                @input="onPromptChange"
              ></textarea>
            </div>
            
            <div v-if="promptModified" class="px-4 py-2 bg-yellow-50 border-t">
              <div class="flex items-center text-sm text-yellow-800">
                <ExclamationTriangleIcon class="w-4 h-4 mr-2" />
                Prompt has unsaved changes
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Created Tickets -->
    <div class="mt-8">
      <div class="card">
        <div class="card-header">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-lg font-medium text-gray-900">Created Tickets</h3>
              <p class="text-sm text-gray-500">Tickets generated during call sessions</p>
            </div>
            <div class="flex items-center space-x-2">
              <span class="text-sm text-gray-600">{{ createdTickets.length }} tickets</span>
              <button @click="clearTickets" v-if="createdTickets.length > 0" class="btn-sm btn-secondary">
                <TrashIcon class="w-3 h-3 mr-1" />
                Clear All
              </button>
            </div>
          </div>
        </div>
        <div class="card-body">
          <div v-if="createdTickets.length === 0" class="text-center py-8">
            <ClipboardDocumentIcon class="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p class="text-gray-500">No tickets created yet</p>
            <p class="text-sm text-gray-400 mt-2">Start a call and use ticket creation tools to see results here</p>
          </div>
          
          <div v-else class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
            <div 
              v-for="ticket in createdTickets" 
              :key="ticket.id"
              class="border rounded-lg p-4 hover:shadow-md transition-shadow"
              :class="getTicketBorderClass(ticket.priority)"
            >
              <!-- Ticket Header -->
              <div class="flex items-start justify-between mb-3">
                <div>
                  <div class="flex items-center space-x-2 mb-1">
                    <span class="text-sm font-medium text-gray-900">Ticket #{{ ticket.id }}</span>
                    <span :class="getTicketStatusBadge(ticket.status)" class="badge text-xs">
                      {{ ticket.status }}
                    </span>
                  </div>
                  <div class="text-xs text-gray-500">
                    Created {{ formatTime(ticket.createdAt) }}
                  </div>
                </div>
                <div class="flex items-center space-x-1">
                  <span :class="getPriorityBadge(ticket.priority)" class="badge text-xs">
                    {{ ticket.priority }}
                  </span>
                  <button 
                    @click="viewTicketDetails(ticket)"
                    class="text-gray-400 hover:text-gray-600"
                  >
                    <EyeIcon class="w-4 h-4" />
                  </button>
                </div>
              </div>

              <!-- Ticket Content -->
              <div class="space-y-2">
                <div>
                  <div class="text-sm font-medium text-gray-900 line-clamp-2">
                    {{ ticket.subject }}
                  </div>
                </div>
                
                <div class="text-xs text-gray-600 line-clamp-3">
                  {{ ticket.description }}
                </div>

                <!-- Customer Info -->
                <div v-if="ticket.customer" class="pt-2 border-t border-gray-100">
                  <div class="text-xs text-gray-500">Customer:</div>
                  <div class="text-xs font-medium text-gray-900">
                    {{ ticket.customer.name }}
                  </div>
                  <div class="text-xs text-gray-500">
                    {{ ticket.customer.phone || ticket.customer.email }}
                  </div>
                </div>

                <!-- Call Association -->
                <div v-if="ticket.callId" class="flex items-center text-xs text-blue-600">
                  <PhoneIcon class="w-3 h-3 mr-1" />
                  From current call session
                </div>
              </div>

              <!-- Ticket Actions -->
              <div class="mt-3 pt-3 border-t border-gray-100 flex items-center justify-between">
                <div class="text-xs text-gray-500">
                  {{ ticket.problemType || 'General' }}
                </div>
                <div class="flex items-center space-x-2">
                  <button 
                    @click="addTicketNote(ticket)"
                    class="text-blue-600 hover:text-blue-800 text-xs"
                    title="Add note"
                  >
                    <ChatBubbleLeftIcon class="w-3 h-3" />
                  </button>
                  <button 
                    @click="updateTicketStatus(ticket)"
                    class="text-green-600 hover:text-green-800 text-xs"
                    title="Update status"
                  >
                    <CheckIcon class="w-3 h-3" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Evaluation Tests -->
    <div class="mt-8">
      <EvalList :test-scenarios="testScenarios" />
    </div>

    <!-- Testing Checklist -->
    <div class="mt-8">
      <div class="card">
        <div class="card-header">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-lg font-medium text-gray-900">Testing Checklist</h3>
              <p class="text-sm text-gray-500">Comprehensive test scenarios for agent validation</p>
            </div>
            <button @click="showAddTestModal = true" class="btn-primary btn-sm">
              <PlusIcon class="w-3 h-3 mr-1" />
              Add Test
            </button>
          </div>
        </div>
        <div class="card-body p-0">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Test Scenario
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
                    <div class="text-sm font-medium text-gray-900">{{ test.name }}</div>
                    <div class="text-sm text-gray-500">{{ test.description }}</div>
                  </td>
                  <td class="px-6 py-4">
                    <span :class="getCategoryBadge(test.category)" class="badge text-xs">
                      {{ test.category }}
                    </span>
                  </td>
                  <td class="px-6 py-4">
                    <select 
                      v-model="test.status" 
                      @change="updateTestStatus(test)"
                      :class="getStatusSelectClass(test.status)"
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
                        @click="runTest(test)"
                        :disabled="!currentCall"
                        class="text-blue-600 hover:text-blue-900 disabled:text-gray-400"
                        title="Run test with current call"
                      >
                        <PlayIcon class="w-4 h-4" />
                      </button>
                      <button 
                        @click="editTest(test)"
                        class="text-primary-600 hover:text-primary-900"
                      >
                        <PencilIcon class="w-4 h-4" />
                      </button>
                      <button 
                        @click="deleteTest(test.id)"
                        class="text-red-600 hover:text-red-900"
                      >
                        <TrashIcon class="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
            
            <div v-if="testScenarios.length === 0" class="text-center py-12">
              <ClipboardDocumentListIcon class="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p class="text-gray-500">No test scenarios yet</p>
              <button @click="loadDefaultTests" class="btn-primary btn-sm mt-4">
                Load Default Tests
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Test Modal -->
    <div v-if="showAddTestModal || editingTest" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-medium text-gray-900">
              {{ editingTest ? 'Edit Test' : 'Add New Test' }}
            </h3>
            <button @click="closeTestModal" class="text-gray-400 hover:text-gray-600">
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>
          
          <form @submit.prevent="saveTest" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Test Name</label>
              <input 
                v-model="testForm.name"
                type="text" 
                required
                class="form-input w-full"
                placeholder="e.g., Basic greeting response"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea 
                v-model="testForm.description"
                rows="3"
                class="form-input w-full"
                placeholder="Detailed description of what this test validates..."
              ></textarea>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Category</label>
              <select v-model="testForm.category" class="form-select w-full">
                <option value="conversation">Conversation Flow</option>
                <option value="tools">Tool Usage</option>
                <option value="error_handling">Error Handling</option>
                <option value="integration">Integration</option>
                <option value="performance">Performance</option>
                <option value="edge_cases">Edge Cases</option>
              </select>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Test Steps</label>
              <textarea 
                v-model="testForm.steps"
                rows="4"
                class="form-input w-full"
                placeholder="1. Call the agent&#10;2. Say 'Hello'&#10;3. Verify response is appropriate..."
              ></textarea>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Expected Result</label>
              <textarea 
                v-model="testForm.expectedResult"
                rows="2"
                class="form-input w-full"
                placeholder="What should happen when this test passes..."
              ></textarea>
            </div>
            
            <div class="flex justify-end space-x-3 pt-4">
              <button type="button" @click="closeTestModal" class="btn-secondary">
                Cancel
              </button>
              <button type="submit" class="btn-primary">
                {{ editingTest ? 'Update' : 'Create' }} Test
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Add/Edit Routing Rule Modal -->
    <div v-if="showRoutingModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-10 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-medium text-gray-900">
              {{ editingRoutingRule ? 'Edit Routing Rule' : 'Add New Routing Rule' }}
            </h3>
            <button @click="closeRoutingModal" class="text-gray-400 hover:text-gray-600">
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>
          
          <form @submit.prevent="saveRoutingRule" class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Rule Name</label>
                <input 
                  v-model="routingForm.name"
                  type="text" 
                  required
                  class="form-input w-full"
                  placeholder="e.g., Business Hours Sales"
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Request Type</label>
                <select v-model="routingForm.requestType" class="form-select w-full">
                  <option value="sales">Sales Inquiry</option>
                  <option value="support">Technical Support</option>
                  <option value="billing">Billing Question</option>
                  <option value="general">General Information</option>
                  <option value="emergency">Emergency/Urgent</option>
                </select>
              </div>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea 
                v-model="routingForm.description"
                rows="2"
                class="form-input w-full"
                placeholder="Brief description of when this rule applies..."
              ></textarea>
            </div>

            <!-- Time Conditions -->
            <div class="space-y-4">
              <h4 class="text-sm font-medium text-gray-900">Time Conditions</h4>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Start Time</label>
                  <input 
                    v-model="routingForm.timeCondition.start"
                    type="time"
                    class="form-input w-full"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">End Time</label>
                  <input 
                    v-model="routingForm.timeCondition.end"
                    type="time"
                    class="form-input w-full"
                  />
                </div>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Active Days</label>
                <div class="flex flex-wrap gap-2">
                  <label v-for="day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']" :key="day" class="flex items-center">
                    <input 
                      type="checkbox" 
                      :value="day"
                      v-model="routingForm.timeCondition.days"
                      class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    />
                    <span class="ml-2 text-sm text-gray-700">{{ day }}</span>
                  </label>
                </div>
              </div>
            </div>

            <!-- Target Agent -->
            <div class="space-y-4">
              <h4 class="text-sm font-medium text-gray-900">Target Agent</h4>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Agent Name</label>
                  <input 
                    v-model="routingForm.targetAgent.name"
                    type="text"
                    required
                    class="form-input w-full"
                    placeholder="e.g., Sales Agent"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Agent Type</label>
                  <input 
                    v-model="routingForm.targetAgent.type"
                    type="text"
                    class="form-input w-full"
                    placeholder="e.g., Sales Team"
                  />
                </div>
              </div>
            </div>

            <!-- Prompt Configuration -->
            <div class="space-y-4 border-t pt-4">
              <div class="flex items-center justify-between">
                <h4 class="text-sm font-medium text-gray-900">Prompt Configuration</h4>
                <button 
                  type="button"
                  @click="routingForm.promptConfig.specialized = !routingForm.promptConfig.specialized"
                  :class="routingForm.promptConfig.specialized ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-600'"
                  class="px-2 py-1 text-xs rounded"
                >
                  {{ routingForm.promptConfig.specialized ? 'Specialized' : 'Standard' }}
                </button>
              </div>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">System Prompt</label>
                  <select v-model="routingForm.promptConfig.systemPrompt" class="form-select w-full">
                    <option value="normal_working_hours">Normal Working Hours</option>
                    <option value="after_hours_support">After Hours Support</option>
                    <option value="emergency_priority">Emergency Priority</option>
                    <option value="billing_support_hours">Billing Support Hours</option>
                    <option value="weekend_sms_support">Weekend SMS Support</option>
                    <option value="sales_working_hours">Sales Working Hours</option>
                    <option value="technical_support_hours">Technical Support Hours</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Prompt Priority</label>
                  <select v-model="routingForm.promptConfig.promptPriority" class="form-select w-full">
                    <option value="default">Default</option>
                    <option value="sales_focused">Sales Focused</option>
                    <option value="ticket_focused">Ticket Focused</option>
                    <option value="emergency_escalation">Emergency Escalation</option>
                    <option value="billing_focused">Billing Focused</option>
                    <option value="sms_focused">SMS Focused</option>
                  </select>
                </div>
              </div>

              <div v-if="routingForm.promptConfig.specialized">
                <label class="block text-sm font-medium text-gray-700 mb-2">Context Prompts</label>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div v-for="(prompt, key) in availableContextPrompts" :key="key" class="flex items-center">
                    <input 
                      type="checkbox" 
                      :checked="routingForm.promptConfig.contextPrompts[key]"
                      @change="toggleContextPrompt(key, prompt)"
                      class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    />
                    <span class="ml-2 text-sm text-gray-700">{{ prompt.label }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Priority (0 = highest)</label>
                <input 
                  v-model.number="routingForm.priority"
                  type="number"
                  min="0"
                  max="10"
                  class="form-input w-full"
                />
              </div>
              <div class="flex items-center pt-6">
                <input 
                  v-model="routingForm.active"
                  type="checkbox"
                  class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span class="ml-2 text-sm text-gray-700">Rule is active</span>
              </div>
            </div>
            
            <div class="flex justify-end space-x-3 pt-4 border-t">
              <button type="button" @click="closeRoutingModal" class="btn-secondary">
                Cancel
              </button>
              <button type="submit" class="btn-primary">
                {{ editingRoutingRule ? 'Update' : 'Create' }} Rule
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useToast } from 'vue-toastification'
import { formatDistanceToNow } from 'date-fns'
import api from '@/services/api'
import EvalList from '@/components/EvalList.vue'
import {
  PhoneIcon,
  PhoneXMarkIcon,
  ChatBubbleLeftRightIcon,
  DocumentTextIcon,
  DocumentCheckIcon,
  ArrowPathIcon,
  TrashIcon,
  ArrowDownIcon,
  ExclamationTriangleIcon,
  PlusIcon,
  PlayIcon,
  PencilIcon,
  XMarkIcon,
  ClipboardDocumentListIcon,
  MinusIcon,
  MapIcon,
  ClipboardDocumentIcon,
  EyeIcon,
  ChatBubbleLeftIcon,
  CheckIcon
} from '@heroicons/vue/24/outline'

const toast = useToast()

// Reactive state
const agents = ref([])
const selectedAgent = ref(null) // For prompt editing (keep this for compatibility)
const phoneCallAgent = ref(null) // Agent for phone calls
const receivingAgent = ref(null) // Agent receiving the agent-to-agent call
const callingAgent = ref(null) // Agent making the agent-to-agent call
const phoneNumber = ref('')
const currentCall = ref(null)
const callDuration = ref(0)
const manualMinutes = ref(0)
const manualSeconds = ref(0)
const transcript = ref([])
const editedPrompt = ref('')
const originalPrompt = ref('')
const isTyping = ref(false)
const autoScroll = ref(true)
const connectionStatus = ref('disconnected')

// Testing checklist state
const testScenarios = ref([])
const showAddTestModal = ref(false)
const editingTest = ref(null)
const editingNotes = ref(null)
const notesEditValue = ref('')
const testForm = ref({
  name: '',
  description: '',
  category: 'conversation',
  steps: '',
  expectedResult: '',
  status: 'not_started',
  notes: ''
})

// Routing state
const routingRules = ref([])
const showRoutingModal = ref(false)
const editingRoutingRule = ref(null)
const testRequestType = ref('')
const currentTime = ref('')
const routingForm = ref({
  name: '',
  description: '',
  timeCondition: {
    start: '09:00',
    end: '17:00',
    days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
  },
  requestType: 'general',
  targetAgent: {
    name: '',
    type: '',
    id: null
  },
  promptConfig: {
    systemPrompt: 'normal_working_hours',
    contextPrompts: {},
    specialized: false,
    promptPriority: 'default'
  },
  priority: 1,
  active: true
})

// Available context prompts based on your system
const availableContextPrompts = ref({
  demo_call: { label: 'Demo Call Prompt', value: 'demo_call_prompt' },
  send_call: { label: 'Send Call Prompt', value: 'send_call_prompt' },
  eval_system: { label: 'Eval System Prompt', value: 'call_transcript_eval_system_prompt' },
  eval_user: { label: 'Eval User Prompt', value: 'call_transcript_eval_user_prompt' },
  ticket_create: { label: 'Ticket Create Prompt', value: 'ticket_create_prompt' },
  ticket_update: { label: 'Ticket Update Prompt', value: 'outbound_call_ticket_update_prompt' },
  contact_determination: { label: 'Contact Determination', value: 'contact_determination_prompt' },
  sms_messaging: { label: 'SMS Messaging', value: 'sms_messaging' },
  sms_analysis: { label: 'SMS Analysis', value: 'sms_messaging_analysis' },
  contact_determination_sms: { label: 'SMS Contact Determination', value: 'contact_determination_prompt_sms' },
  email_messaging: { label: 'Email Messaging', value: 'email_messaging' },
  email_ticket_decision: { label: 'Email Ticket Decision', value: 'email_ticket_decision' },
  teams_message: { label: 'Teams Message', value: 'teams_message' },
  structured_asset: { label: 'Structured Asset', value: 'structured_asset_prompt' }
})

// Created tickets state
const createdTickets = ref([])
const showTicketModal = ref(false)
const selectedTicket = ref(null)

// Live transcript streaming state
const interimTranscripts = ref(new Map()) // speaker -> interim text
const speechDetected = ref(new Map()) // speaker -> boolean

// UI refs
const transcriptContainer = ref(null)

// Session stats
const sessionStats = ref({
  totalCalls: 0,
  avgDuration: 0
})

// Computed properties
const promptModified = computed(() => {
  return editedPrompt.value !== originalPrompt.value
})

const isBusinessHours = computed(() => {
  const now = new Date()
  const hour = now.getHours()
  const day = now.getDay() // 0 = Sunday, 1 = Monday, etc.
  
  // Basic business hours: Monday-Friday, 9 AM - 5 PM
  return day >= 1 && day <= 5 && hour >= 9 && hour < 17
})

const activeRoutingRule = computed(() => {
  const now = new Date()
  const currentHour = now.getHours()
  const currentMinutes = now.getMinutes()
  const currentTimeStr = `${currentHour.toString().padStart(2, '0')}:${currentMinutes.toString().padStart(2, '0')}`
  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
  const currentDay = dayNames[now.getDay()]
  
  return routingRules.value
    .filter(rule => rule.active)
    .find(rule => {
      const inTimeRange = currentTimeStr >= rule.timeCondition.start && currentTimeStr <= rule.timeCondition.end
      const inDayRange = rule.timeCondition.days.includes(currentDay)
      return inTimeRange && inDayRange
    })
})

const canStartCall = computed(() => {
  if (!selectedAgent.value) return false
  
  if (callType.value === 'phone') {
    return phoneNumber.value && phoneNumber.value.trim() !== ''
  }
  
  if (callType.value === 'agent_to_agent') {
    return callingAgent.value && callingAgent.value.id !== selectedAgent.value.id
  }
  
  return false
})

// Call duration timer
let callTimer = null

// WebSocket for real-time updates (placeholder for now)
let ws = null

// Methods
const loadAgents = async () => {
  try {
    const response = await api.agents.list()
    agents.value = response.data
  } catch (error) {
    toast.error('Failed to load agents')
  }
}

const loadAgentDetails = () => {
  if (selectedAgent.value) {
    editedPrompt.value = selectedAgent.value.prompt || ''
    originalPrompt.value = selectedAgent.value.prompt || ''
  }
}

const startPhoneCall = async () => {
  if (!phoneCallAgent.value || !phoneNumber.value) {
    toast.error('Please select an agent and enter a phone number')
    return
  }

  try {
    const response = await api.calls.create({
      agent_id: phoneCallAgent.value.id,
      to_number: phoneNumber.value,
      from_number: null, // Will use agent's assigned number
      call_type: 'outbound'
    })
    
    currentCall.value = response.data
    callDuration.value = 0
    startCallTimer()
    
    // Connect to WebSocket for real-time updates
    if (response.data.retell_call_id) {
      connectToCallWebSocket(response.data.retell_call_id)
    }
    
    // Start monitoring call for updates (fallback for mock data)
    startCallMonitoring()
    
    addTranscriptMessage({
      speaker: 'system',
      content: `Phone call initiated: ${phoneCallAgent.value.name} calling ${phoneNumber.value}`,
      timestamp: new Date(),
      system: true
    })
    
    toast.success('Phone call initiated successfully')
    sessionStats.value.totalCalls++
    
  } catch (error) {
    toast.error('Failed to start phone call: ' + (error.response?.data?.detail || error.message))
  }
}

const startAgentToAgentCall = async () => {
  if (!receivingAgent.value || !callingAgent.value) {
    toast.error('Please select both receiving and calling agents')
    return
  }

  try {
    const response = await api.calls.createAgentToAgent({
      caller_agent_id: callingAgent.value.id,  // The agent making the call (outbound)
      inbound_agent_id: receivingAgent.value.id,  // The agent receiving the call (inbound)
      call_type: 'agent_to_agent'
    })
    
    currentCall.value = response.data
    callDuration.value = 0
    startCallTimer()
    
    // Connect to WebSocket for real-time updates
    if (response.data.retell_call_id) {
      connectToCallWebSocket(response.data.retell_call_id)
    }
    
    // Start monitoring call for updates (fallback for mock data)
    startCallMonitoring()
    
    addTranscriptMessage({
      speaker: 'system',
      content: `Agent-to-agent call: ${callingAgent.value.name} calling ${receivingAgent.value.name}`,
      timestamp: new Date(),
      system: true
    })
    
    toast.success('Agent call initiated successfully')
    sessionStats.value.totalCalls++
    
  } catch (error) {
    toast.error('Failed to start agent call: ' + (error.response?.data?.detail || error.message))
  }
}

const endCall = () => {
  if (currentCall.value) {
    // In a real implementation, you'd call an API to end the call
    currentCall.value = null
    stopCallTimer()
    stopCallMonitoring()
    clearInterimTranscripts()
    isTyping.value = false
    toast.info('Call ended')
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

const startCallMonitoring = () => {
  // Simulate real-time transcript updates
  // In production, this would be WebSocket or Server-Sent Events
  const mockTranscriptUpdate = () => {
    if (!currentCall.value) return
    
    // Simulate periodic transcript updates
    setTimeout(() => {
      if (currentCall.value && Math.random() > 0.7) {
        const isToolCall = Math.random() > 0.8
        
        if (isToolCall) {
          const toolFunctions = ['lookup_customer', 'create_ticket']
          const selectedTool = toolFunctions[Math.floor(Math.random() * toolFunctions.length)]
          
          addTranscriptMessage({
            speaker: 'agent',
            content: `This is a simulated ${selectedTool} tool call for testing.`,
            timestamp: new Date(),
            tool_call: {
              function_name: selectedTool,
              parameters: selectedTool === 'lookup_customer' 
                ? { search_term: 'John Doe' }
                : { 
                    subject: 'Simulated Support Request', 
                    description: 'This is a test ticket created during the demo call.',
                    priority: 'Medium'
                  }
            }
          })
          
          // Simulate ticket creation
          if (selectedTool === 'create_ticket' && Math.random() > 0.5) {
            setTimeout(() => {
              addTicketFromCall({
                subject: 'Simulated Support Request',
                description: 'This is a test ticket created during the demo call to show how tickets appear in real-time.',
                priority: ['Low', 'Medium', 'High'][Math.floor(Math.random() * 3)],
                customer: {
                  id: Math.floor(Math.random() * 1000),
                  name: 'Demo Customer',
                  phone: '+1 (555) 123-4567'
                },
                problemType: 'Technical Issue'
              })
            }, 1000)
          }
        } else {
          addTranscriptMessage({
            speaker: Math.random() > 0.5 ? 'agent' : 'human',
            content: 'This is a simulated transcript message for testing.',
            timestamp: new Date()
          })
        }
      }
      
      if (currentCall.value) {
        mockTranscriptUpdate()
      }
    }, 2000 + Math.random() * 3000)
  }
  
  mockTranscriptUpdate()
}

const stopCallMonitoring = () => {
  // Stop monitoring logic
}

const addTranscriptMessage = (message) => {
  transcript.value.push({
    id: Date.now() + Math.random(),
    ...message
  })
  
  if (autoScroll.value) {
    nextTick(() => {
      scrollToBottom()
    })
  }
}

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

const savePrompt = async () => {
  if (!selectedAgent.value) return
  
  try {
    await api.agents.update(selectedAgent.value.id, {
      prompt: editedPrompt.value
    })
    
    originalPrompt.value = editedPrompt.value
    selectedAgent.value.prompt = editedPrompt.value
    
    toast.success('Prompt saved successfully')
  } catch (error) {
    toast.error('Failed to save prompt')
  }
}

const resetPrompt = () => {
  editedPrompt.value = originalPrompt.value
}

const onPromptChange = () => {
  // This will trigger the promptModified computed property
}

const formatDuration = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// Manual call time adjustment methods
const adjustCallTime = (seconds) => {
  callDuration.value = Math.max(0, callDuration.value + seconds)
  updateManualTimeInputs()
  
  // Add to transcript
  addTranscriptMessage({
    speaker: 'system',
    content: `Call time ${seconds > 0 ? 'increased' : 'decreased'} by ${Math.abs(seconds)} seconds (Total: ${formatDuration(callDuration.value)})`,
    timestamp: new Date(),
    system: true
  })
}

const setManualTime = () => {
  const totalSeconds = (manualMinutes.value || 0) * 60 + (manualSeconds.value || 0)
  const oldDuration = callDuration.value
  callDuration.value = Math.max(0, totalSeconds)
  
  // Add to transcript if time changed
  if (oldDuration !== callDuration.value) {
    addTranscriptMessage({
      speaker: 'system',
      content: `Call time manually set to ${formatDuration(callDuration.value)}`,
      timestamp: new Date(),
      system: true
    })
  }
}

const resetCallTime = () => {
  callDuration.value = 0
  updateManualTimeInputs()
  
  addTranscriptMessage({
    speaker: 'system',
    content: 'Call time reset to 0:00',
    timestamp: new Date(),
    system: true
  })
}

const updateManualTimeInputs = () => {
  manualMinutes.value = Math.floor(callDuration.value / 60)
  manualSeconds.value = callDuration.value % 60
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString()
}

const formatDate = (timestamp) => {
  return new Date(timestamp).toLocaleDateString()
}

// Testing checklist methods
const loadTestScenarios = () => {
  const saved = localStorage.getItem('e2e_test_scenarios')
  if (saved) {
    testScenarios.value = JSON.parse(saved)
  }
}

const saveTestScenarios = () => {
  localStorage.setItem('e2e_test_scenarios', JSON.stringify(testScenarios.value))
}

const loadDefaultTests = () => {
  const defaultTests = [
    {
      id: Date.now() + 1,
      name: 'Basic Greeting Response',
      description: 'Test that agent responds appropriately to basic greetings',
      category: 'conversation',
      steps: '1. Call the agent\n2. Say "Hello"\n3. Verify response is friendly and appropriate',
      expectedResult: 'Agent should respond with a professional greeting and ask how they can help',
      status: 'not_started',
      notes: '',
      createdAt: new Date(),
      lastTested: null
    },
    {
      id: Date.now() + 2,
      name: 'Customer Lookup Tool',
      description: 'Verify agent can successfully look up customer information',
      category: 'tools',
      steps: '1. Call agent\n2. Mention need to find customer info\n3. Provide customer name or phone\n4. Verify tool is called correctly',
      expectedResult: 'Agent should call lookup_customer tool with correct parameters and relay results',
      status: 'not_started',
      notes: '',
      createdAt: new Date(),
      lastTested: null
    },
    {
      id: Date.now() + 3,
      name: 'Ticket Creation Flow',
      description: 'Test complete ticket creation process',
      category: 'tools',
      steps: '1. Call agent\n2. Report an issue\n3. Provide all required details\n4. Confirm ticket creation',
      expectedResult: 'Agent should gather all necessary info and create ticket using create_ticket tool',
      status: 'not_started',
      notes: '',
      createdAt: new Date(),
      lastTested: null
    },
    {
      id: Date.now() + 4,
      name: 'Handling Unclear Requests',
      description: 'Test how agent handles ambiguous or unclear user requests',
      category: 'error_handling',
      steps: '1. Call agent\n2. Make vague or confusing request\n3. Verify agent asks clarifying questions',
      expectedResult: 'Agent should politely ask for clarification rather than guessing',
      status: 'not_started',
      notes: '',
      createdAt: new Date(),
      lastTested: null
    },
    {
      id: Date.now() + 5,
      name: 'Call Duration & Natural Flow',
      description: 'Test that conversations flow naturally without awkward pauses',
      category: 'performance',
      steps: '1. Call agent\n2. Have normal conversation\n3. Monitor response times and flow',
      expectedResult: 'Responses should be timely (<3 seconds) and conversation should flow naturally',
      status: 'not_started',
      notes: '',
      createdAt: new Date(),
      lastTested: null
    },
    {
      id: Date.now() + 6,
      name: 'Interruption Handling',
      description: 'Test agent behavior when interrupted by caller',
      category: 'edge_cases',
      steps: '1. Call agent\n2. Start speaking while agent is talking\n3. Verify appropriate response',
      expectedResult: 'Agent should stop speaking and listen to the interruption appropriately',
      status: 'not_started',
      notes: '',
      createdAt: new Date(),
      lastTested: null
    }
  ]
  
  testScenarios.value = defaultTests
  saveTestScenarios()
  toast.success('Default test scenarios loaded')
}

const resetTestForm = () => {
  testForm.value = {
    name: '',
    description: '',
    category: 'conversation',
    steps: '',
    expectedResult: '',
    status: 'not_started',
    notes: ''
  }
}

const closeTestModal = () => {
  showAddTestModal.value = false
  editingTest.value = null
  resetTestForm()
}

const editTest = (test) => {
  editingTest.value = test
  testForm.value = { ...test }
}

const saveTest = () => {
  if (editingTest.value) {
    // Update existing test
    const index = testScenarios.value.findIndex(t => t.id === editingTest.value.id)
    if (index !== -1) {
      testScenarios.value[index] = { ...testForm.value, id: editingTest.value.id }
    }
    toast.success('Test scenario updated')
  } else {
    // Create new test
    const newTest = {
      ...testForm.value,
      id: Date.now(),
      createdAt: new Date(),
      lastTested: null
    }
    testScenarios.value.push(newTest)
    toast.success('Test scenario created')
  }
  
  saveTestScenarios()
  closeTestModal()
}

const deleteTest = (testId) => {
  if (confirm('Are you sure you want to delete this test scenario?')) {
    testScenarios.value = testScenarios.value.filter(t => t.id !== testId)
    saveTestScenarios()
    toast.success('Test scenario deleted')
  }
}

const updateTestStatus = (test) => {
  test.lastTested = new Date()
  saveTestScenarios()
  
  // Add to transcript if there's an active call
  if (currentCall.value) {
    addTranscriptMessage({
      speaker: 'system',
      content: `Test "${test.name}" marked as ${test.status.replace('_', ' ')}`,
      timestamp: new Date(),
      system: true
    })
  }
}

const runTest = (test) => {
  if (!currentCall.value) {
    toast.error('Start a call first to run this test')
    return
  }
  
  test.status = 'in_progress'
  test.lastTested = new Date()
  saveTestScenarios()
  
  // Add test info to transcript
  addTranscriptMessage({
    speaker: 'system',
    content: `Running test: ${test.name}`,
    timestamp: new Date(),
    system: true
  })
  
  addTranscriptMessage({
    speaker: 'system',
    content: `Test steps:\n${test.steps}`,
    timestamp: new Date(),
    system: true
  })
  
  toast.info(`Started test: ${test.name}`)
}

const getCategoryBadge = (category) => {
  const badges = {
    conversation: 'bg-blue-100 text-blue-800',
    tools: 'bg-purple-100 text-purple-800',
    error_handling: 'bg-red-100 text-red-800',
    integration: 'bg-green-100 text-green-800',
    performance: 'bg-yellow-100 text-yellow-800',
    edge_cases: 'bg-gray-100 text-gray-800'
  }
  return badges[category] || 'bg-gray-100 text-gray-800'
}

const getStatusSelectClass = (status) => {
  const classes = {
    not_started: 'bg-gray-100 text-gray-800',
    in_progress: 'bg-blue-100 text-blue-800',
    passed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

// Inline notes editing
const startEditingNotes = (test) => {
  editingNotes.value = test
  notesEditValue.value = test.notes || ''
  nextTick(() => {
    // Focus the textarea when it becomes visible
    const textarea = document.querySelector('textarea[ref="notesInput"]')
    if (textarea) {
      textarea.focus()
    }
  })
}

const saveNotes = (test) => {
  test.notes = notesEditValue.value
  saveTestScenarios()
  editingNotes.value = null
  notesEditValue.value = ''
}

const cancelEditingNotes = () => {
  editingNotes.value = null
  notesEditValue.value = ''
}

// Routing methods
const updateCurrentTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString()
}

const loadRoutingRules = () => {
  const saved = localStorage.getItem('e2e_routing_rules')
  if (saved) {
    routingRules.value = JSON.parse(saved)
  } else {
    // Auto-load default rules on first visit
    loadDefaultRoutingRules()
  }
}

const saveRoutingRules = () => {
  localStorage.setItem('e2e_routing_rules', JSON.stringify(routingRules.value))
}

const loadDefaultRoutingRules = () => {
  const defaultRules = [
    {
      id: Date.now() + 1,
      name: 'Business Hours Sales',
      description: 'Route sales inquiries with sales-optimized prompts during business hours',
      timeCondition: {
        start: '09:00',
        end: '17:00',
        days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
      },
      requestType: 'sales',
      targetAgent: {
        name: 'Sales Agent',
        type: 'Sales Team',
        id: 1
      },
      promptConfig: {
        systemPrompt: 'normal_working_hours',
        contextPrompts: {
          demo_call: 'demo_call_prompt',
          send_call: 'send_call_prompt',
          eval_system: 'call_transcript_eval_system_prompt',
          eval_user: 'call_transcript_eval_user_prompt'
        },
        specialized: true,
        promptPriority: 'sales_focused'
      },
      priority: 1,
      active: true
    },
    {
      id: Date.now() + 2,
      name: 'After Hours Support',
      description: 'Route to support with after-hours messaging and ticket creation',
      timeCondition: {
        start: '17:01',
        end: '08:59',
        days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
      },
      requestType: 'support',
      targetAgent: {
        name: 'General Support Agent',
        type: 'After Hours',
        id: 2
      },
      promptConfig: {
        systemPrompt: 'after_hours_support',
        contextPrompts: {
          ticket_create: 'ticket_create_prompt',
          ticket_update: 'outbound_call_ticket_update_prompt',
          contact_determination: 'contact_determination_prompt',
          sms_messaging: 'sms_messaging',
          email_messaging: 'email_messaging'
        },
        specialized: true,
        promptPriority: 'ticket_focused'
      },
      priority: 2,
      active: true
    },
    {
      id: Date.now() + 3,
      name: 'Emergency Priority',
      description: 'Always route emergency calls with priority support prompts',
      timeCondition: {
        start: '00:00',
        end: '23:59',
        days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
      },
      requestType: 'emergency',
      targetAgent: {
        name: 'Emergency Support Agent',
        type: 'Priority Support',
        id: 3
      },
      promptConfig: {
        systemPrompt: 'emergency_priority',
        contextPrompts: {
          ticket_create: 'ticket_create_prompt',
          contact_determination: 'contact_determination_prompt',
          teams_message: 'teams_message',
          structured_asset: 'structured_asset_prompt'
        },
        specialized: true,
        promptPriority: 'emergency_escalation'
      },
      priority: 0,
      active: true
    },
    {
      id: Date.now() + 4,
      name: 'Billing Support',
      description: 'Route billing questions with financial and email-focused prompts',
      timeCondition: {
        start: '08:00',
        end: '18:00',
        days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
      },
      requestType: 'billing',
      targetAgent: {
        name: 'Billing Support Agent',
        type: 'Billing Team',
        id: 4
      },
      promptConfig: {
        systemPrompt: 'billing_support_hours',
        contextPrompts: {
          email_messaging: 'email_messaging',
          email_ticket_decision: 'email_ticket_decision',
          contact_determination: 'contact_determination_prompt',
          teams_message: 'teams_message'
        },
        specialized: true,
        promptPriority: 'billing_focused'
      },
      priority: 1,
      active: true
    },
    {
      id: Date.now() + 5,
      name: 'Weekend SMS Support',
      description: 'Lightweight SMS-based support for weekend inquiries',
      timeCondition: {
        start: '10:00',
        end: '18:00',
        days: ['Sat', 'Sun']
      },
      requestType: 'general',
      targetAgent: {
        name: 'Weekend SMS Agent',
        type: 'SMS Support',
        id: 5
      },
      promptConfig: {
        systemPrompt: 'weekend_sms_support',
        contextPrompts: {
          sms_messaging: 'sms_messaging',
          sms_analysis: 'sms_messaging_analysis',
          contact_determination_sms: 'contact_determination_prompt_sms'
        },
        specialized: true,
        promptPriority: 'sms_focused'
      },
      priority: 3,
      active: true
    }
  ]

  routingRules.value = defaultRules
  saveRoutingRules()
  toast.success('Default routing rules loaded with time-based prompt configurations')
}

const getRoutingDestination = (requestType) => {
  if (!requestType) return 'No selection'
  
  const matchingRules = routingRules.value
    .filter(rule => rule.active && rule.requestType === requestType)
    .sort((a, b) => a.priority - b.priority)
  
  if (matchingRules.length === 0) {
    return 'Default Agent (no matching rules)'
  }
  
  // Check time-based rules
  const activeRule = matchingRules.find(rule => {
    const now = new Date()
    const currentHour = now.getHours()
    const currentMinutes = now.getMinutes()
    const currentTimeStr = `${currentHour.toString().padStart(2, '0')}:${currentMinutes.toString().padStart(2, '0')}`
    const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    const currentDay = dayNames[now.getDay()]
    
    const inTimeRange = currentTimeStr >= rule.timeCondition.start && currentTimeStr <= rule.timeCondition.end
    const inDayRange = rule.timeCondition.days.includes(currentDay)
    return inTimeRange && inDayRange
  })
  
  if (activeRule) {
    const promptInfo = activeRule.promptConfig ? 
      ` → ${activeRule.promptConfig.systemPrompt} (${activeRule.promptConfig.promptPriority})` : ''
    return `${activeRule.targetAgent.name} (${activeRule.name})${promptInfo}`
  }
  
  const fallbackRule = matchingRules[0]
  const promptInfo = fallbackRule.promptConfig ? 
    ` → ${fallbackRule.promptConfig.systemPrompt}` : ''
  return `${fallbackRule.targetAgent.name} (fallback rule)${promptInfo}`
}

const testRouting = () => {
  if (!testRequestType.value) {
    toast.error('Please select a request type to test')
    return
  }
  
  const destination = getRoutingDestination(testRequestType.value)
  
  addTranscriptMessage({
    speaker: 'system',
    content: `Routing test: ${testRequestType.value} request → ${destination}`,
    timestamp: new Date(),
    system: true
  })
  
  toast.success(`Routing test: ${testRequestType.value} → ${destination}`)
}

const getRequestTypeBadge = (type) => {
  const badges = {
    sales: 'bg-green-100 text-green-800',
    support: 'bg-blue-100 text-blue-800',
    billing: 'bg-yellow-100 text-yellow-800',
    general: 'bg-gray-100 text-gray-800',
    emergency: 'bg-red-100 text-red-800'
  }
  return badges[type] || 'bg-gray-100 text-gray-800'
}

const getCurrentActivePromptConfig = () => {
  const now = new Date()
  const currentHour = now.getHours()
  const currentMinutes = now.getMinutes()
  const currentTimeStr = `${currentHour.toString().padStart(2, '0')}:${currentMinutes.toString().padStart(2, '0')}`
  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
  const currentDay = dayNames[now.getDay()]
  
  const activeRules = routingRules.value.filter(rule => {
    if (!rule.active) return false
    const inTimeRange = currentTimeStr >= rule.timeCondition.start && currentTimeStr <= rule.timeCondition.end
    const inDayRange = rule.timeCondition.days.includes(currentDay)
    return inTimeRange && inDayRange
  }).sort((a, b) => a.priority - b.priority)
  
  if (activeRules.length === 0) return null
  
  const primaryRule = activeRules[0]
  return {
    rule: primaryRule,
    promptConfig: primaryRule.promptConfig,
    timeContext: `${currentTimeStr} on ${currentDay}`,
    totalActiveRules: activeRules.length
  }
}

const toggleRule = (rule) => {
  rule.active = !rule.active
  saveRoutingRules()
  toast.success(`Rule "${rule.name}" ${rule.active ? 'enabled' : 'disabled'}`)
}

const editRoutingRule = (rule) => {
  editingRoutingRule.value = rule
  routingForm.value = JSON.parse(JSON.stringify(rule)) // Deep copy
  showRoutingModal.value = true
}

const deleteRoutingRule = (ruleId) => {
  if (confirm('Are you sure you want to delete this routing rule?')) {
    routingRules.value = routingRules.value.filter(r => r.id !== ruleId)
    saveRoutingRules()
    toast.success('Routing rule deleted')
  }
}

const toggleContextPrompt = (key, prompt) => {
  if (routingForm.value.promptConfig.contextPrompts[key]) {
    delete routingForm.value.promptConfig.contextPrompts[key]
  } else {
    routingForm.value.promptConfig.contextPrompts[key] = prompt.value
  }
}

const closeRoutingModal = () => {
  showRoutingModal.value = false
  editingRoutingRule.value = null
  resetRoutingForm()
}

const resetRoutingForm = () => {
  routingForm.value = {
    name: '',
    description: '',
    timeCondition: {
      start: '09:00',
      end: '17:00',
      days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    },
    requestType: 'general',
    targetAgent: {
      name: '',
      type: '',
      id: null
    },
    promptConfig: {
      systemPrompt: 'normal_working_hours',
      contextPrompts: {},
      specialized: false,
      promptPriority: 'default'
    },
    priority: 1,
    active: true
  }
}

const saveRoutingRule = () => {
  if (editingRoutingRule.value) {
    // Update existing rule
    const index = routingRules.value.findIndex(r => r.id === editingRoutingRule.value.id)
    if (index !== -1) {
      routingRules.value[index] = { ...routingForm.value, id: editingRoutingRule.value.id }
    }
    toast.success('Routing rule updated')
  } else {
    // Create new rule
    const newRule = {
      ...routingForm.value,
      id: Date.now()
    }
    routingRules.value.push(newRule)
    toast.success('Routing rule created')
  }
  
  saveRoutingRules()
  closeRoutingModal()
}

// Initialize WebSocket connection for real-time updates
const initializeConnection = () => {
  connectionStatus.value = 'connecting'
  
  // For now, simulate connection - in production you'd connect to WebSocket
  setTimeout(() => {
    connectionStatus.value = 'connected'
  }, 1000)
}

const connectToCallWebSocket = (callId) => {
  if (!callId) return
  
  // Create WebSocket connection for this specific call
  const wsUrl = `ws://localhost:8000/api/v1/calls/ws/transcript/${callId}`
  
  try {
    ws = new WebSocket(wsUrl)
    
    ws.onopen = () => {
      console.log(`WebSocket connected for call ${callId}`)
      // Subscribe to call updates
      ws.send(JSON.stringify({ type: 'subscribe', call_id: callId }))
    }
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        handleWebSocketMessage(data)
      } catch (error) {
        console.error('Error parsing WebSocket message:', error)
      }
    }
    
    ws.onclose = () => {
      console.log(`WebSocket closed for call ${callId}`)
      ws = null
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      connectionStatus.value = 'disconnected'
    }
    
  } catch (error) {
    console.error('Failed to create WebSocket connection:', error)
    connectionStatus.value = 'disconnected'
  }
}

const handleWebSocketMessage = (data) => {
  switch (data.type) {
    case 'call_started':
      if (currentCall.value) {
        currentCall.value.status = 'ongoing'
      }
      addTranscriptMessage({
        speaker: 'system',
        content: 'Call started - live transcript streaming active',
        timestamp: new Date(data.timestamp),
        system: true
      })
      toast.success('Live transcript streaming connected')
      break
      
    case 'call_ended':
      if (currentCall.value) {
        currentCall.value.status = 'ended'
        endCall()
      }
      addTranscriptMessage({
        speaker: 'system',
        content: 'Call ended - transcript streaming stopped',
        timestamp: new Date(data.timestamp),
        system: true
      })
      break
      
    case 'transcript_update':
      // Handle real-time transcript updates
      const transcript_data = data.data
      if (transcript_data.content && transcript_data.content.trim()) {
        // Only add final transcripts to avoid duplicates
        if (transcript_data.is_final) {
          addTranscriptMessage({
            speaker: transcript_data.speaker,
            content: transcript_data.content,
            timestamp: new Date(transcript_data.timestamp),
            streaming: true
          })
        } else {
          // Show partial/interim transcripts with different styling
          showInterimTranscript(transcript_data)
        }
      }
      break
      
    case 'speech_detected':
      // Show speech detection indicators
      const speech_data = data.data
      if (speech_data.detected) {
        setTypingIndicator(speech_data.speaker, true)
      } else {
        setTypingIndicator(speech_data.speaker, false)
      }
      break
      
    case 'tool_call':
      // Handle tool call events
      const tool_data = data.data
      addTranscriptMessage({
        speaker: 'agent',
        content: `🔧 Called ${tool_data.function_name}`,
        timestamp: new Date(data.timestamp),
        tool_call: {
          function_name: tool_data.function_name,
          parameters: tool_data.arguments,
          result: tool_data.result
        }
      })
      
      // If it's a ticket creation tool call, add the ticket
      if (tool_data.function_name === 'create_ticket' && tool_data.result) {
        addTicketFromCall({
          id: tool_data.result.ticket_id,
          subject: tool_data.arguments.subject,
          description: tool_data.arguments.description,
          priority: tool_data.arguments.priority || 'Medium',
          customer: tool_data.arguments.customer_id ? {
            id: tool_data.arguments.customer_id,
            name: tool_data.result.customer_name || 'Unknown Customer'
          } : null,
          problemType: tool_data.arguments.problem_type
        })
      }
      break
      
    case 'subscribed':
      toast.success('Connected to live call transcript stream')
      addTranscriptMessage({
        speaker: 'system',
        content: 'WebSocket connected - ready for live transcript streaming',
        timestamp: new Date(),
        system: true
      })
      break
      
    default:
      console.log('Unknown WebSocket message type:', data.type, data)
  }
}

// Live transcript streaming helpers
const showInterimTranscript = (transcriptData) => {
  // Store interim transcript for this speaker
  interimTranscripts.value.set(transcriptData.speaker, {
    content: transcriptData.content,
    timestamp: new Date(transcriptData.timestamp)
  })
  
  // Auto-clear interim transcript after 3 seconds if no update
  setTimeout(() => {
    if (interimTranscripts.value.has(transcriptData.speaker)) {
      const stored = interimTranscripts.value.get(transcriptData.speaker)
      if (stored.content === transcriptData.content) {
        interimTranscripts.value.delete(transcriptData.speaker)
      }
    }
  }, 3000)
}

const setTypingIndicator = (speaker, isTyping) => {
  if (isTyping) {
    speechDetected.value.set(speaker, true)
    // Auto-clear typing indicator after 5 seconds
    setTimeout(() => {
      speechDetected.value.delete(speaker)
    }, 5000)
  } else {
    speechDetected.value.delete(speaker)
  }
}

const clearInterimTranscripts = () => {
  interimTranscripts.value.clear()
  speechDetected.value.clear()
}

// Ticket management methods
const loadCreatedTickets = () => {
  const saved = localStorage.getItem('e2e_created_tickets')
  if (saved) {
    createdTickets.value = JSON.parse(saved)
  }
}

const saveCreatedTickets = () => {
  localStorage.setItem('e2e_created_tickets', JSON.stringify(createdTickets.value))
}

const addTicketFromCall = (ticketData) => {
  const newTicket = {
    id: ticketData.id || Date.now(),
    subject: ticketData.subject,
    description: ticketData.description,
    priority: ticketData.priority || 'Medium',
    status: ticketData.status || 'Open',
    customer: ticketData.customer,
    problemType: ticketData.problemType,
    callId: currentCall.value?.id,
    createdAt: new Date(),
    ...ticketData
  }
  
  createdTickets.value.unshift(newTicket)
  saveCreatedTickets()
  
  // Add to transcript
  addTranscriptMessage({
    speaker: 'system',
    content: `Ticket #${newTicket.id} created: ${newTicket.subject}`,
    timestamp: new Date(),
    system: true
  })
  
  toast.success(`Ticket #${newTicket.id} created successfully`)
}

const clearTickets = () => {
  if (confirm('Are you sure you want to clear all tickets?')) {
    createdTickets.value = []
    saveCreatedTickets()
    toast.success('All tickets cleared')
  }
}

const viewTicketDetails = (ticket) => {
  selectedTicket.value = ticket
  showTicketModal.value = true
}

const addTicketNote = (ticket) => {
  const note = prompt('Add a note to this ticket:')
  if (note) {
    if (!ticket.notes) ticket.notes = []
    ticket.notes.push({
      id: Date.now(),
      content: note,
      createdAt: new Date(),
      createdBy: 'User'
    })
    saveCreatedTickets()
    toast.success('Note added to ticket')
  }
}

const updateTicketStatus = (ticket) => {
  const newStatus = prompt('Enter new status (Open, In Progress, Resolved, Closed):', ticket.status)
  if (newStatus && newStatus !== ticket.status) {
    ticket.status = newStatus
    ticket.updatedAt = new Date()
    saveCreatedTickets()
    toast.success(`Ticket status updated to ${newStatus}`)
  }
}

const getTicketBorderClass = (priority) => {
  const classes = {
    'Critical': 'border-l-4 border-red-500',
    'High': 'border-l-4 border-orange-500',
    'Medium': 'border-l-4 border-yellow-500',
    'Low': 'border-l-4 border-green-500'
  }
  return classes[priority] || 'border-l-4 border-gray-300'
}

const getTicketStatusBadge = (status) => {
  const classes = {
    'Open': 'bg-blue-100 text-blue-800',
    'In Progress': 'bg-yellow-100 text-yellow-800',
    'Resolved': 'bg-green-100 text-green-800',
    'Closed': 'bg-gray-100 text-gray-800'
  }
  return `badge ${classes[status] || 'bg-gray-100 text-gray-800'}`
}

const getPriorityBadge = (priority) => {
  const classes = {
    'Critical': 'bg-red-100 text-red-800',
    'High': 'bg-orange-100 text-orange-800',
    'Medium': 'bg-yellow-100 text-yellow-800',
    'Low': 'bg-green-100 text-green-800'
  }
  return `badge ${classes[priority] || 'bg-gray-100 text-gray-800'}`
}

// Cleanup
onMounted(() => {
  loadAgents()
  initializeConnection()
  loadTestScenarios()
  loadRoutingRules()
  loadCreatedTickets()
  
  // Update current time every minute
  updateCurrentTime()
  setInterval(updateCurrentTime, 60000)
})

onUnmounted(() => {
  if (callTimer) {
    clearInterval(callTimer)
  }
  if (ws) {
    ws.close()
  }
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

.badge-primary {
  @apply bg-primary-100 text-primary-800;
}

.badge-success {
  @apply bg-green-100 text-green-800;
}

.badge-blue {
  @apply bg-blue-100 text-blue-800;
}

/* Modal styling */
.fixed {
  position: fixed;
}

/* Table styling */
table {
  border-collapse: separate;
  border-spacing: 0;
}

/* Form textarea styling */
textarea.form-input {
  resize: vertical;
  min-height: 80px;
}

/* Live transcript styling */
.transcript-message.interim {
  animation: fadeInGlow 0.3s ease-in;
}

.transcript-message.speech-indicator {
  animation: pulseIn 0.5s ease-in-out;
}

@keyframes fadeInGlow {
  from {
    opacity: 0;
    transform: translateY(5px);
    box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
  }
  to {
    opacity: 0.6;
    transform: translateY(0);
    box-shadow: none;
  }
}

@keyframes pulseIn {
  0% {
    opacity: 0;
    transform: scale(0.95);
  }
  50% {
    opacity: 1;
    transform: scale(1.02);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}
</style> 