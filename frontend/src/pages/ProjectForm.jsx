import { useState } from 'react';
import api from '../lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export default function ProjectForm() {
  // Read client_id from URL if present
  const urlParams = new URLSearchParams(window.location.search);
  const initialClientId = urlParams.get('client_id') || '';

  const [form, setForm] = useState({
    client_id: initialClientId,
    project_name: '',
    project_address: '',
    project_type: 'RENOVATION',
    description: '',
    notes: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const onChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    setError(null);
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const fd = new FormData();
      Object.entries(form).forEach(([k, v]) => fd.append(k, v ?? ''));
      const data = await api.request('/intake/project', { method: 'POST', body: fd });
      setResult(data);
    } catch (err) {
      setError(err.message || 'Submission failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-2xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle>Project Intake Form</CardTitle>
          </CardHeader>
          <CardContent>
            {result && (
              <div className="mb-4 text-sm text-green-700">
                Created project. Business ID: {result.business_id}
              </div>
            )}
            {error && (
              <div className="mb-4 text-sm text-red-700">{error}</div>
            )}
            <form onSubmit={onSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium">Client ID</label>
                <input name="client_id" value={form.client_id} onChange={onChange} className="mt-1 w-full border rounded p-2" placeholder="Paste client_id from client form response" />
              </div>
              <div>
                <label className="block text-sm font-medium">Project Name</label>
                <input name="project_name" value={form.project_name} onChange={onChange} className="mt-1 w-full border rounded p-2" />
              </div>
              <div>
                <label className="block text-sm font-medium">Project Address</label>
                <input name="project_address" value={form.project_address} onChange={onChange} className="mt-1 w-full border rounded p-2" />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium">Project Type</label>
                  <select name="project_type" value={form.project_type} onChange={onChange} className="mt-1 w-full border rounded p-2">
                    <option>RENOVATION</option>
                    <option>REMODEL</option>
                    <option>ADDITION</option>
                    <option>RESIDENTIAL</option>
                    <option>COMMERCIAL</option>
                    <option>OTHER</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium">Description</label>
                <textarea name="description" value={form.description} onChange={onChange} className="mt-1 w-full border rounded p-2" rows={4} />
              </div>
              <div>
                <label className="block text-sm font-medium">Notes</label>
                <textarea name="notes" value={form.notes} onChange={onChange} className="mt-1 w-full border rounded p-2" rows={3} />
              </div>
              <div className="flex justify-end">
                <Button type="submit" disabled={loading}>{loading ? 'Submitting...' : 'Submit'}</Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
