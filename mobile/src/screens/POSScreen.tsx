import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, FlatList } from 'react-native';
import { Text, Card, Button, Chip, Searchbar, FAB } from 'react-native-paper';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { posApi } from '../services/apiServices';
import { Loading, ErrorMessage } from '../components';

export default function POSScreen() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [cart, setCart] = useState<any[]>([]);
  const [selectedOutlet, setSelectedOutlet] = useState<number | null>(null);
  const queryClient = useQueryClient();

  const { data: outlets } = useQuery({
    queryKey: ['outlets'],
    queryFn: () => posApi.outlets.list(),
  });

  const { data: menu, isLoading, error, refetch } = useQuery({
    queryKey: ['menu', selectedOutlet],
    queryFn: () => selectedOutlet ? posApi.menu.get(selectedOutlet) : Promise.resolve(null),
    enabled: !!selectedOutlet,
  });

  const createOrder = useMutation({
    mutationFn: (data: any) => posApi.orders.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] });
      setCart([]);
    },
  });

  const addToCart = (product: any) => {
    const existing = cart.find(item => item.product.id === product.id);
    if (existing) {
      setCart(cart.map(item =>
        item.product.id === product.id
          ? { ...item, quantity: item.quantity + 1 }
          : item
      ));
    } else {
      setCart([...cart, { product, quantity: 1, unit_price: product.price }]);
    }
  };

  const removeFromCart = (productId: number) => {
    setCart(cart.filter(item => item.product.id !== productId));
  };

  const updateQuantity = (productId: number, quantity: number) => {
    if (quantity <= 0) {
      removeFromCart(productId);
    } else {
      setCart(cart.map(item =>
        item.product.id === productId ? { ...item, quantity } : item
      ));
    }
  };

  const calculateTotal = () => {
    return cart.reduce((sum, item) => sum + (parseFloat(item.unit_price) * item.quantity), 0);
  };

  const handleCheckout = () => {
    const orderData = {
      outlet: selectedOutlet,
      items: cart.map(item => ({
        menu_item: item.product.id,
        quantity: item.quantity,
        unit_price: item.unit_price,
      })),
    };
    createOrder.mutate(orderData);
  };

  const menuItems = menu?.data?.items || [];
  const categories = menu?.data?.categories || [];

  const filteredProducts = menuItems.filter((p: any) => {
    const matchesSearch = p.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = !selectedCategory || p.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  if (!selectedOutlet) {
    return (
      <View style={styles.container}>
        <Text variant="headlineSmall" style={styles.title}>Select an Outlet</Text>
        <ScrollView>
          {outlets?.data?.map((outlet: any) => (
            <Card key={outlet.id} style={styles.outletCard} onPress={() => setSelectedOutlet(outlet.id)}>
              <Card.Title title={outlet.name} subtitle={outlet.location} />
            </Card>
          ))}
        </ScrollView>
      </View>
    );
  }

  if (isLoading) return <Loading message="Loading menu..." />;
  if (error) return <ErrorMessage message="Failed to load menu" onRetry={refetch} />;

  return (
    <View style={styles.container}>
      <View style={styles.leftPanel}>
        <Searchbar
          placeholder="Search products..."
          onChangeText={setSearchQuery}
          value={searchQuery}
          style={styles.searchbar}
        />

        {/* Categories */}
        <ScrollView horizontal style={styles.categories}>
          <Chip
            selected={!selectedCategory}
            onPress={() => setSelectedCategory(null)}
            style={styles.categoryChip}
          >
            All
          </Chip>
          {categories.map((cat: any) => (
            <Chip
              key={cat.id}
              selected={selectedCategory === cat.id}
              onPress={() => setSelectedCategory(cat.id)}
              style={styles.categoryChip}
            >
              {cat.name}
            </Chip>
          ))}
        </ScrollView>

        {/* Products Grid */}
        <FlatList
          data={filteredProducts}
          numColumns={2}
          keyExtractor={(item) => item.id.toString()}
          renderItem={({ item }) => (
            <Card style={styles.productCard} onPress={() => addToCart(item)}>
              <Card.Content>
                <Text variant="titleMedium" numberOfLines={2}>{item.name}</Text>
                <Text variant="bodySmall" style={styles.productCode}>{item.code}</Text>
                <Text variant="titleLarge" style={styles.price}>${item.price}</Text>
                <Text variant="bodySmall">Stock: {item.stock_quantity}</Text>
              </Card.Content>
            </Card>
          )}
          contentContainerStyle={styles.productGrid}
        />
      </View>

      {/* Cart Panel */}
      <View style={styles.rightPanel}>
        <Card style={styles.cartCard}>
          <Card.Title title="Current Order" subtitle={`${cart.length} items`} />
          <Card.Content>
            <ScrollView style={styles.cartItems}>
              {cart.map((item) => (
                <View key={item.product.id} style={styles.cartItem}>
                  <View style={styles.cartItemInfo}>
                    <Text variant="bodyMedium">{item.product.name}</Text>
                    <Text variant="bodySmall">${item.unit_price} × {item.quantity}</Text>
                  </View>
                  <View style={styles.cartItemActions}>
                    <Button onPress={() => updateQuantity(item.product.id, item.quantity - 1)}>
                      -
                    </Button>
                    <Text>{item.quantity}</Text>
                    <Button onPress={() => updateQuantity(item.product.id, item.quantity + 1)}>
                      +
                    </Button>
                  </View>
                  <Text variant="titleMedium" style={styles.itemTotal}>
                    ${(parseFloat(item.unit_price) * item.quantity).toFixed(2)}
                  </Text>
                </View>
              ))}
            </ScrollView>

            <View style={styles.total}>
              <Text variant="headlineSmall">Total:</Text>
              <Text variant="headlineMedium" style={styles.totalAmount}>
                ${calculateTotal().toFixed(2)}
              </Text>
            </View>
          </Card.Content>
          <Card.Actions>
            <Button onPress={() => setCart([])} disabled={cart.length === 0}>
              Clear
            </Button>
            <Button
              mode="contained"
              onPress={handleCheckout}
              disabled={cart.length === 0}
              loading={createOrder.isPending}
            >
              Checkout
            </Button>
          </Card.Actions>
        </Card>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    flexDirection: 'row',
    backgroundColor: '#f5f5f5',
    padding: 16,
  },
  title: {
    marginBottom: 16,
  },
  outletCard: {
    marginBottom: 12,
  },
  leftPanel: {
    flex: 2,
    padding: 16,
  },
  rightPanel: {
    flex: 1,
    padding: 16,
    borderLeftWidth: 1,
    borderLeftColor: '#e0e0e0',
  },
  searchbar: {
    marginBottom: 12,
  },
  categories: {
    marginBottom: 12,
    maxHeight: 50,
  },
  categoryChip: {
    marginRight: 8,
  },
  productGrid: {
    paddingBottom: 16,
  },
  productCard: {
    flex: 1,
    margin: 8,
    maxWidth: '48%',
  },
  productCode: {
    color: '#666',
    marginTop: 4,
  },
  price: {
    color: '#2196f3',
    fontWeight: 'bold',
    marginTop: 8,
  },
  cartCard: {
    flex: 1,
  },
  cartItems: {
    maxHeight: 400,
  },
  cartItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  cartItemInfo: {
    flex: 1,
  },
  cartItemActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  itemTotal: {
    marginLeft: 12,
    minWidth: 80,
    textAlign: 'right',
  },
  total: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 20,
    paddingTop: 20,
    borderTopWidth: 2,
    borderTopColor: '#2196f3',
  },
  totalAmount: {
    color: '#2196f3',
    fontWeight: 'bold',
  },
});
