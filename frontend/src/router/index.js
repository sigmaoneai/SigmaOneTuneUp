import { createRouter, createWebHistory } from 'vue-router'

// Import views
import Dashboard from '@/views/Dashboard.vue'
import Agents from '@/views/Agents/index.vue'
import AgentDetail from '@/views/Agents/Detail.vue'
import AgentCreate from '@/views/Agents/Create.vue'
import PhoneNumbers from '@/views/PhoneNumbers/index.vue'
import Calls from '@/views/Calls/index.vue'
import CallDetail from '@/views/Calls/Detail.vue'
import Prompts from '@/views/Prompts/index.vue'
import PromptDetail from '@/views/Prompts/Detail.vue'
import PromptCreate from '@/views/Prompts/Create.vue'
import SyncroMSP from '@/views/SyncroMSP/index.vue'
import Settings from '@/views/Settings.vue'
import E2ETuning from '@/views/E2ETuning.vue'
import Onboarding from '@/views/Onboarding.vue'
import KnowledgeBase from '@/views/KnowledgeBase/index.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: {
      title: 'Dashboard'
    }
  },
  {
    path: '/agents',
    name: 'Agents',
    component: Agents,
    meta: {
      title: 'Voice Agents'
    }
  },
  {
    path: '/agents/create',
    name: 'AgentCreate',
    component: AgentCreate,
    meta: {
      title: 'Create Agent'
    }
  },
  {
    path: '/agents/:id',
    name: 'AgentDetail',
    component: AgentDetail,
    meta: {
      title: 'Agent Details'
    }
  },
  {
    path: '/phone-numbers',
    name: 'PhoneNumbers',
    component: PhoneNumbers,
    meta: {
      title: 'Phone Numbers'
    }
  },
  {
    path: '/calls',
    name: 'Calls',
    component: Calls,
    meta: {
      title: 'Call History'
    }
  },
  {
    path: '/calls/:id',
    name: 'CallDetail',
    component: CallDetail,
    meta: {
      title: 'Call Details'
    }
  },
  {
    path: '/prompts',
    name: 'Prompts',
    component: Prompts,
    meta: {
      title: 'Prompt Library'
    }
  },
  {
    path: '/prompts/create',
    name: 'PromptCreate',
    component: PromptCreate,
    meta: {
      title: 'Create Prompt'
    }
  },
  {
    path: '/prompts/:name',
    name: 'PromptDetail',
    component: PromptDetail,
    meta: {
      title: 'Prompt Details'
    }
  },
  {
    path: '/syncromsp',
    name: 'SyncroMSP',
    component: SyncroMSP,
    meta: {
      title: 'SyncroMSP Integration'
    }
  },
  {
    path: '/onboarding',
    name: 'Onboarding',
    component: Onboarding,
    meta: {
      title: 'Business Onboarding'
    }
  },
  {
    path: '/e2e-tuning',
    name: 'E2ETuning',
    component: E2ETuning,
    meta: {
      title: 'E2E Agent Tuning'
    }
  },
  {
    path: '/knowledge-base',
    name: 'KnowledgeBase',
    component: KnowledgeBase,
    meta: {
      title: 'Knowledge Base'
    }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: {
      title: 'Settings'
    }
  },
  // 404 fallback
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Global navigation guard
router.beforeEach((to, from, next) => {
  // Update document title
  document.title = to.meta?.title 
    ? `${to.meta.title} - SigmaOne TuneUp`
    : 'SigmaOne TuneUp'
  
  next()
})

export default router 