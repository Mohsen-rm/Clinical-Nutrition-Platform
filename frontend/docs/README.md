# ⚛️ Frontend Documentation - Clinical Nutrition Platform

## Overview

Frontend built with React 18, TypeScript, and Tailwind CSS to provide a modern, responsive UI.

## 🏗️ Project Structure

```
frontend/
├── public/                  # Public files
│   ├── index.html          # Main HTML
│   └── manifest.json       # PWA settings
├── src/
│   ├── components/         # Reusable components
│   │   ├── ui/            # Core UI components
│   │   │   ├── button.jsx
│   │   │   ├── card.jsx
│   │   │   ├── input.jsx
│   │   │   └── toast.jsx
│   │   ├── Layout.jsx     # Main page layout
│   │   └── ProtectedRoute.jsx # Route protection
│   ├── pages/             # App pages
│   │   ├── Home.jsx       # Home page
│   │   ├── Login.jsx      # Login
│   │   ├── Register.jsx   # Register
│   │   ├── Dashboard.jsx  # Dashboard
│   │   ├── Subscription.jsx # Subscription management
│   │   ├── SubscriptionPlans.jsx # Plan selection
│   │   ├── Checkout.jsx   # Checkout page
│   │   ├── Affiliate.jsx  # Affiliate
│   │   ├── Profile.jsx    # Profile
│   │   └── NutritionPlan.jsx # Nutrition plans
│   ├── lib/               # Helper libraries
│   │   ├── api.js         # API client
│   │   └── utils.js       # Helper functions
│   ├── store/             # State management
│   │   └── authStore.js   # Auth state
│   ├── App.js             # Root component
│   ├── index.js           # Entry point
│   └── index.css          # Global styles
├── package.json           # Project dependencies
├── tailwind.config.js     # Tailwind config
├── postcss.config.js      # PostCSS config
└── .env                   # Environment variables
```

## 📦 Main Dependencies

### Core libraries
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "react-router-dom": "^6.20.1",
  "@tanstack/react-query": "^5.8.4",
  "zustand": "^4.4.7"
}
```

### UI
```json
{
  "tailwindcss": "^3.3.0",
  "tailwind-merge": "^2.0.0",
  "tailwindcss-animate": "^1.0.7",
  "lucide-react": "^0.294.0",
  "@radix-ui/react-toast": "^1.1.5"
}
```

### Payments and API
```json
{
  "@stripe/stripe-js": "^2.4.0",
  "@stripe/react-stripe-js": "^2.4.0",
  "axios": "^1.6.2"
}
```

## 🎨 Design System

### إعداد Tailwind CSS
```javascript
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: "hsl(var(--primary))",
        secondary: "hsl(var(--secondary))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
      }
    }
  }
}
```

### CSS variables
```css
/* src/index.css */
:root {
  --primary: 222.2 47.4% 11.2%;
  --secondary: 210 40% 96%;
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
}
```

## 🔧 State Management

### Zustand Store
```javascript
// src/store/authStore.js
const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      
      login: (userData, tokens) => {
        localStorage.setItem('access_token', tokens.access);
        localStorage.setItem('refresh_token', tokens.refresh);
        set({ user: userData, isAuthenticated: true });
      },
      
      logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        set({ user: null, isAuthenticated: false });
      }
    })
  )
);
```

## 📡 API Integration

### HTTP client
```javascript
// src/lib/api.js
const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: { 'Content-Type': 'application/json' }
});

// Add token automatically
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### Using React Query
```javascript
// In components
const { data: plans, isLoading } = useQuery({
  queryKey: ['subscription-plans'],
  queryFn: subscriptionAPI.getPlans,
});

const mutation = useMutation({
  mutationFn: authAPI.login,
  onSuccess: (data) => {
    login(data.user, data.tokens);
    navigate('/dashboard');
  }
});
```

## 🔐 Authentication & Protection

### حماية الصفحات
```javascript
// src/components/ProtectedRoute.jsx
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuthStore();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
};
```

### Token refresh
```javascript
// تجديد تلقائي للرموز
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post('/api/auth/token/refresh/', {
            refresh: refreshToken,
          });
          localStorage.setItem('access_token', response.data.access);
          return api(error.config);
        } catch (refreshError) {
          logout();
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);
```

## 💳 Stripe Integration

### Setup Stripe
```javascript
// src/App.js
import { loadStripe } from '@stripe/stripe-js';
import { Elements } from '@stripe/react-stripe-js';

const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY);

function App() {
  return (
    <Elements stripe={stripePromise}>
      {/* باقي التطبيق */}
    </Elements>
  );
}
```

### Updated payment flow
```javascript
// src/pages/Checkout.jsx - improved flow
const CheckoutForm = ({ plan }) => {
  const stripe = useStripe();
  const elements = useElements();

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    // Create PaymentMethod directly
    const { error, paymentMethod } = await stripe.createPaymentMethod({
      type: 'card',
      card: elements.getElement(CardElement),
    });

    if (!error) {
      // Create subscription directly with PaymentMethod
      await subscriptionAPI.createSubscription({
        plan_id: plan.id,
        payment_method_id: paymentMethod.id,
      });
    }
  };
};
```

