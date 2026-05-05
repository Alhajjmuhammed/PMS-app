// Environment configuration
// REQUIRED: Set EXPO_PUBLIC_API_BASE_URL in your .env file
// Example .env file:
//   Development: EXPO_PUBLIC_API_BASE_URL=http://localhost:8000
//   Production:  EXPO_PUBLIC_API_BASE_URL=https://api.yourhotel.com

const getApiBaseUrl = (): string => {
  const envApiBase = process.env.EXPO_PUBLIC_API_BASE_URL;
  
  if (envApiBase) {
    // Enforce HTTPS in production
    if (!__DEV__ && !envApiBase.startsWith('https://')) {
      throw new Error(
        'Production API must use HTTPS. Update EXPO_PUBLIC_API_BASE_URL in your .env file.'
      );
    }
    return envApiBase;
  }
  
  // Development fallback (only in dev mode)
  if (__DEV__) {
    console.warn(
      'Using default API URL. Set EXPO_PUBLIC_API_BASE_URL in .env for your environment.'
    );
    return 'http://localhost:8000';
  }
  
  // Production requires explicit configuration
  throw new Error(
    'API_BASE_URL not configured. Set EXPO_PUBLIC_API_BASE_URL environment variable before building.'
  );
};

const API_BASE_URL = getApiBaseUrl();

export const ENV = {
  development: {
    API_URL: `${API_BASE_URL}/api/v1`,
    API_BASE_URL: API_BASE_URL,
    IS_DEV: true,
  },
  production: {
    API_URL: `${API_BASE_URL}/api/v1`,
    API_BASE_URL: API_BASE_URL,
    IS_DEV: false,
  },
};

// Determine environment
const getEnvironment = () => {
  return __DEV__ ? ENV.development : ENV.production;
};

export const config = getEnvironment();
export const API_URL = config.API_URL;
export { API_BASE_URL };

// Timeout settings
export const REQUEST_TIMEOUT = 30000; // 30 seconds

// Token storage keys (SecureStore only allows alphanumeric, dots, dashes, underscores)
export const TOKEN_KEY = 'pms_token';
export const REFRESH_TOKEN_KEY = 'pms_refresh_token';
export const USER_KEY = '@pms_user';

// Token refresh settings
export const TOKEN_REFRESH_THRESHOLD = 5 * 60 * 1000; // Refresh 5 minutes before expiry
