# ⚛️ Frontend Documentation - Clinical Nutrition Platform

## نظرة عامة

Frontend مبني باستخدام React 18 مع TypeScript وTailwind CSS لتوفير واجهة مستخدم حديثة وسريعة الاستجابة.

## 🏗️ هيكل المشروع

```
frontend/
├── public/                  # الملفات العامة
│   ├── index.html          # HTML الرئيسي
│   └── manifest.json       # إعدادات PWA
├── src/
│   ├── components/         # المكونات القابلة للإعادة
│   │   ├── ui/            # مكونات واجهة المستخدم الأساسية
│   │   │   ├── button.jsx
│   │   │   ├── card.jsx
│   │   │   ├── input.jsx
│   │   │   └── toast.jsx
│   │   ├── Layout.jsx     # تخطيط الصفحة الرئيسي
│   │   └── ProtectedRoute.jsx # حماية الصفحات
│   ├── pages/             # صفحات التطبيق
│   │   ├── Home.jsx       # الصفحة الرئيسية
│   │   ├── Login.jsx      # تسجيل الدخول
│   │   ├── Register.jsx   # التسجيل
│   │   ├── Dashboard.jsx  # لوحة التحكم
│   │   ├── Subscription.jsx # إدارة الاشتراكات
│   │   ├── SubscriptionPlans.jsx # اختيار الخطط
│   │   ├── Checkout.jsx   # صفحة الدفع
│   │   ├── Affiliate.jsx  # الشراكة
│   │   ├── Profile.jsx    # الملف الشخصي
│   │   └── NutritionPlan.jsx # خطط التغذية
│   ├── lib/               # المكتبات المساعدة
│   │   ├── api.js         # عميل API
│   │   └── utils.js       # وظائف مساعدة
│   ├── store/             # إدارة الحالة
│   │   └── authStore.js   # حالة المصادقة
│   ├── App.js             # المكون الرئيسي
│   ├── index.js           # نقطة الدخول
│   └── index.css          # الأنماط الرئيسية
├── package.json           # تبعيات المشروع
├── tailwind.config.js     # إعداد Tailwind
├── postcss.config.js      # إعداد PostCSS
└── .env                   # متغيرات البيئة
```

## 📦 التبعيات الرئيسية

### المكتبات الأساسية
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "react-router-dom": "^6.20.1",
  "@tanstack/react-query": "^5.8.4",
  "zustand": "^4.4.7"
}
```

### واجهة المستخدم
```json
{
  "tailwindcss": "^3.3.0",
  "tailwind-merge": "^2.0.0",
  "tailwindcss-animate": "^1.0.7",
  "lucide-react": "^0.294.0",
  "@radix-ui/react-toast": "^1.1.5"
}
```

### المدفوعات والAPI
```json
{
  "@stripe/stripe-js": "^2.4.0",
  "@stripe/react-stripe-js": "^2.4.0",
  "axios": "^1.6.2"
}
```

## 🎨 نظام التصميم

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

### المتغيرات CSS
```css
/* src/index.css */
:root {
  --primary: 222.2 47.4% 11.2%;
  --secondary: 210 40% 96%;
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
}
```

## 🔧 إدارة الحالة

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

## 📡 تكامل API

### عميل HTTP
```javascript
// src/lib/api.js
const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: { 'Content-Type': 'application/json' }
});

// إضافة الرمز المميز تلقائياً
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### استخدام React Query
```javascript
// في المكونات
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

## 🔐 المصادقة والحماية

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

### تجديد الرموز المميزة
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

## 💳 تكامل Stripe

### إعداد Stripe
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

### معالجة الدفع المحدثة
```javascript
// src/pages/Checkout.jsx - التدفق المحسن
const CheckoutForm = ({ plan }) => {
  const stripe = useStripe();
  const elements = useElements();

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    // إنشاء PaymentMethod مباشرة
    const { error, paymentMethod } = await stripe.createPaymentMethod({
      type: 'card',
      card: elements.getElement(CardElement),
    });

    if (!error) {
      // إنشاء الاشتراك مباشرة مع PaymentMethod
      await subscriptionAPI.createSubscription({
        plan_id: plan.id,
        payment_method_id: paymentMethod.id,
      });
    }
  };
};
```

## 🎯 الصفحات الرئيسية

### الصفحة الرئيسية
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
          {/* باقي المحتوى */}
        </div>
      </section>
    </div>
  );
};
```

