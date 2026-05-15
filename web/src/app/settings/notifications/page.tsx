'use client';

import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Button from '@/components/Button';
import { useAuth } from '@/contexts/AuthContext';

const STORAGE_KEY = 'pms_notification_settings';

const defaultSettings = {
  email_reservations: true,
  email_checkins: true,
  email_checkouts: false,
  email_maintenance: true,
  email_reports: true,
  push_reservations: true,
  push_checkins: true,
  push_checkouts: false,
  push_maintenance: true,
  push_housekeeping: false,
  sms_enabled: false,
  sms_critical_only: true,
};

export default function NotificationsSettingsPage() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [settings, setSettings] = useState(defaultSettings);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const key = `${STORAGE_KEY}_${user?.id ?? 'anon'}`;
    const saved = localStorage.getItem(key);
    if (saved) {
      try { setSettings({ ...defaultSettings, ...JSON.parse(saved) }); } catch {}
    }
  }, [user?.id]);

  const handleSave = async () => {
    setLoading(true);
    try {
      const key = `${STORAGE_KEY}_${user?.id ?? 'anon'}`;
      localStorage.setItem(key, JSON.stringify(settings));
      setSaved(true);
      setTimeout(() => setSaved(false), 3500);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="max-w-4xl mx-auto space-y-6">
        {saved && (
          <div className="px-4 py-3 rounded-lg bg-green-50 text-green-800 border border-green-200 text-sm font-medium">Notification settings updated successfully!</div>
        )}
        <h1 className="text-3xl font-bold text-gray-900">Notification Settings</h1>

        <Card title="Email Notifications">
          <div className="space-y-3">
            <label className="flex items-center justify-between">
              <div>
                <span className="font-medium">New Reservations</span>
                <p className="text-sm text-gray-500">Receive emails when new reservations are created</p>
              </div>
              <input
                type="checkbox"
                checked={settings.email_reservations}
                onChange={(e) => setSettings({ ...settings, email_reservations: e.target.checked })}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500 h-5 w-5"
              />
            </label>

            <label className="flex items-center justify-between">
              <div>
                <span className="font-medium">Check-ins</span>
                <p className="text-sm text-gray-500">Notifications for guest check-ins</p>
              </div>
              <input
                type="checkbox"
                checked={settings.email_checkins}
                onChange={(e) => setSettings({ ...settings, email_checkins: e.target.checked })}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500 h-5 w-5"
              />
            </label>

            <label className="flex items-center justify-between">
              <div>
                <span className="font-medium">Check-outs</span>
                <p className="text-sm text-gray-500">Notifications for guest check-outs</p>
              </div>
              <input
                type="checkbox"
                checked={settings.email_checkouts}
                onChange={(e) => setSettings({ ...settings, email_checkouts: e.target.checked })}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500 h-5 w-5"
              />
            </label>

            <label className="flex items-center justify-between">
              <div>
                <span className="font-medium">Maintenance Requests</span>
                <p className="text-sm text-gray-500">Alerts for new maintenance requests</p>
              </div>
              <input
                type="checkbox"
                checked={settings.email_maintenance}
                onChange={(e) => setSettings({ ...settings, email_maintenance: e.target.checked })}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500 h-5 w-5"
              />
            </label>

            <label className="flex items-center justify-between">
              <div>
                <span className="font-medium">Daily Reports</span>
                <p className="text-sm text-gray-500">Receive daily summary reports</p>
              </div>
              <input
                type="checkbox"
                checked={settings.email_reports}
                onChange={(e) => setSettings({ ...settings, email_reports: e.target.checked })}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500 h-5 w-5"
              />
            </label>
          </div>
        </Card>

        <Card title="Push Notifications">
          <div className="space-y-3">
            <label className="flex items-center justify-between">
              <div>
                <span className="font-medium">New Reservations</span>
                <p className="text-sm text-gray-500">Push notifications for new bookings</p>
              </div>
              <input
                type="checkbox"
                checked={settings.push_reservations}
                onChange={(e) => setSettings({ ...settings, push_reservations: e.target.checked })}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500 h-5 w-5"
              />
            </label>

            <label className="flex items-center justify-between">
              <div>
                <span className="font-medium">Check-ins</span>
                <p className="text-sm text-gray-500">Real-time check-in notifications</p>
              </div>
              <input
                type="checkbox"
                checked={settings.push_checkins}
                onChange={(e) => setSettings({ ...settings, push_checkins: e.target.checked })}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500 h-5 w-5"
              />
            </label>

            <label className="flex items-center justify-between">
              <div>
                <span className="font-medium">Check-outs</span>
                <p className="text-sm text-gray-500">Real-time check-out notifications</p>
              </div>
              <input
                type="checkbox"
                checked={settings.push_checkouts}
                onChange={(e) => setSettings({ ...settings, push_checkouts: e.target.checked })}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500 h-5 w-5"
              />
            </label>

            <label className="flex items-center justify-between">
              <div>
                <span className="font-medium">Maintenance</span>
                <p className="text-sm text-gray-500">Urgent maintenance alerts</p>
              </div>
              <input
                type="checkbox"
                checked={settings.push_maintenance}
                onChange={(e) => setSettings({ ...settings, push_maintenance: e.target.checked })}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500 h-5 w-5"
              />
            </label>

            <label className="flex items-center justify-between">
              <div>
                <span className="font-medium">Housekeeping</span>
                <p className="text-sm text-gray-500">Housekeeping task updates</p>
              </div>
              <input
                type="checkbox"
                checked={settings.push_housekeeping}
                onChange={(e) => setSettings({ ...settings, push_housekeeping: e.target.checked })}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500 h-5 w-5"
              />
            </label>
          </div>
        </Card>

        <Card title="SMS Notifications">
          <div className="space-y-3">
            <label className="flex items-center justify-between">
              <div>
                <span className="font-medium">Enable SMS</span>
                <p className="text-sm text-gray-500">Receive SMS notifications</p>
              </div>
              <input
                type="checkbox"
                checked={settings.sms_enabled}
                onChange={(e) => setSettings({ ...settings, sms_enabled: e.target.checked })}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500 h-5 w-5"
              />
            </label>

            {settings.sms_enabled && (
              <label className="flex items-center justify-between">
                <div>
                  <span className="font-medium">Critical Only</span>
                  <p className="text-sm text-gray-500">Only send SMS for critical alerts</p>
                </div>
                <input
                  type="checkbox"
                  checked={settings.sms_critical_only}
                  onChange={(e) => setSettings({ ...settings, sms_critical_only: e.target.checked })}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500 h-5 w-5"
                />
              </label>
            )}
          </div>
        </Card>

        <div className="flex justify-end">
          <Button onClick={handleSave} isLoading={loading}>
            Save Settings
          </Button>
        </div>
      </div>
    </Layout>
  );
}
