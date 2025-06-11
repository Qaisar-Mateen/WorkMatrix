# WorkMatrix Front-End Application Report

## 1. Introduction and Overall Purpose

This document will provide a detailed overview of the WorkMatrix Front-End application.

## 2. Project Structure Overview

The WorkMatrix Front-End is a Next.js application, evident from the presence of `next.config.mjs`, `next-env.d.ts`, and the `app/` directory structure which is characteristic of Next.js 13+ with the App Router.

Key directories and their likely purposes:

*   **`app/`**: Core application directory for Next.js App Router. Contains layouts, pages (routes), loading states, error handlers, and API routes.
    *   `layout.tsx`: Root layout for the entire application.
    *   `page.tsx`: Entry page for the root URL.
    *   `globals.css`: Global stylesheets.
    *   Route groups like `(auth)`, `(dashboard)`, `(marketing)` suggest different application sections with potentially different layouts or purposes.
    *   Specific route directories like `admin/`, `auth/`, `employee/`, `profile/` define application paths.
*   **`components/`**: Reusable UI components (likely React components) used throughout the application. Subdirectories like `auth/`, `dashboard/`, `employee/`, `layout/`, `profile/` suggest organization by feature or section.
*   **`config/`**: Application-level configuration files (e.g., site metadata, navigation links).
*   **`contexts/`**: React Context API providers for managing global state (e.g., authentication state, theme, user preferences).
*   **`docs/`**: Project documentation, including this report.
*   **`hooks/`**: Custom React hooks to encapsulate reusable logic and stateful behavior.
*   **`lib/`**: Utility functions, helper scripts, and third-party library configurations. `websocket-service.ts` is a key file here.
*   **`public/`**: Static assets that are served directly (e.g., images, fonts, favicon.ico).
*   **`services/`**: Modules for interacting with external APIs or services, such as the Supabase backend or the WebSocket service. `background-service.ts` is likely related to interactions with the desktop background app.
*   **`styles/`**: Global styles, theme definitions, or CSS modules if not using `globals.css` exclusively or Tailwind CSS utility classes directly in components.
*   **`supabase/`**: Supabase client setup, helper functions, and potentially database migration scripts or type definitions related to Supabase.
*   **`types/`**: TypeScript type definitions for various data structures and props used in the application.

**Key Configuration Files:**

*   **`package.json`**: Defines project metadata, dependencies (like Next.js, React, Tailwind CSS, Supabase client), and scripts (for development, build, lint, test).
*   **`next.config.mjs`**: Configuration for the Next.js framework (e.g., build options, environment variables, redirects, headers).
*   **`tailwind.config.ts` (or `.js`)**: Configuration for Tailwind CSS, defining theme, plugins, and content paths.
*   **`tsconfig.json`**: TypeScript compiler options.
*   **`.env.local`, `.env.example`**: Environment variable management. `.env.local` stores actual secrets and configurations for local development (and should be gitignored), while `.env.example` serves as a template.
*   **`middleware.ts`**: Next.js middleware for running code before a request is completed (e.g., for authentication, redirects, header modification).

I will now read the `README.md` and `package.json` to understand the project's stated purpose, dependencies, and available scripts.

### 2.1. Purpose and Technology Stack (from README and package.json)

The WorkMatrix Front-End is a modern web application built with **Next.js 13** (using the App Router) and **TypeScript**. Its primary role is to provide a user interface for interacting with the data collected by the `Background-App` and to manage user accounts and settings.

It connects to:
1.  The **WorkMatrix Background-App** via WebSockets (for real-time commands like start/stop monitoring) and potentially REST APIs.
2.  **Supabase** for authentication, database interactions (PostgreSQL), and real-time data synchronization (e.g., displaying collected activity, screenshots).

**Key Technologies and Libraries:**