### لوحة التحكم
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

## 🧩 المكونات الأساسية

### مكون البطاقة
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

### مكون الزر
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

## 🔄 إدارة النماذج

### نموذج تسجيل الدخول
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

## 🚀 البناء والنشر

### أوامر التطوير
```bash
# تشغيل خادم التطوير
npm start

# بناء للإنتاج
npm run build

# تشغيل الاختبارات
npm test

# تحليل الحزمة
npm run analyze
```

### إعداد البيئة
```bash
# .env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_test_...
REACT_APP_FRONTEND_URL=http://localhost:3000
```

### بناء الإنتاج
```bash
# بناء الملفات الثابتة
npm run build

# نشر على Netlify/Vercel
npm run deploy
```

## 🎨 التخصيص والثيمات

### ألوان مخصصة
```css
/* إضافة ألوان جديدة */
:root {
  --success: 142 76% 36%;
  --warning: 38 92% 50%;
  --error: 0 84% 60%;
}
```

### مكونات مخصصة
```javascript
// إنشاء مكون جديد
const CustomCard = ({ title, children, ...props }) => (
  <Card {...props}>
    <CardHeader>
      <CardTitle>{title}</CardTitle>
    </CardHeader>
    <CardContent>{children}</CardContent>
  </Card>
);
```

## 📱 الاستجابة والموبايل

### نقاط التوقف
```javascript
// Tailwind breakpoints
sm: '640px',   // الهواتف الكبيرة
md: '768px',   // الأجهزة اللوحية
lg: '1024px',  // أجهزة الكمبيوتر المحمولة
xl: '1280px',  // أجهزة سطح المكتب
```

### تصميم متجاوب
```javascript
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {/* المحتوى */}
</div>
```

## 🧪 الاختبارات

### اختبارات المكونات
```javascript
// src/components/__tests__/Button.test.js
import { render, screen } from '@testing-library/react';
import { Button } from '../ui/button';

test('renders button with text', () => {
  render(<Button>Click me</Button>);
  expect(screen.getByText('Click me')).toBeInTheDocument();
});
```

## 🔧 أدوات التطوير

### ESLint و Prettier
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

### إعداد VS Code
```json
// .vscode/settings.json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```

## 🆕 التحديثات الأخيرة

### تحسينات نظام الاشتراكات
- **صفحة إدارة الاشتراك**: واجهة مخصصة للمشتركين النشطين
- **صفحة اختيار الخطط**: صفحة منفصلة لعرض جميع الخطط
- **التوجيه الذكي**: المشتركون يرون إدارة الاشتراك، الجدد يرون اختيار الخطط
- **تدفق دفع محسن**: استخدام `createPaymentMethod` مباشرة بدلاً من `PaymentIntent`

### الميزات الجديدة
```javascript
// صفحة إدارة الاشتراك للمشتركين النشطين
if (currentSubscription?.is_active) {
  return <SubscriptionManagementPage />;
}

// صفحة اختيار الخطط منفصلة
<Route path="/subscription/plans" element={<SubscriptionPlans />} />
```

### إصلاحات تقنية
- **إصلاح أخطاء Stripe**: حل مشاكل "No such price" و "current_period_start"
- **معالجة الأخطاء**: تحسين معالجة الأخطاء في جميع العمليات
- **تحديث البيانات**: إضافة `plan_id`, `plan_name`, `amount` للـ serializers
- **تحسين UX**: واجهات أوضح وأكثر سهولة في الاستخدام

### مسارات جديدة
```javascript
// App.js - المسارات المحدثة
<Route path="/subscription" element={<Subscription />} />
<Route path="/subscription/plans" element={<SubscriptionPlans />} />
```

### تحسينات الواجهة
- **مؤشرات الخطة الحالية**: تمييز واضح للخطة النشطة
- **أزرار إدارة**: تغيير الخطة، الإلغاء، تحديث الدفع
- **معلومات مفصلة**: عرض تفاصيل الاشتراك والأيام المتبقية
- **تصميم متجاوب**: واجهات محسنة لجميع الأجهزة

---

**آخر تحديث**: أكتوبر 2025  
**الإصدار**: 1.1.0  
**حالة الكود**: مكتمل ومجهز للإنتاج مع تحسينات UX
