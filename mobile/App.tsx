import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { PaperProvider, MD3LightTheme } from 'react-native-paper';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { NavigationContainer } from '@react-navigation/native';
import RootNavigator from './src/navigation/RootNavigator';
import { AuthProvider } from './src/contexts/AuthContext';
import { ErrorBoundary } from './src/components';
import { NotificationProvider } from './src/components/NotificationProvider';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      retryDelay: 1000,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

const theme = {
  ...MD3LightTheme,
  colors: {
    ...MD3LightTheme.colors,
    primary: '#1a73e8',
    secondary: '#5f6368',
  },
};

export default function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <PaperProvider theme={theme}>
          <SafeAreaProvider>
            <AuthProvider>
              <NotificationProvider>
                <NavigationContainer>
                  <RootNavigator />
                  <StatusBar style="auto" />
                </NavigationContainer>
              </NotificationProvider>
            </AuthProvider>
          </SafeAreaProvider>
        </PaperProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}
