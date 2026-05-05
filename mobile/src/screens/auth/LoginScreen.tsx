import React, { useState } from 'react';
import { View, StyleSheet, Image, KeyboardAvoidingView, Platform } from 'react-native';
import { TextInput, Button, Text, HelperText } from 'react-native-paper';
import { useAuth } from '../../contexts/AuthContext';
import { validators, sanitizeInput } from '../../utils/validation';

export default function LoginScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();

  const handleLogin = async () => {
    // Validate email
    const emailValidation = validators.email(email);
    if (!emailValidation.isValid) {
      setError(emailValidation.error || 'Invalid email');
      return;
    }

    // Validate password
    const passwordValidation = validators.required(password, 'Password');
    if (!passwordValidation.isValid) {
      setError(passwordValidation.error || 'Password is required');
      return;
    }

    setLoading(true);
    setError('');

    try {
      console.log('Attempting login with:', email);
      // Sanitize email before sending
      const sanitizedEmail = sanitizeInput.toLowerCase(email);
      await login(sanitizedEmail, password);
      console.log('Login successful!');
    } catch (err: any) {
      console.error('Login error:', err);
      console.error('Error response:', err.response);
      const errorMsg = err.response?.data?.error 
        || err.response?.data?.detail 
        || err.message 
        || 'Login failed. Please check your credentials.';
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <View style={styles.content}>
        <View style={styles.header}>
          <Text variant="headlineLarge" style={styles.title}>
            Hotel PMS
          </Text>
          <Text variant="bodyLarge" style={styles.subtitle}>
            Staff Mobile App
          </Text>
        </View>

        <View style={styles.form}>
          <TextInput
            label="Email"
            value={email}
            onChangeText={setEmail}
            mode="outlined"
            keyboardType="email-address"
            autoCapitalize="none"
            style={styles.input}
            accessible={true}
            accessibilityLabel="Email address input field"
            accessibilityHint="Enter your email address to log in"
          />

          <TextInput
            label="Password"
            value={password}
            onChangeText={setPassword}
            mode="outlined"
            secureTextEntry
            style={styles.input}
            accessible={true}
            accessibilityLabel="Password input field"
            accessibilityHint="Enter your password to log in"
          />

          {error ? (
            <HelperText type="error" visible={true} accessible={true} accessibilityLabel="Login error message">
              {error}
            </HelperText>
          ) : null}

          <Button
            mode="contained"
            onPress={handleLogin}
            loading={loading}
            disabled={loading}
            style={styles.button}
            accessible={true}
            accessibilityLabel="Login button"
            accessibilityHint="Double tap to log in to the application"
            accessibilityRole="button"
          >
            Login
          </Button>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    padding: 24,
  },
  header: {
    alignItems: 'center',
    marginBottom: 48,
  },
  title: {
    color: '#1a73e8',
    fontWeight: 'bold',
  },
  subtitle: {
    color: '#5f6368',
    marginTop: 8,
  },
  form: {
    width: '100%',
  },
  input: {
    marginBottom: 16,
  },
  button: {
    marginTop: 8,
    paddingVertical: 8,
  },
});
