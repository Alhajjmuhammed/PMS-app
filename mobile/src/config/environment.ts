// API Configuration
// IMPORTANT: Set EXPO_PUBLIC_API_URL in your .env file
// DO NOT commit hardcoded production URLs

const getApiUrl = (): string => {
  // Get from environment variable (set in .env or build config)
  const envApiUrl = process.env.EXPO_PUBLIC_API_URL;
  
  if (envApiUrl) {
    // Enforce HTTPS in production builds
    if (!__DEV__ && !envApiUrl.startsWith('https://')) {
      throw new Error('Production API URL must use HTTPS');
    }
    return envApiUrl;
  }
  
  // Development fallbacks (only allowed in dev mode)
  if (__DEV__) {
    // Default to localhost for dev
    // For Android emulator: use http://10.0.2.2:8000/api/v1
    // For iOS simulator: use http://localhost:8000/api/v1
    // For physical device: use your computer's IP (e.g., http://192.168.1.100:8000/api/v1)
    return 'http://localhost:8000/api/v1';
  }
  
  // Production build REQUIRES environment variable
  throw new Error(
    'API URL not configured. Set EXPO_PUBLIC_API_URL environment variable.'
  );
};

const ENV = {
  apiUrl: getApiUrl(),
  isDevelopment: __DEV__,
};

export default () => ENV;
