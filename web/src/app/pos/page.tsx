'use client';

import { useEffect, useState } from 'react';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Button from '@/components/Button';
import api from '@/lib/api';

export default function POSPage() {
  const [items, setItems] = useState<any[]>([]);
  const [cart, setCart] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadItems();
  }, []);

  const loadItems = async () => {
    try {
      const response = await api.get('/api/v1/pos/items/');
      setItems(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to load items:', error);
    } finally {
      setLoading(false);
    }
  };

  const addToCart = (item: any) => {
    const existing = cart.find(c => c.id === item.id);
    if (existing) {
      setCart(cart.map(c => c.id === item.id ? { ...c, quantity: c.quantity + 1 } : c));
    } else {
      setCart([...cart, { ...item, quantity: 1 }]);
    }
  };

  const updateQuantity = (itemId: number, quantity: number) => {
    if (quantity === 0) {
      setCart(cart.filter(c => c.id !== itemId));
    } else {
      setCart(cart.map(c => c.id === itemId ? { ...c, quantity } : c));
    }
  };

  const getTotal = () => {
    return cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  };

  const handleCheckout = async () => {
    if (cart.length === 0) {
      alert('Cart is empty');
      return;
    }

    try {
      const orderData = {
        items: cart.map(item => ({
          item_id: item.id,
          quantity: item.quantity,
          price: item.price,
        })),
        total_amount: getTotal(),
      };

      await api.post('/api/v1/pos/orders/', orderData);
      alert('Order placed successfully!');
      setCart([]);
    } catch (error) {
      alert('Failed to place order');
    }
  };

  return (
    <Layout>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Items Grid */}
        <div className="lg:col-span-2 space-y-6">
          <h1 className="text-3xl font-bold text-gray-900">Point of Sale</h1>
          
          <Card padding="none">
            <div className="p-6 grid grid-cols-2 md:grid-cols-3 gap-4">
              {loading ? (
                <div className="col-span-full flex justify-center py-12">
                  <svg className="animate-spin h-8 w-8 text-primary-600" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                </div>
              ) : items.length === 0 ? (
                <p className="col-span-full text-center text-gray-500 py-12">No items available</p>
              ) : (
                items.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => addToCart(item)}
                    className="p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-left"
                  >
                    <div className="font-semibold text-gray-900">{item.name}</div>
                    <div className="text-2xl font-bold text-primary-600 mt-2">
                      ${item.price?.toFixed(2)}
                    </div>
                    {item.category && (
                      <div className="text-xs text-gray-500 mt-1 capitalize">{item.category}</div>
                    )}
                  </button>
                ))
              )}
            </div>
          </Card>
        </div>

        {/* Cart */}
        <div className="space-y-6">
          <h2 className="text-2xl font-bold text-gray-900">Cart</h2>
          
          <Card padding="none">
            <div className="p-4 space-y-3 max-h-96 overflow-y-auto">
              {cart.length === 0 ? (
                <p className="text-center text-gray-500 py-8">Cart is empty</p>
              ) : (
                cart.map((item) => (
                  <div key={item.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">{item.name}</div>
                      <div className="text-sm text-gray-500">${item.price?.toFixed(2)} each</div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => updateQuantity(item.id, item.quantity - 1)}
                        className="w-8 h-8 flex items-center justify-center bg-white border border-gray-300 rounded hover:bg-gray-100"
                      >
                        -
                      </button>
                      <span className="w-8 text-center font-semibold">{item.quantity}</span>
                      <button
                        onClick={() => updateQuantity(item.id, item.quantity + 1)}
                        className="w-8 h-8 flex items-center justify-center bg-white border border-gray-300 rounded hover:bg-gray-100"
                      >
                        +
                      </button>
                    </div>
                    <div className="ml-4 font-bold text-gray-900">
                      ${(item.price * item.quantity).toFixed(2)}
                    </div>
                  </div>
                ))
              )}
            </div>

            <div className="border-t p-4 space-y-4">
              <div className="flex justify-between text-lg font-bold">
                <span>Total:</span>
                <span className="text-primary-600">${getTotal().toFixed(2)}</span>
              </div>
              
              <Button onClick={handleCheckout} fullWidth disabled={cart.length === 0}>
                Checkout
              </Button>
              
              {cart.length > 0 && (
                <Button variant="secondary" onClick={() => setCart([])} fullWidth>
                  Clear Cart
                </Button>
              )}
            </div>
          </Card>
        </div>
      </div>
    </Layout>
  );
}
