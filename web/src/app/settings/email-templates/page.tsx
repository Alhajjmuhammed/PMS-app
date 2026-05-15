'use client';

import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Input from '@/components/Input';
import Button from '@/components/Button';
import Table from '@/components/Table';
import Modal from '@/components/Modal';

const STORAGE_KEY = 'pms_email_templates';

const DEFAULT_TEMPLATES: EmailTemplate[] = [
  { id: 1, name: 'Reservation Confirmation', subject: 'Your reservation is confirmed', body: 'Dear {{guest_name}},\n\nYour reservation has been confirmed...', category: 'confirmation', active: true, created_at: new Date().toISOString() },
  { id: 2, name: 'Check-in Reminder', subject: 'Your check-in is tomorrow', body: 'Dear {{guest_name}},\n\nThis is a reminder that your check-in is scheduled for tomorrow...', category: 'reminder', active: true, created_at: new Date().toISOString() },
];

interface EmailTemplate {
  id: number;
  name: string;
  subject: string;
  body: string;
  category: string;
  active: boolean;
  created_at: string;
}

function loadFromStorage(): EmailTemplate[] {
  if (typeof window === 'undefined') return DEFAULT_TEMPLATES;
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? JSON.parse(saved) : DEFAULT_TEMPLATES;
  } catch { return DEFAULT_TEMPLATES; }
}

function saveToStorage(templates: EmailTemplate[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(templates));
}

export default function EmailTemplatesPage() {
  const [templates, setTemplates] = useState<EmailTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<EmailTemplate | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    subject: '',
    body: '',
    category: 'reservation',
    active: true,
  });

  useEffect(() => {
    setTemplates(loadFromStorage());
    setLoading(false);
  }, []);

  const handleCreate = () => {
    setEditingTemplate(null);
    setFormData({
      name: '',
      subject: '',
      body: '',
      category: 'reservation',
      active: true,
    });
    setShowModal(true);
  };

  const handleEdit = (template: EmailTemplate) => {
    setEditingTemplate(template);
    setFormData({
      name: template.name,
      subject: template.subject,
      body: template.body,
      category: template.category,
      active: template.active,
    });
    setShowModal(true);
  };

  const handleSave = async () => {
    let updated: EmailTemplate[];
    if (editingTemplate) {
      updated = templates.map((t) =>
        t.id === editingTemplate.id ? { ...t, ...formData } : t
      );
    } else {
      const newTpl: EmailTemplate = {
        ...formData,
        id: Date.now(),
        created_at: new Date().toISOString(),
      };
      updated = [...templates, newTpl];
    }
    saveToStorage(updated);
    setTemplates(updated);
    setShowModal(false);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this template?')) return;
    const updated = templates.filter((t) => t.id !== id);
    saveToStorage(updated);
    setTemplates(updated);
  };

  const categories = [
    { value: 'reservation', label: 'Reservation' },
    { value: 'check_in', label: 'Check-in' },
    { value: 'check_out', label: 'Check-out' },
    { value: 'payment', label: 'Payment' },
    { value: 'confirmation', label: 'Confirmation' },
    { value: 'reminder', label: 'Reminder' },
    { value: 'marketing', label: 'Marketing' },
    { value: 'feedback', label: 'Feedback' },
  ];

  const variables = [
    '{{guest_name}}',
    '{{guest_email}}',
    '{{reservation_id}}',
    '{{check_in_date}}',
    '{{check_out_date}}',
    '{{room_number}}',
    '{{room_type}}',
    '{{total_amount}}',
    '{{property_name}}',
    '{{property_phone}}',
  ];

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">Loading templates...</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Email Templates</h1>
            <p className="text-gray-500">Manage automated email templates</p>
          </div>
          <Button onClick={handleCreate}>+ New Template</Button>
        </div>

        {/* Templates Table */}
        <Card>
          <Table
            columns={[
              { key: 'name', label: 'Template Name' },
              { key: 'category', label: 'Category' },
              { key: 'subject', label: 'Subject' },
              { key: 'active', label: 'Status' },
              { key: 'actions', label: 'Actions' },
            ]}
            data={templates.map((template) => ({
              name: template.name,
              category: (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 capitalize">
                  {template.category.replace('_', ' ')}
                </span>
              ),
              subject: template.subject,
              active: (
                <span
                  className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    template.active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {template.active ? 'Active' : 'Inactive'}
                </span>
              ),
              actions: (
                <div className="flex gap-2">
                  <Button size="sm" variant="outline" onClick={() => handleEdit(template)}>
                    Edit
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => handleDelete(template.id)}>
                    Delete
                  </Button>
                </div>
              ),
            }))}
          />
        </Card>

        {/* Template Editor Modal */}
        <Modal isOpen={showModal} onClose={() => setShowModal(false)} title={editingTemplate ? 'Edit Template' : 'Create Template'}>
          <div className="space-y-4">
            <Input
              label="Template Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g., Booking Confirmation"
              required
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              >
                {categories.map((cat) => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </div>

            <Input
              label="Subject Line"
              value={formData.subject}
              onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
              placeholder="Your reservation is confirmed"
              required
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email Body</label>
              <textarea
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows={10}
                value={formData.body}
                onChange={(e) => setFormData({ ...formData, body: e.target.value })}
                placeholder="Dear {{guest_name}},&#10;&#10;Your reservation has been confirmed..."
                required
              />
              <p className="text-xs text-gray-500 mt-1">Use variables from the list below</p>
            </div>

            {/* Available Variables */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm font-medium text-gray-700 mb-2">Available Variables:</p>
              <div className="flex flex-wrap gap-2">
                {variables.map((variable, index) => (
                  <button
                    key={index}
                    onClick={() => {
                      const newBody = formData.body + ' ' + variable;
                      setFormData({ ...formData, body: newBody });
                    }}
                    className="text-xs px-2 py-1 bg-white border border-gray-300 rounded hover:bg-gray-100"
                  >
                    {variable}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="active"
                checked={formData.active}
                onChange={(e) => setFormData({ ...formData, active: e.target.checked })}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="active" className="ml-2 block text-sm text-gray-700">
                Template is active
              </label>
            </div>

            <div className="flex gap-4 pt-4">
              <Button onClick={handleSave}>
                {editingTemplate ? 'Update Template' : 'Create Template'}
              </Button>
              <Button variant="outline" onClick={() => setShowModal(false)}>
                Cancel
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </Layout>
  );
}
