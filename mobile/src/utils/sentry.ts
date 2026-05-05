/**
 * Sentry Error Tracking Configuration
 * 
 * Setup instructions:
 * 1. Install Sentry: npm install @sentry/react-native
 * 2. Run: npx @sentry/wizard@latest -i reactNative
 * 3. Set SENTRY_DSN in your environment variables
 * 4. Import and initialize in App.tsx
 */

import * as Sentry from '@sentry/react-native';
import Constants from 'expo-constants';

// Get DSN from environment or Constants
const SENTRY_DSN = process.env.EXPO_PUBLIC_SENTRY_DSN || Constants.expoConfig?.extra?.sentryDsn;

/**
 * Initialize Sentry error tracking
 * Call this early in your app initialization (App.tsx)
 */
export const initSentry = () => {
  if (!SENTRY_DSN) {
    console.warn('Sentry DSN not configured. Error tracking disabled.');
    return;
  }

  Sentry.init({
    dsn: SENTRY_DSN,
    
    // Set environment (development, staging, production)
    environment: __DEV__ ? 'development' : 'production',
    
    // Enable in production, disable in development to reduce noise
    enabled: !__DEV__,
    
    // Tracing - performance monitoring
    tracesSampleRate: 0.2, // 20% of transactions
    
    // Session tracking
    enableAutoSessionTracking: true,
    sessionTrackingIntervalMillis: 30000, // 30 seconds
    
    // Automatic breadcrumbs
    enableNative: true,
    enableNativeCrashHandling: true,
    enableNativeNagger: __DEV__, // Nag in development if native modules not linked
    
    // Attach stack traces to errors
    attachStacktrace: true,
    
    // Before send callback - filter sensitive data
    beforeSend(event, hint) {
      // Filter out sensitive data from event
      if (event.request) {
        // Remove authorization headers
        if (event.request.headers) {
          delete event.request.headers.Authorization;
          delete event.request.headers.authorization;
        }
        
        // Remove tokens from URLs
        if (event.request.url) {
          event.request.url = event.request.url.replace(/token=[^&]+/gi, 'token=REDACTED');
        }
      }
      
      // Remove password fields from extra data
      if (event.extra) {
        Object.keys(event.extra).forEach(key => {
          if (key.toLowerCase().includes('password') || key.toLowerCase().includes('token')) {
            event.extra![key] = 'REDACTED';
          }
        });
      }
      
      return event;
    },
    
    // Integrations
    integrations: [
      new Sentry.ReactNativeTracing({
        // Trace navigation events
        routingInstrumentation: new Sentry.ReactNavigationInstrumentation(),
        
        // Trace API calls
        traceFetch: true,
        traceXHR: true,
        
        // Idle timeout
        idleTimeout: 5000,
      }),
    ],
  });

  console.log('Sentry initialized for error tracking');
};

/**
 * Set user context for error tracking
 * Call this after login
 */
export const setUserContext = (user: { id: number; email: string; role: string }) => {
  Sentry.setUser({
    id: user.id.toString(),
    email: user.email,
    role: user.role,
  });
};

/**
 * Clear user context
 * Call this on logout
 */
export const clearUserContext = () => {
  Sentry.setUser(null);
};

/**
 * Add custom breadcrumb
 */
export const addBreadcrumb = (message: string, category: string, data?: any) => {
  Sentry.addBreadcrumb({
    message,
    category,
    data,
    level: 'info',
  });
};

/**
 * Capture custom error
 */
export const captureError = (error: Error, context?: Record<string, any>) => {
  Sentry.captureException(error, {
    extra: context,
  });
};

/**
 * Capture custom message
 */
export const captureMessage = (message: string, level: 'info' | 'warning' | 'error' = 'info') => {
  Sentry.captureMessage(message, level);
};

/**
 * Set custom tag
 */
export const setTag = (key: string, value: string) => {
  Sentry.setTag(key, value);
};

/**
 * Set custom context
 */
export const setContext = (name: string, context: Record<string, any>) => {
  Sentry.setContext(name, context);
};

/**
 * Wrap component with Sentry error boundary
 * Use this instead of the custom ErrorBoundary for production
 */
export const ErrorBoundary = Sentry.ErrorBoundary;

/**
 * HOC to wrap screens with error tracking
 */
export const withErrorTracking = (ScreenComponent: React.ComponentType<any>, screenName: string) => {
  return (props: any) => {
    Sentry.addBreadcrumb({
      message: `Navigated to ${screenName}`,
      category: 'navigation',
      level: 'info',
    });
    
    return <ScreenComponent {...props} />;
  };
};

// Export Sentry for advanced usage
export { Sentry };

/**
 * Example usage in App.tsx:
 * 
 * import { initSentry } from './src/utils/sentry';
 * 
 * // Initialize Sentry before rendering
 * initSentry();
 * 
 * export default function App() {
 *   return (
 *     <ErrorBoundary fallback={<ErrorFallback />}>
 *       <AuthProvider>
 *         <QueryClientProvider client={queryClient}>
 *           <NavigationContainer>
 *             <RootNavigator />
 *           </NavigationContainer>
 *         </QueryClientProvider>
 *       </AuthProvider>
 *     </ErrorBoundary>
 *   );
 * }
 * 
 * Example usage in AuthContext:
 * 
 * import { setUserContext, clearUserContext } from '../utils/sentry';
 * 
 * const login = async (email, password) => {
 *   const response = await authApi.login(email, password);
 *   setUser(response.data.user);
 *   setUserContext(response.data.user);
 * };
 * 
 * const logout = async () => {
 *   await authApi.logout();
 *   clearUserContext();
 *   setUser(null);
 * };
 */
