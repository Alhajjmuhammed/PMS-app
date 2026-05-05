// Mock Expo modules
jest.mock('expo-secure-store', () => ({
  getItemAsync: jest.fn(),
  setItemAsync: jest.fn(),
  deleteItemAsync: jest.fn(),
}))

jest.mock('expo-constants', () => ({
  default: {
    expoConfig: {
      extra: {
        apiUrl: 'http://localhost:8000',
      },
    },
  },
}))

jest.mock('@react-native-async-storage/async-storage', () =>
  require('@react-native-async-storage/async-storage/jest/async-storage-mock')
)

// Mock React Native modules
jest.mock('react-native/Libraries/Animated/NativeAnimatedHelper')

// Silence the warning: Animated: `useNativeDriver` is not supported
jest.mock('react-native/Libraries/Animated/src/NativeAnimatedHelper')

// Mock Alert
jest.mock('react-native', () => {
  const RN = jest.requireActual('react-native')
  RN.Alert.alert = jest.fn()
  return RN
})

// Global test setup
global.__DEV__ = true
