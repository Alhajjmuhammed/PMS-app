import api from './api';

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  is_superuser?: boolean;
  assigned_property?: {
    id: number;
    name: string;
  };
  mfa_enabled?: boolean;
  mfa_method?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user?: User;
  mfa_required?: boolean;
  mfa_method?: string;
}

export interface MFASetupResponse {
  method: string;
  secret?: string;
  qr_code?: string;
  backup_codes: string[];
  message?: string;
}

export const authService = {
  // Login
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response = await api.post<any>('/api/v1/auth/login/', credentials);
    const data = response.data;

    // Backend returns { token, user } for normal login or { mfa_required, mfa_token } for MFA
    if (!data.mfa_required && data.token) {
      api.setAccessToken(data.token);
    }

    // Normalise to the shape the rest of the app expects
    return {
      access: data.token ?? '',
      refresh: '',
      user: data.user,
      mfa_required: data.mfa_required,
      mfa_method: data.mfa_method,
    };
  },

  // Logout
  async logout(): Promise<void> {
    api.clearTokens();
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  },

  // Get current user
  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/api/v1/auth/me/');
    return response.data;
  },

  // MFA Setup
  async setupMFA(method: 'TOTP' | 'EMAIL' | 'SMS'): Promise<MFASetupResponse> {
    const response = await api.post<MFASetupResponse>('/api/v1/accounts/mfa/setup/', { method });
    return response.data;
  },

  // Enable MFA
  async enableMFA(code: string, method: string): Promise<{ message: string }> {
    const response = await api.post('/api/v1/accounts/mfa/enable/', { code, method });
    return response.data;
  },

  // Verify MFA Code
  async verifyMFA(code: string): Promise<{ message: string }> {
    const response = await api.post('/api/v1/accounts/mfa/verify/', { code });
    return response.data;
  },

  // Disable MFA
  async disableMFA(code: string): Promise<{ message: string }> {
    const response = await api.post('/api/v1/accounts/mfa/disable/', { code });
    return response.data;
  },

  // Get MFA Status
  async getMFAStatus(): Promise<{ mfa_enabled: boolean; mfa_method: string }> {
    const response = await api.get('/api/v1/accounts/mfa/status/');
    return response.data;
  },

  // Resend MFA Code
  async resendMFACode(): Promise<{ message: string }> {
    const response = await api.post('/api/v1/accounts/mfa/resend/');
    return response.data;
  },

  // Check if authenticated
  isAuthenticated(): boolean {
    return !!api.getAccessToken();
  },
};
