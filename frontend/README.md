# SigmaOne TuneUp Frontend

A modern Vue.js frontend for the SigmaOne TuneUp voice AI management platform. Built with Vue 3, TypeScript, Tailwind CSS, and modern development practices.

## 🚀 Features

- **Modern Vue 3**: Composition API with TypeScript support
- **Responsive Design**: Mobile-first design with Tailwind CSS
- **Real-time Updates**: Live dashboard with system monitoring
- **Component Library**: Reusable UI components and patterns
- **State Management**: Pinia for reactive state management
- **API Integration**: Axios-based API client with error handling
- **Charts & Visualization**: Chart.js integration for analytics
- **Toast Notifications**: User-friendly feedback system
- **Router**: Vue Router with route guards and meta

## 📁 Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── assets/            # CSS, images, and other assets
│   ├── components/        # Reusable Vue components
│   │   ├── dashboard/     # Dashboard-specific components
│   │   ├── agents/        # Agent management components
│   │   ├── layout/        # Layout components (navigation, etc.)
│   │   └── ui/            # Generic UI components
│   ├── router/            # Vue Router configuration
│   ├── services/          # API services and utilities
│   ├── stores/            # Pinia state management
│   ├── views/             # Page-level components
│   │   ├── Agents/        # Agent management views
│   │   ├── Calls/         # Call history and details
│   │   ├── PhoneNumbers/  # Phone number management
│   │   ├── Prompts/       # Prompt library
│   │   └── SyncroMSP/     # SyncroMSP integration
│   ├── App.vue            # Root component
│   └── main.js            # Application entry point
├── index.html             # HTML template
├── package.json           # Dependencies and scripts
├── tailwind.config.js     # Tailwind CSS configuration
├── vite.config.js         # Vite build configuration
└── README.md              # This file
```

## 🛠️ Technology Stack

### Core Framework
- **Vue 3** - Progressive JavaScript framework
- **Vite** - Next-generation frontend tooling
- **Vue Router** - Official router for Vue.js
- **Pinia** - Intuitive state management

### Styling & UI
- **Tailwind CSS** - Utility-first CSS framework
- **Headless UI** - Unstyled, accessible UI components
- **Heroicons** - Beautiful hand-crafted SVG icons

### Data & API
- **Axios** - Promise-based HTTP client
- **Chart.js** - Simple yet flexible charting
- **Vue Chart.js** - Vue wrapper for Chart.js

### Developer Experience
- **ESLint** - Code linting and formatting
- **Prettier** - Code formatting
- **Vite HMR** - Hot module replacement

## 🚦 Getting Started

### Prerequisites

- Node.js 18+ (LTS recommended)
- npm or yarn package manager
- Backend API running on port 8000

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd SigmaOneTuneUp/frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start development server:**
```bash
npm run dev
```

4. **Access the application:**
- Frontend: http://localhost:3000
- API Proxy: http://localhost:3000/api (proxies to backend:8000)

### Build for Production

```bash
# Build optimized production bundle
npm run build

# Preview production build locally
npm run preview
```

## 📊 Key Components

### Dashboard
- **StatsCard**: Reusable metric display cards
- **SystemHealth**: Real-time system status monitoring  
- **RecentCalls**: Latest voice AI interactions
- **CallActivityChart**: Hourly call volume visualization
- **AgentPerformanceChart**: Agent success rates and metrics
- **QuickActions**: Common task shortcuts

### Agent Management
- **AgentCard**: Agent overview with quick actions
- **AgentForm**: Create/edit agent configurations
- **TestCallModal**: Initiate test calls with agents
- **PromptEditor**: Advanced prompt editing with syntax highlighting

### Call Monitoring
- **CallList**: Paginated call history with filtering
- **CallDetail**: Comprehensive call information and transcript
- **LiveCallIndicator**: Real-time active call monitoring

### Phone Number Management
- **PhoneNumberGrid**: Visual phone number assignment
- **AssignmentModal**: Assign numbers to agents
- **SyncStatus**: RetellAI synchronization status

## 🔧 Configuration

### Environment Variables
```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api/v1

