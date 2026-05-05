import React, { useState } from 'react';
import { View, StyleSheet, KeyboardAvoidingView, Platform } from 'react-native';
import { TextInput, Button, Text, HelperText } from 'react-native-paper';
import { useAuth } from '../../contexts/AuthContext';

export default function MFAScreen() {
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { mfaPending, completeMFALogin } = useAuth();

  const handleVerify = async () => {
    if (!mfaPending) return;
    if (!code.trim()) {
      setError('Please enter your verification code');
      return;
    }
    setLoading(true);
    setError('');
    try {
      await completeMFALogin(mfaPending.mfa_token, code.trim());
    } catch (err: any) {
      const errorMsg =
        err.response?.data?.error ||
        err.response?.data?.detail ||
        err.message ||
        'Invalid code. Please try again.';
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const methodLabel: Record<string, string> = {
    TOTP: 'authenticator app',
    EMAIL: 'email',
    SMS: 'SMS',
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <View style={styles.content}>
        <Text variant="headlineMedium" style={styles.title}>
          Two-Factor Authentication
        </Text>
        <Text variant="bodyMedium" style={styles.subtitle}>
          Enter the 6-digit code from your{' '}
          {methodLabel[mfaPending?.mfa_method ?? ''] ?? 'authenticator'}.
        </Text>

        <TextInput
          label="Verification Code"
          value={code}
          onChangeText={setCode}
          mode="outlined"
          keyboardType="number-pad"
          maxLength={10}
          style={styles.input}
          accessible
          accessibilityLabel="MFA verification code"
        />

        {error ? (
          <HelperText type="error" visible>
            {error}
          </HelperText>
        ) : null}

        <Button
          mode="contained"
          onPress={handleVerify}
          loading={loading}
          disabled={loading}
          style={styles.button}
        >
          Verify
        </Button>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  content: { flex: 1, justifyContent: 'center', paddingHorizontal: 24 },
  title: { marginBottom: 8, fontWeight: 'bold' },
  subtitle: { marginBottom: 24, color: '#666' },
  input: { marginBottom: 8 },
  button: { marginTop: 8 },
});