*   **Framework:** Next.js 13
*   **Language:** TypeScript
*   **UI Components:** React, [shadcn/ui](https://ui.shadcn.com/) (which utilizes Radix UI primitives)
*   **Styling:** [Tailwind CSS](https://tailwindcss.com/)
*   **State Management:**
    *   [TanStack Query (React Query)](https://tanstack.com/query): For managing server state, caching, and data fetching.
    *   React Context API: For global UI state.
    *   [Zustand](https://zustand.surge.sh/): Another global state management solution. The interplay between Context, Zustand, and TanStack Query will be an area to explore.
    *   Local component state (React `useState`, `useReducer`).
*   **Forms:** [React Hook Form](https://react-hook-form.com/) for building forms.
*   **Schema Validation:** [Zod](https://zod.dev/) for data validation, often used with React Hook Form.
*   **Authentication:** [Supabase Auth](https://supabase.com/auth) (handles email/password, OAuth, session management).
*   **Database Client:** [Supabase Client](https://supabase.com/docs/library/js/getting-started) for interacting with the Supabase PostgreSQL database.
*   **Real-time:** Supabase Realtime subscriptions.
*   **HTTP Client:** [Axios](https://axios-http.com/) (likely for REST API communication if not using `fetch` directly).
*   **Icons:** [Lucide Icons](https://lucide.dev/)
*   **Date/Time:** [date-fns](https://date-fns.org/)
*   **Notifications (Toasts):** [Sonner](https://sonner.emilkowal.ski/) or `react-toast` (from Radix via shadcn/ui).
*   **Theming:** `next-themes` for light/dark mode support.
*   **Linting/Formatting:** ESLint and Prettier.

### 2.2. Core Features (from README)

*   **Authentication:**
    *   Email/Password and OAuth (Google, GitHub) login.
    *   Role-Based Access Control (RBAC).
    *   Protected routes and session management.
*   **Dashboard (for monitored users/employees):**
    *   Display of monitoring data (time tracking, screenshots, activity analytics).
    *   Team management features.
    *   Project tracking capabilities.
*   **Admin Features:**
    *   User management.
    *   Team-wide analytics and activity monitoring.
    *   System settings configuration.
    *   Report generation.

### 2.3. Available Scripts (from `package.json`)

*   `npm run dev` or `pnpm dev`: Starts the Next.js development server (typically on `http://localhost:3000`).
*   `npm run build` or `pnpm build`: Builds the application for production.
*   `npm run start` or `pnpm start`: Starts a Next.js production server (after a build).
*   `npm run lint` or `pnpm lint`: Runs ESLint to check for code quality and style issues.

## 3. Detailed File System Exploration Plan

To understand the application in detail, I will now explore the contents of the following key directories and their files:

*   `app/` (Routes, layouts, core pages)
*   `components/` (Reusable UI components)
*   `lib/` (Utilities, including `websocket-service.ts`)
*   `services/` (External service integrations, e.g., `background-service.ts`)
*   `hooks/` (Custom React Hooks)
*   `contexts/` (Global state contexts)
*   `config/` (Application configuration)
*   `supabase/` (Supabase client setup and utilities)
*   `types/` (TypeScript definitions)
*   Root files like `middleware.ts`, `next.config.mjs`, `.env.local`, etc.

I will start by listing the contents of these directories.

## 4. Core Application Setup and Configuration

This section details the setup of the Next.js application, including root layouts, providers, middleware, and essential configuration files.

### 4.1. Root Layout (`app/layout.tsx`)

The `app/layout.tsx` file defines the root layout for the entire application. Key aspects include:

*   **Global Styles:** Imports `globals.css`.
*   **Font:** Uses `Inter` font from `next/font/google`.
*   **Metadata:** Sets a default title ("WorkMatrix") and description for the application.
*   **Theme Provider:** Wraps the application in `ThemeProvider` (from `@/components/theme-provider`) to enable light/dark mode, configured to use the `class` attribute and default to the system theme.
*   **Error Boundary:** Uses a custom `ErrorBoundary` component to catch rendering errors in its children.
*   **Auth Provider:** Wraps children in `AuthProvider` (from `@/hooks`), likely providing authentication context (user session, roles) throughout the app.
*   **Toaster:** Includes `<Toaster />` from `sonner` for displaying notifications.
*   **Theme Toggle:** A `ThemeToggle` component is placed in a fixed position (top-right) for easy theme switching.
*   **Structure:** Standard HTML structure (`<html>`, `<head>`, `<body>`) with language set to "en". `suppressHydrationWarning` is used on the `<html>` tag.

### 4.2. Root Page (`app/page.tsx`)

The `app/page.tsx` file serves as the entry point for the root URL (`/`). Its primary responsibility is to redirect users based on their authentication status and role:

*   **Client Component:** Declared with `"use client";`.
*   **Hooks:** Uses `useRouter` for navigation and a custom `useAuth` hook to get user, `userRole`, and `isLoading` state.
*   **Redirection Logic:**
    *   If authentication state is still loading (`isLoading`), it displays a `<Loading />` component.
    *   If not loading and no user is authenticated, it redirects to `/login`.
    *   If a user is authenticated:
        *   If `userRole` is 'admin', it redirects to `/admin/dashboard`.
        *   Otherwise (presumably 'employee' or other roles), it redirects to `/employee/dashboard`.
*   **Default View:** While redirecting or loading, it renders a `<Loading />` component.

### 4.3. Client-Side Providers (`app/providers.tsx`)

The `app/providers.tsx` file centralizes client-side providers, primarily for React Query and potentially others if `ClientProviders` from `@/components/providers/client-providers` (imported in `layout.tsx` but `providers.tsx` itself also exists) is different or used elsewhere.

*   **Client Component:** Declared with `"use client";`.
*   **React Query:**
    *   Initializes a `QueryClient` instance.
    *   Wraps children with `<QueryClientProvider>`.
    *   Includes `<ReactQueryDevtools />` for debugging React Query state (initialIsOpen set to false).
    *   Sets default options for queries: `staleTime` (1 minute), `gcTime` (5 minutes), `retry` (1), and `refetchOnWindowFocus` (false).
*   **Auth Provider:** It also wraps children in `<AuthProvider>`, which seems redundant if `app/layout.tsx` already does this. This might be an area for review to ensure providers are not nested unnecessarily or are serving distinct purposes in different parts of the component tree.
*   **Toaster:** Includes `<Toaster />` from `sonner`, also potentially redundant if present in `app/layout.tsx`.

*Self-correction: `app/layout.tsx` imports `ClientProviders` from `@/components/providers/client-providers`. The file `app/providers.tsx` seems to be a separate setup, possibly intended for a different scope or an alternative way of organizing providers. The `app/layout.tsx` is the one that actually wraps the root children. The content of `@/components/providers/client-providers.tsx` would need to be checked to understand its exact role. For now, the analysis of `app/providers.tsx` stands as is, but its usage context relative to `ClientProviders` in `layout.tsx` is noted.*

### 4.4. Global Styles (`app/globals.css`)

This file defines the global styling for the application using Tailwind CSS directives and custom CSS:

*   **Tailwind CSS:** Imports Tailwind's `base`, `components`, and `utilities` layers.
*   **CSS Variables for Theming:**
    *   Defines a comprehensive set of CSS variables for light mode (`:root`) and dark mode (`.dark`) covering background, foreground, card, popover, primary, secondary, muted, accent, destructive colors, as well as border, input, and ring colors.
    *   Includes specific variables for chart colors and sidebar elements for both themes.
*   **Base Styles:** Applies `border-border` to all elements (`*`) and sets default `bg-background` and `text-foreground` on the `body`. Enables font feature settings `rlig` and `calt`.
*   **Animations:** Defines several custom keyframe animations (`float`, `slideUp`, `slideDown`, `scale`) and utility classes to apply them (e.g., `.animate-float`, `.animate-slide-up`).
*   **Gradient Utilities:** Includes `.hero-gradient` and `.text-gradient` classes.
*   **Glassmorphism Effects:** Provides `.glass-effect` and `.glass-effect-light` classes.
*   **Enhanced Hover Effects:** Defines `.card-hover` and `.feature-icon-container` for interactive UI elements.
*   **Custom Scrollbar:** Styles the scrollbar for Webkit browsers, with different appearances for track and thumb, and hover effects. Hides the scrollbar on smaller screens (max-width: 768px) while maintaining touch scrolling.
*   **Theme Transition:** A `.theme-transition` class is defined for smooth transitions of `background-color`, `color`, and `border-color`.

### 4.5. Default Metadata (`app/metadata.ts`)

This simple file exports a `metadata` object of type `Metadata` (from Next.js) to define default site-wide metadata:

*   **Title:** "Work Matrix"
*   **Description:** "A comprehensive work management platform"

This metadata is likely imported and used in the root `app/layout.tsx` or merged with page-specific metadata.

### 4.6. Middleware (`middleware.ts`)

The `middleware.ts` file is crucial for handling requests before they reach the page or API route. It implements several important functionalities:

*   **Supabase Client:** Creates a Supabase client instance for middleware operations.
*   **Route Definitions:** Defines arrays for `PROTECTED_ROUTE_PREFIXES` (e.g., `/admin`, `/employee`), `AUTH_ROUTES` (e.g., `/login`, `/register`), and `PUBLIC_ROUTES` (e.g., `/`, `/about`).
*   **Rate Limiting (Upstash Redis):**
    *   Initializes a Redis client and a `Ratelimit` instance from `@upstash/ratelimit`.
    *   Applies rate limiting (sliding window algorithm) based on IP address for `AUTH_ROUTES`.
    *   Returns a 429 "Too Many Requests" response if the limit is exceeded.
    *   Rate limit requests and window are configurable via environment variables (`NEXT_PUBLIC_RATE_LIMIT_REQUESTS`, `NEXT_PUBLIC_RATE_LIMIT_WINDOW_MS`).
*   **CSRF Protection:**
    *   `validateCsrfToken`: Checks if the `x-csrf-token` header matches the `csrf-token` cookie for non-GET/HEAD requests.
    *   `generateCsrfToken`: Generates a new CSRF token using `nanoid`.
    *   For GET requests, if no `csrf-token` cookie exists, it generates one and sets it (httpOnly, secure in production, sameSite: 'strict').
    *   For mutating requests (POST, PUT, DELETE, etc.), it validates the CSRF token and returns a 403 if invalid.
*   **Session Management & Authentication:**
    *   Retrieves the current session using `supabase.auth.getSession()`.
    *   **Session Expiry:** Checks if the session has expired. If so, signs out the user and redirects to `/login`.
    *   **Session Refresh:** If the session is close to expiring (e.g., within 5 minutes), it attempts to refresh the session and updates the `sb-access-token` cookie.
    *   **Public Routes:** Allows access to `PUBLIC_ROUTES` and `/api/` routes.
        *   If a user is logged in and tries to access an `AUTH_ROUTE` (e.g., `/login`), they are redirected to their respective dashboard (`/admin/dashboard` or `/employee/dashboard`) based on their role fetched from the `profiles` table.
    *   **Protected Routes:**
        *   If a user is not signed in and tries to access a protected route, they are redirected to `/login` with a `redirectedFrom` query parameter.
*   **Role-Based Access Control (RBAC):**
    *   If a user is signed in, it fetches their role from the `profiles` Supabase table.
    *   If a logged-in user is on an `AUTH_ROUTE`, they are redirected to their dashboard.
    *   If a user with a role other than 'admin' tries to access an `/admin` route, they are redirected (e.g., to `/employee/dashboard` or `/`).
*   **Matcher:** The `config.matcher` specifies which routes this middleware applies to. It's configured to match most paths except for Next.js static files, image optimization files, `favicon.ico`, and files with extensions (broadly allowing public assets).

### 4.7. Next.js Configuration (`next.config.mjs`)

This file configures the Next.js build and development behavior:

*   **`reactStrictMode`:** Enabled (`true`).
*   **ESLint & TypeScript:** Configured to `ignoreDuringBuilds` and `ignoreBuildErrors` respectively. This is generally not recommended for production as it can hide issues, but might be used to speed up builds or temporarily bypass blocking errors.
*   **Images:** `unoptimized: true` is set, meaning Next.js Image Optimization will not be used. This could be for various reasons (e.g., deploying to an environment that doesn't support it well, or using an external image provider).
*   **Webpack Alias:** Adds a webpack alias `@` to point to the root directory (`.`), allowing for shorter import paths (e.g., `import foo from '@/components/foo';`).
*   **Redirects:** Includes an example of an `async redirects()` function that sets up a permanent redirect from `/` to `/home`. *Note: The `app/page.tsx` currently handles redirection from `/` based on auth state, so this redirect might conflict or be overridden by the middleware/page logic. The actual behavior would depend on the execution order.* The `README.md` also mentions `/` as a public route, while `page.tsx` redirects from `/`. This suggests `/home` might be the intended marketing/landing page if no user is logged in, or this redirect is an older configuration.

### 4.8. Environment Variables (`.env.local`, `.env.example`)

These files manage environment-specific configurations:

*   **`.env.local`:** (Content shown in previous steps)
    *   `NEXT_PUBLIC_SUPABASE_URL`: URL for the Supabase project.
    *   `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Public anonymous key for Supabase.
    *   `NEXT_PUBLIC_APP_URL`: Base URL of the application (e.g., `http://localhost:3000`).
    *   `NEXT_PUBLIC_MAX_SCREENSHOTS`: Application-specific setting (e.g., 100).
    *   `NEXT_PUBLIC_WS_URL`: WebSocket URL for connecting to the background service (e.g., `ws://localhost:8765`).
    *   `NEXT_PUBLIC_GOOGLE_CLIENT_ID`, `NEXT_PUBLIC_GOOGLE_CLIENT_SECRET`: Placeholders for Google OAuth credentials.
    *   *From `middleware.ts`, we can infer additional environment variables are expected:* `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`, `NEXT_PUBLIC_RATE_LIMIT_REQUESTS`, `NEXT_PUBLIC_RATE_LIMIT_WINDOW_MS`.
*   **`.env.example`:** Provides a template for the required environment variables, typically with placeholder or example values. It's missing the WebSocket URL and the Upstash Redis variables seen in `.env.local` or inferred from `middleware.ts`.

This covers the foundational setup. Next, I will delve into the `lib/`, `services/`, `hooks/`, and `contexts/` directories to understand shared utilities, service integrations, custom hooks, and state management.

## 5. `lib/` Directory Analysis

The `lib/` directory typically contains utility functions, helper scripts, API communication logic, and configurations for third-party libraries.

### 5.1. Root `lib/` Files

Based on previous readings, the following files are present in the root of the `lib/` directory:

*   **`lib/api.ts`**: This file likely centralizes API communication logic. It might contain functions for making HTTP requests (e.g., using `fetch` or `axios`) to the application's backend or external services. It could define typed API endpoints and handle request/response transformations and error handling for API calls.
*   **`lib/supabase-client.ts`**: This file is expected to initialize and export the Supabase client instance for use on the client-side of the application. This client is used for interacting with Supabase services like Auth, Database (PostgREST), Realtime, and Storage from browser components.
*   **`lib/supabase-realtime.ts`**: This file likely focuses on managing Supabase Realtime subscriptions. It might provide functions to subscribe to database changes (inserts, updates, deletes) on specific tables or channels, allowing the UI to update dynamically as data changes in the backend.
*   **`lib/supabase.ts`**: This could be a more general Supabase utility file. It might contain helper functions for common Supabase operations, server-side Supabase client initialization (if different from the client-side), or functions that abstract complex Supabase queries or interactions.
*   **`lib/utils.ts`**: This is a general-purpose utility file located directly within `lib/`. It likely contains various helper functions used across different parts of the application that don't fit into more specific utility modules (like date formatting, string manipulation, etc., though some of these might be in `lib/utils/`).

### 5.2. `lib/services/` Directory

This directory likely houses services that encapsulate specific business logic or interactions with external systems.

#### 5.2.1. `lib/services/websocket-service.ts`

This file is responsible for establishing and managing a WebSocket connection, primarily for real-time communication with a backend service, likely the `Background-App` for features like employee activity monitoring.

**Key Features and Functionality:**

*   **`WebSocketManager` Class:**
    *   A singleton class (`WebSocketManager.getInstance()`) ensures a single WebSocket connection instance across the application.
    *   Manages the complete lifecycle of the WebSocket: `connect`, `disconnect`, `reconnect`.
    *   Handles message sending and receiving, parsing JSON messages.
    *   Maintains and notifies about connection status changes: `connecting`, `connected`, `disconnected`, `reconnecting`.
*   **Connection Management:**
    *   Connects to the WebSocket server defined by `WS_URL` (environment variable `NEXT_PUBLIC_WS_URL`, defaulting to `ws://localhost:8765`).
    *   Implements an automatic reconnection strategy with exponential backoff (`INITIAL_RETRY_INTERVAL`, `MAX_RETRY_INTERVAL`, `MAX_RETRIES`).
    *   Utilizes a ping/pong mechanism (`PING_INTERVAL`, `PING_TIMEOUT`) to maintain the connection and detect unresponsive connections, triggering a reconnect if a pong is not received.
    *   Handles browser visibility changes (`visibilitychange` event) and network status (`online`, `offline` events) to proactively manage or re-establish the connection.
*   **Authentication:**
    *   Upon successful connection, it sends an `auth` message to the WebSocket server, including the `user_id` (obtained via `useSupabaseAuth` in the hook) and a timestamp.
*   **Message Handling:**
    *   Allows multiple parts of the application to subscribe to incoming messages (`addMessageHandler`, `removeMessageHandler`).
    *   Handles internal messages like `pong` and `error` (displaying a toast for errors).
*   **Status Handling:**
    *   Allows subscription to connection status updates (`addStatusHandler`, `removeStatusHandler`).
*   **`useWebSocket` Hook:**
    *   A custom React hook that simplifies the integration of WebSocket functionality into UI components.
    *   Retrieves the authenticated user's ID using `useSupabaseAuth` for the WebSocket authentication.
    *   Uses the `useToast` hook to provide user feedback on connection events (e.g., connected, disconnected, errors).
    *   Exposes:
        *   `connectionStatus`: The current state of the WebSocket connection.
        *   `isConnected`, `isConnecting`, `isReconnecting`: Boolean flags for convenience.
        *   `sendMessage`: A memoized function to send `WebSocketMessage` objects.
        *   `startMonitoring`, `stopMonitoring`: Specific methods to send control messages (likely to the `Background-App`).
        *   `disconnect`: A function to intentionally close the WebSocket connection.
*   **Error Handling:**
    *   Logs WebSocket errors to the console.
    *   Handles errors during message parsing.
    *   The `useWebSocket` hook displays toasts for connection failures and errors received from the server.

This service is critical for any feature requiring persistent, real-time, bi-directional communication between the front-end and the `Background-App`.

### 5.3. `lib/utils.ts` (Root Utility File)

This file provides a core utility function `cn` for conditionally joining CSS class names, which is a common pattern when using Tailwind CSS with React components.

*   **`cn(...inputs: ClassValue[]): string`**
    *   This function takes multiple arguments, each of which can be a string (a class name), an array of class names, or an object where keys are class names and values are booleans indicating whether the class should be included.
    *   It uses two helper libraries:
        *   `clsx`: A tiny utility for constructing `className` strings conditionally.
        *   `tailwind-merge`: A utility to intelligently merge Tailwind CSS classes in JavaScript without style conflicts. This is particularly useful for overriding default styles in component-based architectures.
    *   The primary purpose is to make it easier to build dynamic and conditional class lists for styling components with Tailwind CSS, ensuring that conflicting Tailwind utility classes are resolved correctly.

### 5.4. `lib/validations/` Directory

This directory is expected to contain schema definitions and validation logic, likely using a library like Zod, which was identified in the project's dependencies. These schemas are crucial for validating form inputs, API request payloads, and other data structures.

#### 5.4.1. `lib/validations/index.ts`

This file centralizes all Zod validation schemas for the application. It imports `z` from the Zod library and defines the following schemas:

*   **`signUpSchema`**: Validates data for user registration.
    *   `email`: Must be a valid email string.
    *   `password`: Minimum 8 characters, requiring at least one uppercase letter, one lowercase letter, one number, and one special character.
    *   `full_name`: Minimum 2 characters.
    *   `role`: Must be either "admin" or "employee" (enum).
    *   `department`: Optional string.
    *   `phone_number`: Optional string.

*   **`signInSchema`**: Validates data for user login.
    *   `email`: Must be a valid email string.
    *   `password`: Minimum 1 character (required).

*   **`timeLogSchema`**: Validates data for time logging entries.
    *   `start_time`: Must be a valid datetime string.
    *   `end_time`: Must be a valid datetime string.
    *   `description`: Minimum 1 character (required).

*   **`ticketSchema`**: Validates data for support tickets or tasks.
    *   `title`: Minimum 1 character (required).
    *   `description`: Minimum 1 character (required).
    *   `priority`: Must be one of "low", "medium", or "high" (enum).

*   **`documentSchema`**: Validates data for document uploads/management.
    *   `title`: Minimum 1 character (required).
    *   `description`: Optional string.
    *   `category_id`: Must be a valid UUID string (for linking to a category).
    *   `file`: Optional `File` instance (likely for file uploads).

*   **`categorySchema`**: Validates data for document categories.
    *   `name`: Minimum 1 character (required).
    *   `description`: Optional string.

*   **`profileSchema`**: Validates data for user profile updates.
    *   `full_name`: Minimum 2 characters.
    *   `department`: Optional string.
    *   `phone_number`: Optional string.
    *   `current_password`: Optional string.
    *   `new_password`: Optional string. If provided, must meet the same complexity requirements as the `signUpSchema` password.

### 5.5. `lib/store/` Directory

This directory likely contains global state management setup, possibly using Zustand, as indicated by the `create` and `persist` imports.

#### 5.5.1. `lib/store/index.ts`

This file defines a Zustand store for managing global application state. It uses the `persist` middleware to save parts of the store to `localStorage`.

**Store Interface (`AppState`):**

*   **Auth State:**
    *   `isAuthenticated`: Boolean, tracks if a user is logged in.
    *   `user`: Any | null, stores user information.
    *   `setUser`: Function to update the user object.
    *   `setIsAuthenticated`: Function to update authentication status.
*   **UI State:**
    *   `isLoading`: Boolean, for global loading indicators.
    *   `setIsLoading`: Function to set loading state.
    *   `error`: String | null, for global error messages.
    *   `setError`: Function to set global error.
*   **Theme State:**
    *   `theme`: 'light' | 'dark', current application theme.
    *   `setTheme`: Function to change the theme.
*   **Reset Function:**
    *   `reset`: Resets all state slices to their initial values.

**Store Creation (`useStore`):**

*   The store is created using `create<AppState>()` and wrapped with `persist()`.
*   **Persistence Configuration:**
    *   `name: 'app-storage'`: The key used for storing data in `localStorage`.
    *   `partialize`: A function that specifies which parts of the state should be persisted. In this configuration, only the `theme` is persisted. Sensitive data like `isAuthenticated` and `user` are explicitly excluded from persistence to avoid security risks.

This global store provides a centralized way to manage and access shared state across different components of the application, with theme preferences persisted across sessions.

### 5.6. `lib/hooks/` Directory

This directory contains custom React hooks that are specific to the `lib/` directory's concerns, likely related to services or utilities defined within `lib/`.

#### 5.6.1. `lib/hooks/useBackgroundCapture.ts`

This hook provides an interface to the `BackgroundService` (presumably defined in `lib/services/background-service.ts`, which has not been read yet). It manages background activity capture, such as screenshots and video recording, likely for employee monitoring features.

**Key Features and Functionality:**

*   **Configuration (`CaptureConfig`, `DEFAULT_CONFIG`):**
    *   Defines an extensive `CaptureConfig` interface for various settings related to timing (screenshot interval, video duration, idle threshold), storage (max size, local storage age, compression), capture triggers (idle, blur, focus, visibility, network changes), monitoring types (mouse, keyboard, scroll, network, tab visibility), and notifications.
    *   Provides `DEFAULT_CONFIG` with sensible defaults for these settings.
*   **Service Interaction:**
    *   Gets an instance of `BackgroundService`.
*   **State Management:**
    *   `isCapturing`: Boolean state to track if capture is active.
    *   `metrics`: Stores `ActivityMetrics` (type from `BackgroundService`) fetched periodically.
*   **Core Functions (exposed by the hook):**
    *   `startCapture()`: Initiates background capture (e.g., screenshots).
    *   `stopCapture()`: Stops background capture.
    *   `startVideoCapture()`: Starts video recording.
    *   `stopVideoCapture()`: Stops video recording.
    *   `pauseVideoCapture()`: Pauses video recording.
    *   `resumeVideoCapture()`: Resumes video recording.
    *   `setConfig(newConfig: Partial<CaptureConfig>)`: Updates the configuration of the `BackgroundService`.
    *   `getActivityMetrics()`: Retrieves current activity metrics from the service.
    *   `getNetworkStatus()`: Retrieves network status from the service.
    *   `getVisibilityState()`: Retrieves tab visibility state from the service.
*   **Metrics Polling:**
    *   Uses `useEffect` and `setInterval` to periodically fetch and update `ActivityMetrics` (e.g., every second).

This hook is central to the employee activity monitoring features, abstracting the complexities of the `BackgroundService`.

#### 5.6.2. `lib/hooks/useSystemMetrics.ts`

This hook is designed to gather and provide system performance metrics from the client-side and potentially a backend API.

**Key Features and Functionality:**

*   **Metrics Interface (`SystemMetrics`):**
    *   Defines the structure for metrics: `cpuUsage`, `memoryUsage`, `memoryTotal`, `memoryFree`, `timestamp`.
*   **State Management:**
    *   `metrics`: Stores the latest `SystemMetrics`.
*   **Data Fetching (`useEffect`):**
    *   Periodically fetches metrics at a configurable `interval` (defaulting to 1000ms).
    *   **Memory Metrics:**
        *   Attempts to use `performance.memory` (a non-standard browser API, but available in Chrome-based browsers) to get JavaScript heap size information (`usedJSHeapSize`, `totalJSHeapSize`).
    *   **CPU Metrics:**
        *   Attempts to fetch CPU usage from a backend endpoint: `apiClient.get('/api/metrics/cpu')` (the `apiClient` is likely defined in `lib/api/client.ts`).
        *   **Fallback CPU Estimation:** If the API call fails or `performance.memory` is unavailable, and `navigator.hardwareConcurrency` is available, it tries to estimate CPU usage based on frame rendering times (`requestAnimationFrame`) and the number of CPU cores. This is a rough estimation.
*   **Error Handling:**
    *   Logs errors to the console if fetching CPU metrics or general system metrics fails.

The hook provides a way to monitor client-side performance, which can be useful for diagnostics or understanding application resource consumption on the user's device.

### 5.7. `lib/api/` Directory

This directory is responsible for configuring and exporting the HTTP client used for making API requests to the backend or other external services.

#### 5.7.1. `lib/api/client.ts`

This file configures and exports an Axios instance (`apiClient`) for making HTTP requests. It includes interceptors for request and response handling, token management, CSRF protection, and offline support.

**Key Features and Functionality:**

*   **Axios Instance Creation:**
    *   Creates an Axios instance with a `baseURL` (from `process.env.NEXT_PUBLIC_API_URL` or defaulting to a Supabase URL `https://cfxmnmjjfjhztgznzebm.supabase.co`), a `timeout` of 10 seconds, and default `Content-Type` header set to `application/json`.
*   **Request Interceptor:**
    *   **Token Injection:** Retrieves a Supabase auth token (`supabase.auth.token`) from `localStorage` and adds it as a `Bearer` token to the `Authorization` header of outgoing requests.
    *   **CSRF Token Injection:** Retrieves a CSRF token (`XSRF-TOKEN`) from cookies and adds it to the `X-XSRF-TOKEN` header.
    *   **Offline Handling:**
        *   Checks `navigator.onLine`. If offline, it queues the request instead of sending it immediately. The request is wrapped in a Promise that resolves when the request is later processed.
*   **Response Interceptor:**
    *   **Successful Responses:** Returns the response directly.
    *   **Error Handling:**
        *   **Token Refresh (401 Unauthorized):** If a 401 error occurs and it's not a retry attempt (`_retry` flag):
            *   It attempts to refresh the Supabase token using the `refreshToken` from `localStorage` by making a POST request to `/auth/v1/token` (relative to the `baseURL`, which is Supabase).
            *   If successful, it updates the `access_token` and `refresh_token` in `localStorage` and retries the original request with the new token.
            *   If refresh fails, it redirects the user to `/login`.
        *   **Other HTTP Errors:**
            *   `401` (if not handled by refresh or if refresh fails): Shows a toast "Please log in to continue" and redirects to `/login`.
            *   `403 Forbidden`: Shows a toast "You do not have permission to perform this action".
            *   `404 Not Found`: Shows a toast "The requested resource was not found".
            *   `429 Too Many Requests`: Shows a toast "Too many requests. Please try again later" and queues the request for a later attempt.
            *   `500 Internal Server Error`: Shows a toast "An unexpected error occurred. Please try again later". If the request method is not POST, PUT, or DELETE, it queues the request for a later attempt.
            *   **Default Error:** For other response errors, it extracts a message from `error.response.data.message` if available, or shows a generic "An error occurred" toast.
        *   **Network Errors (`error.request`):** Shows a toast "Network error. Please check your connection" and queues the original request for retry.
        *   **Other Errors:** Shows a toast "An unexpected error occurred".
*   **Request Queue for Offline/Retry:**
    *   `requestQueue`: An array to hold requests that failed due to being offline or needing a retry (e.g., for 429 or 500 errors).
    *   `processQueue`: An asynchronous function to process queued requests. It retries each request up to `MAX_RETRIES` (3) times with an exponential backoff (`RETRY_DELAY`).
    *   An event listener for the `online` event on the `window` object triggers `processQueue` when the application comes back online.

This `apiClient` provides a robust way to handle API communication, including common concerns like authentication, authorization, error handling, and basic offline support with request queuing and retries.

## 6. `app/` Directory Analysis: Routing and Page Structure

The `app/` directory is the core of the Next.js application, utilizing the App Router paradigm. It contains all UI and routing logic, including layouts, pages, loading states, error boundaries, and API routes.

Route groups (directories enclosed in parentheses, like `(auth)`) are used to organize routes without affecting the URL path. They are often used to apply specific layouts or contexts to a section of the application.

I will now explore the main route groups and specific route segments.

### 6.1. `(auth)` Route Group

This route group is likely used for authentication-related pages like login, registration, password reset, etc. It has its own `layout.tsx`.

#### 6.1.1. `app/(auth)/layout.tsx`

This layout component defines the structure for pages within the `(auth)` group (e.g., `/login`, `/register`).

*   **`AuthWrapper`:** Wraps the content with an `<AuthWrapper>` component (from `@/components/auth/AuthWrapper`) with `requireAuth={false}`. This suggests that this wrapper might handle redirection if a user is already authenticated and tries to access an auth page (e.g., redirecting from `/login` to a dashboard if already logged in).
*   **Structure:**
    *   A two-column grid layout on larger screens (`lg:grid-cols-2`).
    *   **Left Side (Auth Form):**
        *   Contains a `<Header>` component (from `@/components/layout/header`) with navigation and user navigation disabled (`showNav={false}`, `showUserNav={false}`). The header is styled to be transparent and without a border.
        *   Renders the `children` (the actual page content, e.g., login form, registration form).
    *   **Right Side (Informational/Branding - hidden on small screens):**
        *   Displays a welcome message, the application name "WorkMatrix", and a brief description of its purpose.
        *   Styled with a gradient background.

This layout provides a consistent two-panel design for authentication screens, with the form on one side and branding/information on the other for larger displays.

### 6.2. `(dashboard)` Route Group

This route group is intended for all authenticated user dashboards (e.g., admin, employee). It will have its own layout and loading state.

#### 6.2.1. `app/(dashboard)/layout.tsx`

This layout component defines the main structure for all pages within the `(dashboard)` route group (e.g., `/admin/dashboard`, `/employee/dashboard`, `/profile`).

*   **Authentication & Authorization:**
    *   It wraps the content with `<AuthWrapper requireAuth={true}>`. This ensures that only authenticated users can access routes within this group. The `AuthWrapper` (presumably from `@/components/auth/AuthWrapper`) would handle redirection to a login page if the user is not authenticated.
*   **Main Structure:**
    *   Uses a `<MainLayout>` component (presumably from `@/components/layout/main-layout` or a similar path). This component likely provides the common dashboard shell, including:
        *   A `<Header>` component (from `@/components/layout/header`), which is configured to show navigation (`showNav={true}`) and user navigation (`showUserNav={true}`).
        *   A `<Sidebar>` component (from `@/components/layout/sidebar`).
        *   The main content area where `children` (the actual page content) are rendered.
*   **Providers:**
    *   The layout is wrapped with `<QueryProvider>` (likely for TanStack Query/React Query) and `<ToastProvider>` (likely for Sonner toasts). This makes client-side data fetching capabilities and toast notifications available to all dashboard pages.
*   **Styling:**
    *   The main `div` has classes for flex layout, height, and overflow, suggesting a common dashboard structure with a fixed header/sidebar and scrollable content area.

This layout establishes a consistent and authenticated environment for all dashboard-related views, providing common UI elements like header, sidebar, and necessary context providers.

#### 6.2.2. `app/(dashboard)/loading.tsx`

This file defines a loading UI that will be displayed while the content of a route segment within the `(dashboard)` group is loading. This is part of Next.js's built-in support for loading states via `loading.tsx` conventions.

*   **Functionality:**
    *   It exports a default function component named `Loading`.
    *   Renders a `<DashboardShell>` component (presumably a common shell for dashboard pages, from `@/components/layout/DashboardShell` or similar).
    *   Inside the shell, it displays a `<PageLoading />` component (from `@/components/layout/page-loading`). This component is responsible for rendering the actual loading indicator (e.g., a spinner, skeleton screen).

*   **Purpose**: Displays a loading state for the dashboard pages.
*   **Key Components**:
    *   Uses `<DashboardShell>` for consistent dashboard structure.
    *   Renders a `<PageLoading />` component to indicate that content is being loaded.

### 6.3. `(marketing)` Route Group

#### `app/(marketing)/layout.tsx`

*   **Purpose**: Defines the layout for the marketing-related pages of the application (e.g., home page, features, about).
*   **Functionality**:
    *   Provides a consistent header and navigation for marketing pages.
    *   The header is sticky and includes the application name/logo ("WorkMatrix").
    *   **Navigation Links**:
        *   "Features", "About", "Demo": These links are designed for smooth scrolling to respective sections if the user is on the `/home` page. If on other pages, they link directly to these sections on the `/home` page.
        *   "Dashboard": Links to the main application dashboard.
        *   "Login": Directs users to the employee login page (`/login/employee`).
        *   "Sign Up": Directs users to the employee registration page (`/register/employee`).
    *   Includes a `<ThemeToggle />` component for switching between light and dark modes.
    *   Features a mobile-friendly navigation menu (hamburger icon) for smaller screens.
    *   Renders the `children` prop, which represents the content of the specific marketing page being viewed.

This layout provides a consistent structure and navigation for all marketing-related pages, ensuring a cohesive user experience across the public-facing parts of the application.