# Feature Flags
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_REAL_TIME=true

# Environment
VITE_NODE_ENV=development
```

### API Proxy Setup
The Vite dev server proxies `/api` requests to the backend:

```js
// vite.config.js
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

## 🎨 Styling & Theming

### Tailwind Configuration
Custom color palette and component classes:

```js
// tailwind.config.js
theme: {
  extend: {
    colors: {
      primary: { /* blue color scale */ },
      success: { /* green color scale */ },
      warning: { /* yellow color scale */ },
      danger: { /* red color scale */ }
    }
  }
}
```

### Component Classes
Pre-built utility classes for common UI patterns:

```css
/* Button variants */
.btn-primary, .btn-secondary, .btn-success, .btn-danger

/* Card components */
.card, .card-header, .card-body, .card-footer

/* Form components */
.form-input, .form-select, .form-textarea

/* Status indicators */
.badge-*, .status-dot, .status-online, .status-offline
```

## 📱 Responsive Design

Mobile-first approach with breakpoint utilities:
- **sm**: 640px+ (tablets)
- **md**: 768px+ (small laptops)
- **lg**: 1024px+ (desktops)
- **xl**: 1280px+ (large screens)

Navigation automatically adapts:
- Mobile: Collapsible hamburger menu
- Desktop: Fixed sidebar navigation

## 🔄 State Management

### App Store (`stores/app.js`)
Global application state:
- System health monitoring
- Dashboard statistics
- User notifications
- Error handling

### Component-specific Stores
- **AgentStore**: Agent management and caching
- **CallStore**: Call history and real-time updates
- **PromptStore**: Prompt library management

## 📡 API Integration

### Service Layer (`services/api.js`)
Organized API endpoints:

```js
// Example usage
import api from '@/services/api'

// Get dashboard stats
const stats = await api.dashboard.getStats()

// Create new agent
const agent = await api.agents.create(agentData)

// List phone numbers
const phones = await api.phoneNumbers.list()
```

### Error Handling
Automatic error handling with toast notifications:
- Network errors
- HTTP error responses  
- Request timeout handling
- Retry mechanisms

## 🧪 Testing

### Component Testing
```bash
# Run component unit tests
npm run test

# Run tests in watch mode
npm run test:watch

# Generate coverage report
npm run test:coverage
```

### E2E Testing
```bash
# Run end-to-end tests
npm run test:e2e

# Run E2E tests in headless mode
npm run test:e2e:headless
```

## 🚀 Deployment

### Build Optimization
Production builds include:
- Code splitting and lazy loading
- Asset optimization and compression
- Tree shaking for minimal bundle size
- Source maps for debugging

### Docker Deployment
```dockerfile
# Multi-stage build for optimal image size
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 🔧 Development Workflow

### Code Standards
- **ESLint**: Enforces code quality rules
- **Prettier**: Consistent code formatting  
- **Vue Style Guide**: Following official Vue conventions
- **Commit Conventions**: Conventional commit messages

### Git Hooks
Pre-commit hooks ensure code quality:
```bash
# Lint and format code
npm run lint:fix
npm run format

# Run tests
npm run test:unit
```

## 📈 Performance Optimization

### Bundle Analysis
```bash
# Analyze bundle size
npm run build:analyze
```

### Optimization Strategies
- **Route-based code splitting**: Lazy load page components
- **Component lazy loading**: Dynamic imports for heavy components  
- **Image optimization**: WebP format with fallbacks
- **Caching strategies**: Service worker for offline support

## 🐛 Debugging

### Vue DevTools
Install the Vue DevTools browser extension for:
- Component inspection
- State management debugging
- Performance profiling
- Event tracking

### Console Debugging
```js
// Development helpers
if (import.meta.env.DEV) {
  console.log('Debug info:', data)
}
```

## 📚 Additional Resources

- [Vue 3 Documentation](https://vuejs.org/)
- [Vite Documentation](https://vitejs.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [Pinia Documentation](https://pinia.vuejs.org/)
- [Chart.js Documentation](https://www.chartjs.org/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 