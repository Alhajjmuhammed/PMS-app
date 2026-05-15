'use client';

import { useEffect, useState, useCallback } from 'react';
import Layout from '@/components/Layout';
import api from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import {
  ShoppingCartIcon,
  ReceiptRefundIcon,
  CurrencyDollarIcon,
  UserGroupIcon,
  XMarkIcon,
  PlusIcon,
  MinusIcon,
  CheckCircleIcon,
  HomeModernIcon,
  ClockIcon,
  HomeIcon,
  ChevronRightIcon,
} from '@heroicons/react/24/outline';

interface Outlet { id: number; name: string; outlet_type: string; }
interface Category { id: number; name: string; outlet: number; }
interface MenuItem { id: number; name: string; price: string; description: string; is_available: boolean; category: number; category_name: string; }
interface CartItem extends MenuItem { quantity: number; }
interface Order {
  id: number; order_number: string; outlet_name: string; status: string;
  total: string; subtotal: string; tax_amount: string; discount: string;
  table_number: string; guest_name: string; room_number: string;
  covers: number; is_posted_to_room: boolean; created_at: string;
  items: { id: number; menu_item_name: string; quantity: number; unit_price: string; amount: string; }[];
}
interface DashboardStats {
  open_orders: number; orders_today: number; revenue_today: string;
  covers_today: number; avg_check_size: string; top_selling_items: { name: string; quantity: number; amount: number; }[];
}

type Tab = 'order' | 'orders' | 'dashboard';

function Toast({ message, type, onClose }: { message: string; type: 'success' | 'error'; onClose: () => void }) {
  useEffect(() => { const t = setTimeout(onClose, 3500); return () => clearTimeout(t); }, [onClose]);
  return (
    <div className={`fixed bottom-4 right-4 z-50 flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg text-white text-sm font-medium transition-all ${type === 'success' ? 'bg-emerald-600' : 'bg-red-600'}`}>
      {type === 'success' ? <CheckCircleIcon className="h-5 w-5" /> : <XMarkIcon className="h-5 w-5" />}
      {message}
      <button onClick={onClose}><XMarkIcon className="h-4 w-4 opacity-70 hover:opacity-100" /></button>
    </div>
  );
}

