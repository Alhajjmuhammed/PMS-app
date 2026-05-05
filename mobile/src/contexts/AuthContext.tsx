import React, { createContext, useContext, useState, useEffect } from 'react';
import * as SecureStore from 'expo-secure-store';
import { authApi } from '../services/api';
import { TOKEN_KEY, REFRESH_TOKEN_KEY } from '../config/env';
import { authEvents } from '../utils/authEvents';

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  assigned_property?: { id: number; name: string } | null;
}

export interface MFAPending {
  mfa_token: string;
  mfa_method: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  mfaPending: MFAPending | null;
  login: (email: string, password: string) => Promise<void>;
  completeMFALogin: (mfa_token: string, mfa_code: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [mfaPending, setMfaPending] = useState<MFAPending | null>(null);

  useEffect(() => {
    loadStoredAuth();
    authEvents.onUnauthorized(() => {
      SecureStore.deleteItemAsync(TOKEN_KEY).catch(() => null);
      SecureStore.deleteItemAsync(REFRESH_TOKEN_KEY).catch(() => null);
      setToken(null);
      setUser(null);
      setMfaPending(null);
    });
  }, []);

  const loadStoredAuth = async () => {
    try {
      const storedToken = await SecureStore.getItemAsync(TOKEN_KEY);
      if (storedToken) {
        setToken(storedToken);
        const response = await authApi.getProfile();
        setUser(response.data);
      }
    } catch (error) {
      console.error('Error loading auth:', error);
      await SecureStore.deleteItemAsync(TOKEN_KEY);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    const response = await authApi.login(email, password);
    const data = response.data;

    // MFA required — store pending state and wait for code
    if (data.mfa_required) {
      setMfaPending({ mfa_token: data.mfa_token, mfa_method: data.mfa_method });
      return;
    }

    const accessToken = data.access || data.token;
    if (!accessToken) throw new Error('No access token received');

    await SecureStore.setItemAsync(TOKEN_KEY, accessToken);
    if (data.refresh) {
      await SecureStore.setItemAsync(REFRESH_TOKEN_KEY, data.refresh);
    }
    setToken(accessToken);
    setUser(data.user ?? null);
  };

  const completeMFALogin = async (mfa_token: string, mfa_code: string) => {
    const response = await authApi.verifyMFA(mfa_token, mfa_code);
    const data = response.data;

    const accessToken = data.access || data.token;
    if (!accessToken) throw new Error('No access token received');

    await SecureStore.setItemAsync(TOKEN_KEY, accessToken);
    if (data.refresh) {
      await SecureStore.setItemAsync(REFRESH_TOKEN_KEY, data.refresh);
    }
    setMfaPending(null);
    setToken(accessToken);
    setUser(data.user ?? null);
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      await SecureStore.deleteItemAsync(TOKEN_KEY);
      await SecureStore.deleteItemAsync(REFRESH_TOKEN_KEY);
      setToken(null);
      setUser(null);
      setMfaPending(null);
    }
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, mfaPending, login, completeMFALogin, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
