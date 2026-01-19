// API Configuration
// Update these values based on your environment

const ENV = {
  dev: {
    apiUrl: 'http://192.168.100.114:8000/api/v1',
    // For Android emulator, use: http://10.0.2.2:8000/api/v1
    // For iOS simulator, use: http://localhost:8000/api/v1
    // For physical device, use your computer's IP: http://192.168.x.x:8000/api/v1
  },
  staging: {
    apiUrl: 'https://staging-api.yourhotel.com/api/v1',
  },
  prod: {
    apiUrl: 'https://api.yourhotel.com/api/v1',
  },
};

const getEnvVars = () => {
  // Change this to switch environments
  return ENV.dev;
};

export default getEnvVars;
