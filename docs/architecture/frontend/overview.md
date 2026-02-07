# Frontend Architecture - ContraVento

Comprehensive frontend architecture documentation for the ContraVento cycling social platform.

**Audience**: Frontend developers, full-stack developers, technical architects

---

## Table of Contents

- [Overview](#overview)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Component Architecture](#component-architecture)
- [Custom Hooks Pattern](#custom-hooks-pattern)
- [API Service Layer](#api-service-layer)
- [State Management](#state-management)
- [Form Handling](#form-handling)
- [Routing](#routing)
- [Performance Optimizations](#performance-optimizations)
- [Best Practices](#best-practices)
- [Common Patterns](#common-patterns)

---

## Overview

ContraVento frontend is a **React 18** single-page application (SPA) built with modern patterns and tools for optimal developer experience and user performance.

**Core Architecture Principles**:
1. **Component-Based**: Reusable, composable UI components
2. **Custom Hooks**: Business logic separated from UI
3. **Service Layer**: API calls isolated in service modules
4. **Type Safety**: TypeScript for compile-time error detection
5. **Declarative**: React's declarative paradigm throughout

---

## Technology Stack

### Core Framework

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 18.x | UI library with hooks and concurrent features |
| **TypeScript** | 5.x | Type-safe JavaScript |
| **Vite** | 5.x | Fast build tool and dev server |

### Key Libraries

**Routing & Navigation**:
- **react-router-dom** (6.x) - Client-side routing

**Forms & Validation**:
- **react-hook-form** (7.70.x) - Performant form handling
- **zod** - Schema validation with TypeScript inference

**HTTP Client**:
- **axios** - Promise-based HTTP client
- **axios-retry** - Automatic retry with exponential backoff

**Maps & Geospatial**:
- **react-leaflet** (4.2.x) - React components for Leaflet.js
- **leaflet** (1.9.x) - Interactive maps

**Charts & Visualization**:
- **recharts** (3.7.x) - Declarative charts for React

**File Upload**:
- **react-dropzone** - Drag-and-drop file uploads

**UI Components**:
- **yet-another-react-lightbox** - Photo gallery lightbox
- **react-hot-toast** - Toast notifications

---

## Project Structure

```
frontend/
├── src/
│   ├── assets/             # Static assets (images, icons)
│   │   └── images/
│   │
│   ├── components/         # React components (organized by feature)
│   │   ├── auth/           # Authentication components
│   │   ├── comments/       # Comment system
│   │   ├── common/         # Shared components (Button, Modal, etc.)
│   │   ├── dashboard/      # Dashboard widgets
│   │   ├── feed/           # Public feed components
│   │   ├── landing/        # Landing page
│   │   ├── layout/         # Layout components (Header, Footer)
│   │   ├── likes/          # Like system
│   │   ├── profile/        # User profile components
│   │   ├── routing/        # Routing components (ProtectedRoute)
│   │   ├── social/         # Social features (Follow, Followers)
│   │   ├── trips/          # Trip components (TripCard, TripMap)
│   │   └── wizard/         # Multi-step wizards
│   │
│   ├── contexts/           # React Context providers
│   │   └── AuthContext.tsx # Authentication state
│   │
│   ├── hooks/              # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useTripForm.ts
│   │   ├── useTripPhotos.ts
│   │   ├── useGPXUpload.ts
│   │   ├── useReverseGeocode.ts
│   │   └── ... (30+ custom hooks)
│   │
│   ├── pages/              # Page components (routes)
│   │   ├── DashboardPage.tsx
│   │   ├── FeedPage.tsx
│   │   ├── TripDetailPage.tsx
│   │   ├── TripEditPage.tsx
│   │   └── ... (15+ pages)
│   │
│   ├── services/           # API service layer
│   │   ├── api.ts          # Axios instance configuration
│   │   ├── authService.ts
│   │   ├── tripsService.ts
│   │   ├── gpxService.ts
│   │   ├── geocodingService.ts
│   │   └── ... (18+ services)
│   │
│   ├── utils/              # Utility functions
│   │   ├── tripHelpers.ts
│   │   ├── dateFormatters.ts
│   │   ├── photoHelpers.ts
│   │   └── geocodingCache.ts
│   │
│   ├── lib/                # Third-party library configs
│   │
│   ├── App.tsx             # Root component
│   ├── main.tsx            # Entry point
│   └── vite-env.d.ts       # Vite TypeScript declarations
│
├── public/                 # Static files served as-is
├── package.json            # Dependencies
├── tsconfig.json           # TypeScript configuration
├── vite.config.ts          # Vite build configuration
└── .env.example            # Environment variables template
```

---

## Component Architecture

### Container/Presentational Pattern

ContraVento follows the **smart/dumb component** pattern for separation of concerns.

**Smart Components** (Pages):
- Manage state with custom hooks
- Handle API calls and side effects
- Pass data and callbacks to presentational components

**Dumb Components** (UI Components):
- Receive data via props
- Display UI based on props
- No direct API calls or complex logic
- Highly reusable

### Example: Trip List

**Smart Container** (Page):
```typescript
// src/pages/TripsPage.tsx
export const TripsPage: React.FC = () => {
  const { username } = useParams<{ username: string }>();
  const { trips, isLoading, error } = useTripList(username);
  const { filters, setFilter } = useTripFilters();

  if (isLoading) return <Spinner />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div className="trips-page">
      <TripFilters filters={filters} onChange={setFilter} />
      <TripGrid trips={trips} />
    </div>
  );
};
```

**Dumb Presentational** (Component):
```typescript
// src/components/trips/TripGrid.tsx
interface TripGridProps {
  trips: Trip[];
}

export const TripGrid: React.FC<TripGridProps> = ({ trips }) => {
  return (
    <div className="trip-grid">
      {trips.map((trip) => (
        <TripCard key={trip.trip_id} trip={trip} />
      ))}
    </div>
  );
};
```

**Benefits**:
- ✅ Testability (UI components easy to test with different props)
- ✅ Reusability (TripGrid can be used anywhere)
- ✅ Maintainability (clear separation of concerns)

---

## Custom Hooks Pattern

Custom hooks encapsulate **business logic** and **stateful behavior** for reuse across components.

### Categories of Hooks

**Data Fetching Hooks**:
- `useTripList()` - Fetch trips with filters
- `usePublicTrips()` - Fetch public feed
- `useStats()` - Fetch user statistics
- `useComments()` - Fetch trip comments

**Form Hooks**:
- `useTripForm()` - Trip creation/edit form logic
- `useProfileEdit()` - Profile edit form
- `usePhotoUpload()` - Photo upload with progress

**Feature Hooks**:
- `useGPXUpload()` - GPX file upload and processing
- `useReverseGeocode()` - Reverse geocoding with caching
- `useMapProfileSync()` - Map-profile synchronization
- `useLike()` - Like/unlike functionality
- `useFollow()` - Follow/unfollow logic

**Utility Hooks**:
- `useDebounce()` - Debounce input values
- `useCountdown()` - Countdown timer
- `useSEO()` - Dynamic meta tags
- `useUnsavedChanges()` - Detect unsaved form changes

### Example: useTripList Hook

```typescript
// src/hooks/useTripList.ts
import { useState, useEffect } from 'react';
import { getUserTrips } from '../services/tripsService';
import type { Trip, TripFilters } from '../types/trip';

export const useTripList = (username: string, filters?: TripFilters) => {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTrips = async () => {
      try {
        setIsLoading(true);
        const response = await getUserTrips(username, filters);
        setTrips(response.data);
        setError(null);
      } catch (err: any) {
        setError(err.response?.data?.error?.message || 'Error al cargar viajes');
      } finally {
        setIsLoading(false);
      }
    };

    fetchTrips();
  }, [username, JSON.stringify(filters)]);

  return { trips, isLoading, error };
};
```

**Usage in Component**:
```typescript
const { trips, isLoading, error } = useTripList('johndoe', {
  status: 'published',
  tag: 'bikepacking'
});
```

**Benefits**:
- ✅ Reusable across multiple components
- ✅ Testable in isolation
- ✅ Encapsulates complex logic
- ✅ Type-safe with TypeScript

---

## API Service Layer

All API calls are isolated in **service modules** using Axios.

### Axios Instance Configuration

**Base configuration** (`src/services/api.ts`):

```typescript
import axios from 'axios';
import axiosRetry from 'axios-retry';

// Determine API base URL based on environment
const getBaseURL = (): string => {
  // Production/Docker with proxy: Use '/api' prefix
  if (import.meta.env.VITE_USE_PROXY === 'true') {
    return '/api';
  }

  // Development without Docker: Direct API URL
  return import.meta.env.VITE_API_URL || 'http://localhost:8000';
};

const api = axios.create({
  baseURL: getBaseURL(),
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

// Configure automatic retries
axiosRetry(api, {
  retries: 3,
  retryDelay: axiosRetry.exponentialDelay, // 1s, 2s, 4s
  retryCondition: (error) => {
    // Retry on network errors or 5xx server errors
    return !error.response || (error.response.status >= 500);
  },
});

// Request interceptor: Add access token
api.interceptors.request.use((config) => {
  const accessToken = localStorage.getItem('access_token');
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

// Response interceptor: Automatic token refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401 && !error.config._retry) {
      error.config._retry = true;
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post('/auth/refresh', { refreshToken });
        localStorage.setItem('access_token', response.data.access_token);
        error.config.headers.Authorization = `Bearer ${response.data.access_token}`;
        return api(error.config); // Retry original request
      } catch (refreshError) {
        // Refresh failed → logout
        localStorage.clear();
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
```

### Service Module Example

```typescript
// src/services/tripsService.ts
import api from './api';
import type { Trip, TripCreateInput, TripFilters } from '../types/trip';

export const getUserTrips = async (
  username: string,
  filters?: TripFilters
): Promise<{ success: boolean; data: Trip[] }> => {
  const params = new URLSearchParams();
  if (filters?.status) params.append('status', filters.status);
  if (filters?.tag) params.append('tag', filters.tag);

  const response = await api.get(`/users/${username}/trips?${params}`);
  return response.data;
};

export const getTripById = async (
  tripId: string
): Promise<Trip> => {
  const response = await api.get(`/trips/${tripId}`);
  return response.data.data;
};

export const createTrip = async (
  data: TripCreateInput
): Promise<Trip> => {
  const response = await api.post('/trips', data);
  return response.data.data;
};

export const updateTrip = async (
  tripId: string,
  data: Partial<TripCreateInput>
): Promise<Trip> => {
  const response = await api.put(`/trips/${tripId}`, data);
  return response.data.data;
};

export const deleteTrip = async (tripId: string): Promise<void> => {
  await api.delete(`/trips/${tripId}`);
};

export const publishTrip = async (tripId: string): Promise<Trip> => {
  const response = await api.post(`/trips/${tripId}/publish`);
  return response.data.data;
};
```

**Benefits**:
- ✅ Centralized API logic
- ✅ Type-safe with TypeScript
- ✅ Automatic retry on failures
- ✅ Token refresh handling
- ✅ Easy to mock in tests

---

## State Management

ContraVento uses **React Context + local state** (no Redux/Zustand).

### AuthContext

**Global authentication state** managed with React Context:

```typescript
// src/contexts/AuthContext.tsx
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing token on mount
    const token = localStorage.getItem('access_token');
    if (token) {
      fetchCurrentUser();
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    const response = await authService.login({ email, password });
    localStorage.setItem('access_token', response.access_token);
    localStorage.setItem('refresh_token', response.refresh_token);
    setUser(response.user);
  };

  const logout = () => {
    localStorage.clear();
    setUser(null);
    navigate('/');
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook for accessing auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

**Usage**:
```typescript
const { user, isAuthenticated, logout } = useAuth();

if (!isAuthenticated) {
  return <Navigate to="/login" />;
}
```

### Local State

Most state is **local to components** using `useState`:

```typescript
const [trips, setTrips] = useState<Trip[]>([]);
const [isLoading, setIsLoading] = useState(false);
const [selectedTrip, setSelectedTrip] = useState<Trip | null>(null);
```

**When to use Context vs Local State**:
- **Context**: Global data needed across many components (auth, theme)
- **Local State**: Component-specific data (form values, UI toggles)

---

## Form Handling

Forms use **React Hook Form** + **Zod** for validation.

### Form Pattern

```typescript
// Define Zod schema
const tripSchema = z.object({
  title: z.string().min(5, 'Título muy corto').max(200, 'Título muy largo'),
  description: z.string().min(50, 'Descripción debe tener al menos 50 caracteres'),
  start_date: z.string().refine((val) => !isNaN(Date.parse(val)), 'Fecha inválida'),
  distance_km: z.number().positive('Distancia debe ser positiva').optional(),
  tags: z.array(z.string()).max(10, 'Máximo 10 etiquetas'),
});

type TripFormData = z.infer<typeof tripSchema>;

// Component with form
const TripForm: React.FC = () => {
  const { register, handleSubmit, formState: { errors } } = useForm<TripFormData>({
    resolver: zodResolver(tripSchema),
  });

  const onSubmit = async (data: TripFormData) => {
    try {
      await createTrip(data);
      toast.success('Viaje creado correctamente');
      navigate('/trips');
    } catch (error: any) {
      toast.error(error.response?.data?.error?.message || 'Error al crear viaje');
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('title')} />
      {errors.title && <span>{errors.title.message}</span>}

      <textarea {...register('description')} />
      {errors.description && <span>{errors.description.message}</span>}

      <button type="submit">Crear Viaje</button>
    </form>
  );
};
```

**Benefits**:
- ✅ Type-safe validation
- ✅ Client-side validation before API call
- ✅ Performance (uncontrolled inputs)
- ✅ Schema reusable across frontend/backend

---

## Routing

React Router 6 with protected routes:

```typescript
// src/App.tsx
<BrowserRouter>
  <Routes>
    {/* Public routes */}
    <Route path="/" element={<LandingPage />} />
    <Route path="/login" element={<LoginPage />} />
    <Route path="/register" element={<RegisterPage />} />

    {/* Protected routes */}
    <Route element={<ProtectedRoute />}>
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="/trips/new" element={<TripCreatePage />} />
      <Route path="/trips/:tripId/edit" element={<TripEditPage />} />
    </Route>

    {/* Public trip views */}
    <Route path="/trips/:tripId" element={<TripDetailPage />} />
    <Route path="/users/:username/trips" element={<TripsPage />} />

    <Route path="*" element={<NotFoundPage />} />
  </Routes>
</BrowserRouter>
```

**ProtectedRoute component**:
```typescript
const ProtectedRoute: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) return <Spinner />;

  return isAuthenticated ? <Outlet /> : <Navigate to="/login" />;
};
```

---

## Performance Optimizations

### 1. Code Splitting

```typescript
// Lazy load routes
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const TripDetailPage = lazy(() => import('./pages/TripDetailPage'));

<Suspense fallback={<Spinner />}>
  <Route path="/dashboard" element={<DashboardPage />} />
</Suspense>
```

### 2. Memoization

```typescript
const MemoizedTripCard = React.memo(TripCard, (prev, next) => {
  return prev.trip.trip_id === next.trip.trip_id;
});
```

### 3. Debouncing

```typescript
const useDebounce = (value: string, delay: number) => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
};

// Usage
const searchQuery = useDebounce(inputValue, 500);
```

### 4. Caching

```typescript
// Geocoding cache (LRU, 100 entries)
const geocodingCache = new GeocodingCache(100);

export const reverseGeocode = async (lat: number, lng: number) => {
  const cached = geocodingCache.get(lat, lng);
  if (cached) return cached;

  const result = await callNominatimAPI(lat, lng);
  geocodingCache.set(lat, lng, result);
  return result;
};
```

---

## Best Practices

### 1. TypeScript Strict Mode

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true
  }
}
```

### 2. Props Interfaces

```typescript
interface TripCardProps {
  trip: Trip;
  onClick?: (tripId: string) => void;
  showActions?: boolean;
}

export const TripCard: React.FC<TripCardProps> = ({
  trip,
  onClick,
  showActions = true
}) => { ... };
```

### 3. Error Boundaries

```typescript
class ErrorBoundary extends React.Component {
  state = { hasError: false };

  static getDerivedStateFromError(error: Error) {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback />;
    }
    return this.props.children;
  }
}
```

### 4. Spanish User-Facing Text

All user-facing text in Spanish:

```typescript
// ✅ GOOD
toast.success('Viaje creado correctamente');
throw new Error('El viaje no fue encontrado');

// ❌ BAD
toast.success('Trip created successfully');
```

---

## Common Patterns

### Pattern: Wizard (Multi-Step Forms)

```typescript
const [currentStep, setCurrentStep] = useState(0);
const { control, watch, setValue } = useForm();

const steps = [
  <Step1BasicInfo control={control} />,
  <Step2StoryTags control={control} />,
  <Step3Photos />,
  <Step4Review data={watch()} />
];

return (
  <div>
    {steps[currentStep]}
    {currentStep > 0 && <button onClick={() => setCurrentStep(s => s - 1)}>Anterior</button>}
    {currentStep < 3 && <button onClick={() => setCurrentStep(s => s + 1)}>Siguiente</button>}
    {currentStep === 3 && <button onClick={handleSubmit}>Publicar</button>}
  </div>
);
```

### Pattern: Photo URLs

```typescript
export const getPhotoUrl = (url: string | null | undefined): string => {
  if (!url) return '/images/placeholders/trip-placeholder.jpg';

  // Backend returns absolute URLs
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url;
  }

  // Relative path (development fallback)
  return `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${url}`;
};
```

---

## Related Documentation

- **[Backend Architecture](../backend/overview.md)** - Complete backend guide
- **[API Reference](../../api/README.md)** - API endpoints
- **[Testing](../../testing/README.md)** - Frontend testing strategies
- **[User Guides](../../user-guides/README.md)** - End-user documentation
- **[Deployment](../../deployment/README.md)** - Frontend deployment

---

**Last Updated**: 2026-02-07
**Status**: ✅ Complete
**Framework**: React 18 + TypeScript 5 + Vite 5
