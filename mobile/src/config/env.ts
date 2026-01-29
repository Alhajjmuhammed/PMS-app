// Environment configuration
export const ENV = {
  development: {
    API_URL: 'http://192.168.0.136:8000/api/v1',
    API_BASE_URL: 'http://192.168.0.136:8000',
  },
  production: {
    API_URL: 'https://your-domain.com/api/v1',
    API_BASE_URL: 'https://your-domain.com',
  },
};

// Determine environment
const getEnvironment = () => {
  // In development mode, __DEV__ is true
  if (__DEV__) {
    return ENV.development;
  }
  return ENV.production;
};

export const config = getEnvironment();
export const API_URL = config.API_URL;
export const API_BASE_URL = config.API_BASE_URL;

// Timeout settings
export const REQUEST_TIMEOUT = 30000; // 30 seconds

// Token storage key (SecureStore only allows alphanumeric, dots, dashes, underscores)
export const TOKEN_KEY = 'pms_token';
export const USER_KEY = '@pms_user';
