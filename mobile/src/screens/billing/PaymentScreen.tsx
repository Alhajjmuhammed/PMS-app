import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { Card, Text, Button, TextInput, RadioButton } from 'react-native-paper';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { billingApi } from '../../services/apiServices';
import { useNavigation, useRoute } from '@react-navigation/native';

export default function PaymentScreen() {
  const navigation = useNavigation();
  const route = useRoute<any>();
  const queryClient = useQueryClient();
  const { invoiceId } = route.params;

  const [paymentMethod, setPaymentMethod] = useState('CASH');
  const [amount, setAmount] = useState('');
  const [reference, setReference] = useState('');
  const [notes, setNotes] = useState('');

  const paymentMutation = useMutation({
    mutationFn: (data: any) => billingApi.recordPayment(invoiceId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invoice', invoiceId] });
      queryClient.invalidateQueries({ queryKey: ['invoices'] });
      Alert.alert('Success', 'Payment recorded successfully!', [
        { text: 'OK', onPress: () => navigation.goBack() },
      ]);
    },
    onError: (error: any) => {
      Alert.alert('Error', error.response?.data?.message || 'Failed to record payment');
    },
  });

  const handleSubmit = () => {
    if (!amount || parseFloat(amount) <= 0) {
      Alert.alert('Error', 'Please enter a valid payment amount');
      return;
    }

    paymentMutation.mutate({
      payment_method: paymentMethod,
      amount: parseFloat(amount),
      reference,
      notes,
    });
  };

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Text variant="titleLarge" style={styles.title}>
            Record Payment
          </Text>

          {/* Amount */}
          <View style={styles.section}>
            <Text variant="titleMedium" style={styles.sectionTitle}>
              Payment Amount
            </Text>
            <TextInput
              mode="outlined"
              label="Amount"
              placeholder="0.00"
              keyboardType="decimal-pad"
              value={amount}
              onChangeText={setAmount}
              left={<TextInput.Affix text="$" />}
              style={styles.input}
            />
          </View>

          {/* Payment Method */}
          <View style={styles.section}>
            <Text variant="titleMedium" style={styles.sectionTitle}>
              Payment Method
            </Text>
            <RadioButton.Group
              onValueChange={(value) => setPaymentMethod(value)}
              value={paymentMethod}
            >
              <View style={styles.radioItem}>
                <RadioButton value="CASH" />
                <Text>Cash</Text>
              </View>
              <View style={styles.radioItem}>
                <RadioButton value="CREDIT_CARD" />
                <Text>Credit Card</Text>
              </View>
              <View style={styles.radioItem}>
                <RadioButton value="DEBIT_CARD" />
                <Text>Debit Card</Text>
              </View>
              <View style={styles.radioItem}>
                <RadioButton value="BANK_TRANSFER" />
                <Text>Bank Transfer</Text>
              </View>
              <View style={styles.radioItem}>
                <RadioButton value="CHECK" />
                <Text>Check</Text>
              </View>
              <View style={styles.radioItem}>
                <RadioButton value="MOBILE_PAYMENT" />
                <Text>Mobile Payment</Text>
              </View>
            </RadioButton.Group>
          </View>

          {/* Reference */}
          <View style={styles.section}>
            <TextInput
              mode="outlined"
              label="Reference Number (Optional)"
              placeholder="Transaction ID, check number, etc."
              value={reference}
              onChangeText={setReference}
              style={styles.input}
            />
          </View>

          {/* Notes */}
          <View style={styles.section}>
            <TextInput
              mode="outlined"
              label="Notes (Optional)"
              placeholder="Additional notes..."
              multiline
              numberOfLines={3}
              value={notes}
              onChangeText={setNotes}
              style={styles.input}
            />
          </View>
        </Card.Content>
      </Card>

      {/* Actions */}
      <View style={styles.actions}>
        <Button
          mode="outlined"
          onPress={() => navigation.goBack()}
          style={styles.button}
        >
          Cancel
        </Button>
        <Button
          mode="contained"
          onPress={handleSubmit}
          loading={paymentMutation.isPending}
          disabled={!amount || parseFloat(amount) <= 0}
          icon="check"
          style={styles.button}
        >
          Record Payment
        </Button>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  card: {
    margin: 16,
  },
  title: {
    marginBottom: 24,
    fontWeight: '600',
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    marginBottom: 12,
    fontWeight: '600',
  },
  input: {
    backgroundColor: '#fff',
  },
  radioItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
  },
  actions: {
    flexDirection: 'row',
    padding: 16,
    gap: 8,
  },
  button: {
    flex: 1,
  },
});