export default function POSPage() {
  const { user } = useAuth();
  const canManage = user?.role === 'ADMIN' || user?.role === 'MANAGER';

  const [activeTab, setActiveTab] = useState<Tab>('order');
  const [outlets, setOutlets] = useState<Outlet[]>([]);
  const [selectedOutlet, setSelectedOutlet] = useState<number | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [openOrders, setOpenOrders] = useState<Order[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);

  // Order form
  const [tableNumber, setTableNumber] = useState('');
  const [guestName, setGuestName] = useState('');
  const [roomNumber, setRoomNumber] = useState('');
  const [covers, setCovers] = useState(1);
  const [notes, setNotes] = useState('');

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [postingRoom, setPostingRoom] = useState<number | null>(null);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  const showToast = (message: string, type: 'success' | 'error' = 'success') => setToast({ message, type });

  const loadOutlets = useCallback(async () => {
    try {
      const r = await api.get('/api/v1/pos/outlets/');
      const list: Outlet[] = r.data.results || r.data;
      setOutlets(list);
      if (list.length > 0 && !selectedOutlet) setSelectedOutlet(list[0].id);
    } catch { showToast('Failed to load outlets', 'error'); }
  }, []);

  const loadCategories = useCallback(async (outletId: number) => {
    try {
      const r = await api.get(`/api/v1/pos/categories/?outlet=${outletId}`);
      const list: Category[] = r.data.results || r.data;
      setCategories(list);
      setSelectedCategory(list.length > 0 ? list[0].id : null);
    } catch { setCategories([]); }
  }, []);

  const loadMenuItems = useCallback(async (outletId: number, categoryId?: number | null) => {
    try {
      const params = new URLSearchParams({ outlet: String(outletId) });
      if (categoryId) params.set('category', String(categoryId));
      const r = await api.get(`/api/v1/pos/menu-items/available/?${params}`);
      setMenuItems(r.data.results || r.data);
    } catch { setMenuItems([]); }
  }, []);

  const loadOpenOrders = useCallback(async () => {
    try {
      const r = await api.get('/api/v1/pos/orders/open/');
      setOpenOrders(r.data.results || r.data);
    } catch { setOpenOrders([]); }
  }, []);

  const loadStats = useCallback(async () => {
    try {
      const r = await api.get('/api/v1/pos/dashboard/');
      setStats(r.data);
    } catch { setStats(null); }
  }, []);

  // Initial load
  useEffect(() => {
    (async () => {
      setLoading(true);
      await loadOutlets();
      await loadOpenOrders();
      await loadStats();
      setLoading(false);
    })();
  }, [loadOutlets, loadOpenOrders, loadStats]);

  // When outlet changes → reload categories + items
  useEffect(() => {
    if (selectedOutlet) {
      loadCategories(selectedOutlet);
    }
  }, [selectedOutlet, loadCategories]);

  // When category changes → reload items
  useEffect(() => {
    if (selectedOutlet) {
      loadMenuItems(selectedOutlet, selectedCategory);
    }
  }, [selectedOutlet, selectedCategory, loadMenuItems]);

  const addToCart = (item: MenuItem) => {
    setCart(prev => {
      const existing = prev.find(c => c.id === item.id);
      if (existing) return prev.map(c => c.id === item.id ? { ...c, quantity: c.quantity + 1 } : c);
      return [...prev, { ...item, quantity: 1 }];
    });
  };

  const updateQty = (itemId: number, qty: number) => {
    if (qty <= 0) setCart(prev => prev.filter(c => c.id !== itemId));
    else setCart(prev => prev.map(c => c.id === itemId ? { ...c, quantity: qty } : c));
  };

  const getSubtotal = () => cart.reduce((s, i) => s + parseFloat(i.price) * i.quantity, 0);

  const handlePlaceOrder = async () => {
    if (!selectedOutlet) { showToast('Please select an outlet', 'error'); return; }
    if (cart.length === 0) { showToast('Cart is empty', 'error'); return; }
    setSubmitting(true);
    try {
      await api.post('/api/v1/pos/orders/', {
        outlet: selectedOutlet,
        table_number: tableNumber,
        guest_name: guestName,
        room_number: roomNumber,
        covers,
        notes,
        items: cart.map(i => ({ menu_item: i.id, quantity: i.quantity })),
      });
      showToast(`Order placed successfully!`);
      setCart([]);
      setTableNumber(''); setGuestName(''); setRoomNumber(''); setNotes(''); setCovers(1);
      await loadOpenOrders();
      await loadStats();
    } catch (e: any) {
      showToast(e?.response?.data?.error || 'Failed to place order', 'error');
    } finally { setSubmitting(false); }
  };

  const handleCloseOrder = async (orderId: number) => {
    try {
      await api.post(`/api/v1/pos/orders/${orderId}/close/`);
      showToast('Order closed');
      setSelectedOrder(null);
      await loadOpenOrders();
      await loadStats();
    } catch (e: any) { showToast(e?.response?.data?.error || 'Failed to close order', 'error'); }
  };

  const handlePostToRoom = async (orderId: number) => {
    setPostingRoom(orderId);
    try {
      await api.post(`/api/v1/pos/orders/${orderId}/post-to-room/`);
      showToast('Posted to room folio');
      setSelectedOrder(null);
      await loadOpenOrders();
      await loadStats();
    } catch (e: any) { showToast(e?.response?.data?.error || 'Failed to post to room', 'error'); }
    finally { setPostingRoom(null); }
  };

  const tabs: { key: Tab; label: string; icon: any }[] = [
    { key: 'order', label: 'New Order', icon: ShoppingCartIcon },
    { key: 'orders', label: `Open Orders${openOrders.length > 0 ? ` (${openOrders.length})` : ''}`, icon: ClockIcon },
    { key: 'dashboard', label: 'Dashboard', icon: CurrencyDollarIcon },
  ];

  return (
    <Layout>
      <div className="p-5 lg:p-6 space-y-5">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-1.5 text-sm text-slate-400">
          <HomeIcon className="w-4 h-4" />
          <span>Home</span>
          <ChevronRightIcon className="w-3.5 h-3.5" />
          <span className="text-slate-700 font-medium">Point of Sale</span>
        </nav>

        {/* Header */}
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-100 flex items-center justify-center flex-shrink-0">
              <ShoppingCartIcon className="w-5 h-5 text-indigo-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Point of Sale</h1>
              <p className="text-slate-500 text-sm mt-0.5">Manage orders and menu items</p>
            </div>
          </div>
          {/* Outlet selector */}
          {outlets.length > 1 && (
            <select
              value={selectedOutlet ?? ''}
              onChange={e => setSelectedOutlet(Number(e.target.value))}
              className="border border-slate-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 bg-white text-slate-700"
            >
              {outlets.map(o => <option key={o.id} value={o.id}>{o.name}</option>)}
            </select>
          )}
          {outlets.length === 1 && (
            <span className="text-sm font-semibold text-indigo-700 bg-indigo-50 px-3 py-1.5 rounded-xl">{outlets[0]?.name}</span>
          )}
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex gap-6">
            {tabs.map(({ key, label, icon: Icon }) => (
              <button
                key={key}
                onClick={() => setActiveTab(key)}
                className={`flex items-center gap-2 py-3 px-1 border-b-2 text-sm font-medium transition-colors ${
                  activeTab === key
                    ? 'border-indigo-600 text-indigo-600'
                    : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
                }`}
              >
                <Icon className="h-4 w-4" />
                {label}
              </button>
            ))}
          </nav>
        </div>

        {/* === NEW ORDER TAB === */}
        {activeTab === 'order' && (
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
            {/* Left: Menu */}
            <div className="xl:col-span-2 space-y-4">
              {/* Category tabs */}
              {categories.length > 0 && (
                <div className="flex gap-2 flex-wrap">
                  <button
                    onClick={() => setSelectedCategory(null)}
                    className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${selectedCategory === null ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
                  >
                    All
                  </button>
                  {categories.map(cat => (
                    <button
                      key={cat.id}
                      onClick={() => setSelectedCategory(cat.id)}
                      className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${selectedCategory === cat.id ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
                    >
                      {cat.name}
                    </button>
                  ))}
                </div>
              )}

              {/* Menu items grid */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {loading ? (
                  Array.from({ length: 6 }).map((_, i) => (
                    <div key={i} className="h-28 bg-gray-100 rounded-xl animate-pulse" />
                  ))
                ) : menuItems.length === 0 ? (
                  <div className="col-span-full text-center py-16 text-gray-400">
                    <ShoppingCartIcon className="h-12 w-12 mx-auto mb-3 opacity-30" />
                    <p>No items available</p>
                    {!selectedOutlet && <p className="text-xs mt-1">Select an outlet to see the menu</p>}
                  </div>
                ) : (
                  menuItems.map(item => (
                    <button
                      key={item.id}
                      onClick={() => addToCart(item)}
                      className="p-4 bg-white border-2 border-gray-100 rounded-xl hover:border-indigo-400 hover:shadow-md transition-all text-left group"
                    >
                      <div className="font-semibold text-gray-900 text-sm leading-tight group-hover:text-indigo-700">{item.name}</div>
                      {item.description && <div className="text-xs text-gray-400 mt-1 line-clamp-1">{item.description}</div>}
                      <div className="text-lg font-bold text-indigo-600 mt-2">${parseFloat(item.price).toFixed(2)}</div>
                    </button>
                  ))
                )}
              </div>
            </div>

            {/* Right: Cart + Order Details */}
            <div className="space-y-4">
              {/* Order details */}
              <div className="bg-white border border-gray-200 rounded-xl p-4 space-y-3">
                <h3 className="font-semibold text-gray-800 text-sm">Order Details</h3>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs text-gray-500">Table #</label>
                    <input value={tableNumber} onChange={e => setTableNumber(e.target.value)}
                      placeholder="e.g. T1" className="mt-1 w-full border border-gray-200 rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" />
                  </div>
                  <div>
                    <label className="text-xs text-gray-500">Covers</label>
                    <input type="number" min={1} value={covers} onChange={e => setCovers(Number(e.target.value))}
                      className="mt-1 w-full border border-gray-200 rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" />
                  </div>
                  <div>
                    <label className="text-xs text-gray-500">Guest Name</label>
                    <input value={guestName} onChange={e => setGuestName(e.target.value)}
                      placeholder="Optional" className="mt-1 w-full border border-gray-200 rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" />
                  </div>
                  <div>
                    <label className="text-xs text-gray-500">Room #</label>
                    <input value={roomNumber} onChange={e => setRoomNumber(e.target.value)}
                      placeholder="For room charge" className="mt-1 w-full border border-gray-200 rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" />
                  </div>
                </div>
                <div>
                  <label className="text-xs text-gray-500">Notes</label>
                  <input value={notes} onChange={e => setNotes(e.target.value)}
                    placeholder="Special instructions..." className="mt-1 w-full border border-gray-200 rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" />
                </div>
              </div>

              {/* Cart */}
              <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
                <div className="px-4 py-3 bg-gray-50 border-b border-gray-100 flex items-center justify-between">
                  <h3 className="font-semibold text-gray-800 text-sm flex items-center gap-2">
                    <ShoppingCartIcon className="h-4 w-4" />
                    Cart {cart.length > 0 && <span className="bg-indigo-600 text-white text-xs rounded-full px-1.5">{cart.reduce((s, i) => s + i.quantity, 0)}</span>}
                  </h3>
                  {cart.length > 0 && (
                    <button onClick={() => setCart([])} className="text-xs text-red-500 hover:text-red-700">Clear</button>
                  )}
                </div>

                <div className="divide-y divide-gray-50 max-h-64 overflow-y-auto">
                  {cart.length === 0 ? (
                    <p className="text-center text-gray-400 py-8 text-sm">Add items from the menu</p>
                  ) : cart.map(item => (
                    <div key={item.id} className="flex items-center gap-3 px-4 py-3">
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium text-gray-900 truncate">{item.name}</div>
                        <div className="text-xs text-gray-400">${parseFloat(item.price).toFixed(2)} each</div>
                      </div>
                      <div className="flex items-center gap-1">
                        <button onClick={() => updateQty(item.id, item.quantity - 1)}
                          className="w-6 h-6 flex items-center justify-center rounded-full bg-gray-100 hover:bg-red-100 hover:text-red-600 transition-colors">
                          <MinusIcon className="h-3 w-3" />
                        </button>
                        <span className="w-6 text-center text-sm font-semibold">{item.quantity}</span>
                        <button onClick={() => updateQty(item.id, item.quantity + 1)}
                          className="w-6 h-6 flex items-center justify-center rounded-full bg-gray-100 hover:bg-indigo-100 hover:text-indigo-600 transition-colors">
                          <PlusIcon className="h-3 w-3" />
                        </button>
                      </div>
                      <div className="text-sm font-bold text-gray-900 w-16 text-right">
                        ${(parseFloat(item.price) * item.quantity).toFixed(2)}
                      </div>
                    </div>
                  ))}
                </div>

                {cart.length > 0 && (
                  <div className="border-t border-gray-100 p-4 space-y-3">
                    <div className="flex justify-between text-sm text-gray-600">
                      <span>Subtotal</span>
                      <span>${getSubtotal().toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between font-bold text-gray-900">
                      <span>Est. Total</span>
                      <span className="text-indigo-600">${getSubtotal().toFixed(2)}</span>
                    </div>
                    <button
                      onClick={handlePlaceOrder}
                      disabled={submitting || !selectedOutlet}
                      className="w-full bg-indigo-600 text-white py-2.5 rounded-xl font-semibold text-sm hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {submitting ? 'Placing Order…' : 'Place Order'}
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* === OPEN ORDERS TAB === */}
        {activeTab === 'orders' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {openOrders.length === 0 ? (
              <div className="lg:col-span-2 text-center py-20 text-gray-400">
                <ClockIcon className="h-12 w-12 mx-auto mb-3 opacity-30" />
                <p className="font-medium">No open orders</p>
              </div>
            ) : openOrders.map(order => (
              <div
                key={order.id}
                onClick={() => setSelectedOrder(selectedOrder?.id === order.id ? null : order)}
                className={`bg-white border-2 rounded-xl p-4 cursor-pointer transition-all ${selectedOrder?.id === order.id ? 'border-indigo-500 shadow-md' : 'border-gray-100 hover:border-gray-300'}`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="font-bold text-gray-900">{order.order_number}</div>
                    <div className="text-sm text-gray-500">{order.outlet_name}</div>
                    {order.table_number && <div className="text-xs text-gray-400 mt-0.5">Table {order.table_number} · {order.covers} covers</div>}
                    {order.guest_name && <div className="text-xs text-gray-400">{order.guest_name}</div>}
                    {order.room_number && <div className="text-xs text-indigo-600">Room {order.room_number}</div>}
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-indigo-600">${parseFloat(order.total).toFixed(2)}</div>
                    <div className="text-xs text-gray-400">{order.items?.length ?? 0} items</div>
                  </div>
                </div>

                {/* Expanded actions */}
                {selectedOrder?.id === order.id && (
                  <div className="mt-4 pt-4 border-t border-gray-100 space-y-3">
                    {/* Items list */}
                    <div className="space-y-1">
                      {order.items?.map(item => (
                        <div key={item.id} className="flex justify-between text-sm">
                          <span className="text-gray-700">{item.quantity}× {item.menu_item_name}</span>
                          <span className="text-gray-500">${parseFloat(item.amount).toFixed(2)}</span>
                        </div>
                      ))}
                    </div>
                    <div className="flex items-center justify-between text-xs text-gray-400 pt-1 border-t border-gray-50">
                      <span>Tax: ${parseFloat(order.tax_amount).toFixed(2)}</span>
                      <span>Total: ${parseFloat(order.total).toFixed(2)}</span>
                    </div>
                    <div className="flex gap-2 pt-1">
                      {order.room_number && !order.is_posted_to_room && (
                        <button
                          onClick={e => { e.stopPropagation(); handlePostToRoom(order.id); }}
                          disabled={postingRoom === order.id}
                          className="flex-1 flex items-center justify-center gap-1.5 bg-emerald-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-emerald-700 transition-colors disabled:opacity-50"
                        >
                          <HomeModernIcon className="h-4 w-4" />
                          {postingRoom === order.id ? 'Posting…' : 'Post to Room'}
                        </button>
                      )}
                      <button
                        onClick={e => { e.stopPropagation(); handleCloseOrder(order.id); }}
                        className="flex-1 flex items-center justify-center gap-1.5 bg-gray-700 text-white py-2 rounded-lg text-sm font-medium hover:bg-gray-900 transition-colors"
                      >
                        <CheckCircleIcon className="h-4 w-4" />
                        Close Order
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* === DASHBOARD TAB === */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            {stats ? (
              <>
                {/* Stat cards */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  {[
                    { label: 'Open Orders', value: stats.open_orders, icon: ClockIcon, color: 'bg-amber-50 text-amber-600' },
                    { label: 'Orders Today', value: stats.orders_today, icon: ReceiptRefundIcon, color: 'bg-blue-50 text-blue-600' },
                    { label: "Today's Revenue", value: `$${parseFloat(stats.revenue_today).toFixed(2)}`, icon: CurrencyDollarIcon, color: 'bg-emerald-50 text-emerald-600' },
                    { label: 'Covers Today', value: stats.covers_today, icon: UserGroupIcon, color: 'bg-purple-50 text-purple-600' },
                  ].map(({ label, value, icon: Icon, color }) => (
                    <div key={label} className="bg-white border border-gray-100 rounded-xl p-4 flex items-center gap-4">
                      <div className={`p-2.5 rounded-xl ${color}`}><Icon className="h-5 w-5" /></div>
                      <div>
                        <div className="text-2xl font-bold text-gray-900">{value}</div>
                        <div className="text-xs text-gray-500">{label}</div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Avg check */}
                  <div className="bg-white border border-gray-100 rounded-xl p-5">
                    <h3 className="font-semibold text-gray-800 mb-3">Avg Check Size</h3>
                    <div className="text-4xl font-bold text-indigo-600">${parseFloat(stats.avg_check_size).toFixed(2)}</div>
                    <div className="text-sm text-gray-400 mt-1">per order today</div>
                  </div>

                  {/* Top items */}
                  <div className="bg-white border border-gray-100 rounded-xl p-5">
                    <h3 className="font-semibold text-gray-800 mb-3">Top Selling Today</h3>
                    {stats.top_selling_items.length === 0 ? (
                      <p className="text-sm text-gray-400">No sales yet today</p>
                    ) : (
                      <div className="space-y-2">
                        {stats.top_selling_items.map((item, i) => (
                          <div key={item.name} className="flex items-center justify-between text-sm">
                            <div className="flex items-center gap-2">
                              <span className="text-xs font-bold text-gray-400 w-4">#{i + 1}</span>
                              <span className="text-gray-700 font-medium">{item.name}</span>
                            </div>
                            <div className="flex items-center gap-3">
                              <span className="text-gray-500">{item.quantity} sold</span>
                              <span className="font-semibold text-emerald-600">${item.amount.toFixed(2)}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </>
            ) : (
              <div className="text-center py-20 text-gray-400">
                <CurrencyDollarIcon className="h-12 w-12 mx-auto mb-3 opacity-30" />
                <p>Could not load dashboard stats</p>
              </div>
            )}
          </div>
        )}
      </div>

      {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}
    </Layout>
  );
}
