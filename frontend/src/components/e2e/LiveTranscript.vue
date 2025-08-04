<template>
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
        
        <!-- Main Transcript Messages -->
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
</template>

<script>
import { ref, nextTick, watch } from 'vue'
import { 
  TrashIcon, 
  ArrowDownIcon, 
  ChatBubbleLeftRightIcon 
} from '@heroicons/vue/24/outline'

export default {
  name: 'LiveTranscript',
  components: {
    TrashIcon,
    ArrowDownIcon,
    ChatBubbleLeftRightIcon
  },
  props: {
    transcript: {
      type: Array,
      default: () => []
    },
    interimTranscripts: {
      type: Map,
      default: () => new Map()
    },
    speechDetected: {
      type: Map,
      default: () => new Map()
    },
    currentCall: {
      type: Object,
      default: null
    }
  },
  emits: ['clear-transcript'],
  setup(props, { emit }) {
    const transcriptContainer = ref(null)
    const autoScroll = ref(true)

    const clearTranscript = () => {
      emit('clear-transcript')
    }

    const toggleAutoScroll = () => {
      autoScroll.value = !autoScroll.value
      if (autoScroll.value) {
        scrollToBottom()
      }
    }

    const scrollToBottom = async () => {
      if (!autoScroll.value || !transcriptContainer.value) return
      
      await nextTick()
      transcriptContainer.value.scrollTop = transcriptContainer.value.scrollHeight
    }

    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleTimeString()
    }

    // Auto-scroll when new messages arrive
    watch(() => [props.transcript.length, props.interimTranscripts.size, props.speechDetected.size], () => {
      if (autoScroll.value) {
        scrollToBottom()
      }
    })

    return {
      transcriptContainer,
      autoScroll,
      clearTranscript,
      toggleAutoScroll,
      formatTime
    }
  }
}
</script>

<style scoped>
.transcript-message {
  @apply transition-all duration-200;
}

.transcript-message.interim {
  @apply animate-pulse;
}

.speech-indicator {
  @apply animate-pulse;
}

.badge {
  @apply inline-flex items-center px-2 py-0.5 rounded text-xs font-medium;
}

.badge-primary {
  @apply bg-blue-100 text-blue-800;
}

.badge-success {
  @apply bg-green-100 text-green-800;
}

.badge-blue {
  @apply bg-blue-100 text-blue-800;
}
</style> 