## 🎯 Main Pages

### Home page
```javascript
// src/pages/Home.jsx
const Home = () => {
  return (
    <div className="min-h-screen">
      <section className="bg-gradient-to-r from-primary/10 to-primary/5 py-20">
        <div className="max-w-7xl mx-auto px-4">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            Clinical Nutrition Platform
          </h1>
          {/* Rest of content */}
        </div>
      </section>
    </div>
  );
};
```

### Dashboard
```javascript
// src/pages/Dashboard.jsx
const Dashboard = () => {
  const { user, isDoctor } = useAuthStore();
  
  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {isDoctor() ? <DoctorDashboard /> : <PatientDashboard />}
    </div>
  );
};
```

## 🧩 Core Components

### Card component
```javascript
// src/components/ui/card.jsx
const Card = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "rounded-lg border bg-card text-card-foreground shadow-sm",
      className
    )}
    {...props}
  />
));
```

### Button component
```javascript
// src/components/ui/button.jsx
const Button = React.forwardRef(({ className, variant, size, ...props }, ref) => {
  return (
    <button
      className={cn(buttonVariants({ variant, size, className }))}
      ref={ref}
      {...props}
    />
  );
});
```

## 🔄 Form Management

### Login form
```javascript
// src/pages/Login.jsx
const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const loginMutation = useMutation({
    mutationFn: authAPI.login,
    onSuccess: (response) => {
      login(response.data.user, response.data.tokens);
      navigate('/dashboard');
    }
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    loginMutation.mutate(formData);
  };
};
```

## 🚀 Build & Deployment

### Development commands
```bash
# Start dev server
npm start

# Build for production
npm run build

# Run tests
npm test

# Analyze bundle
npm run analyze
```

### Environment setup
```bash
# .env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_test_...
REACT_APP_FRONTEND_URL=http://localhost:3000
```

### Production build
```bash
# Build static files
npm run build

# Deploy to Netlify/Vercel
npm run deploy
```

## 🎨 Customization & Themes

### Custom colors
```css
/* Add new colors */
:root {
  --success: 142 76% 36%;
  --warning: 38 92% 50%;
  --error: 0 84% 60%;
}
```

### Custom components
```javascript
// Create a new component
const CustomCard = ({ title, children, ...props }) => (
  <Card {...props}>
    <CardHeader>
      <CardTitle>{title}</CardTitle>
    </CardHeader>
    <CardContent>{children}</CardContent>
  </Card>
);
```

## 📱 Responsiveness & Mobile

### Breakpoints
```javascript
// Tailwind breakpoints
sm: '640px',   // Large phones
md: '768px',   // Tablets
lg: '1024px',  // Laptops
xl: '1280px',  // Desktops
```

### Responsive layout
```javascript
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {/* Content */}
</div>
```

## 🧪 Tests

### Component tests
```javascript
// src/components/__tests__/Button.test.js
import { render, screen } from '@testing-library/react';
import { Button } from '../ui/button';

test('renders button with text', () => {
  render(<Button>Click me</Button>);
  expect(screen.getByText('Click me')).toBeInTheDocument();
});
```

## 🔧 Developer Tools

### ESLint & Prettier
```json
// .eslintrc.js
{
  "extends": ["react-app", "react-app/jest"],
  "rules": {
    "no-unused-vars": "warn",
    "no-console": "warn"
  }
}
```

### VS Code setup
```json
// .vscode/settings.json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```

## 🆕 Recent Updates

### Subscription system improvements
 - **Subscription Management page**: Dedicated UI for active subscribers
 - **Plan Selection page**: Separate page to show all plans
 - **Smart routing**: Active subscribers see management; new users see plans
 - **Improved payment flow**: Use `createPaymentMethod` directly instead of `PaymentIntent`

### New features
```javascript
// Subscription management page for active subscribers
if (currentSubscription?.is_active) {
  return <SubscriptionManagementPage />;
}

// Separate plan selection page
<Route path="/subscription/plans" element={<SubscriptionPlans />} />
```

### Technical fixes
 - **Stripe bug fixes**: Resolved "No such price" and "current_period_start"
 - **Error handling**: Improved across all flows
 - **Data updates**: Added `plan_id`, `plan_name`, `amount` to serializers
 - **UX improvements**: Clearer, more usable UI

### New routes
```javascript
// App.js - updated routes
<Route path="/subscription" element={<Subscription />} />
<Route path="/subscription/plans" element={<SubscriptionPlans />} />
```

### UI improvements
 - **Current plan indicators**: Clear highlighting of the active plan
 - **Management actions**: Change plan, cancel, update payment
 - **Detailed info**: Show subscription details and remaining days
 - **Responsive design**: Improved across devices

---

**Last updated**: October 2025  
**Version**: 1.1.0  
**Code status**: Complete and production-ready with UX improvements
