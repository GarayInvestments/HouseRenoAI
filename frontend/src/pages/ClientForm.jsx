import { useState } from 'react';
import api from '../lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export default function ClientForm() {
  const [form, setForm] = useState({
    full_name: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    state: 'NC',
    zip_code: '',
    client_type: 'Residential',
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
      // Use FormData to match backend Form fields
      const fd = new FormData();
      Object.entries(form).forEach(([k, v]) => fd.append(k, v ?? ''));
      const data = await api.request('/intake/client', { method: 'POST', body: fd });
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
            <CardTitle>Client Intake Form</CardTitle>
          </CardHeader>
          <CardContent>
            {result && (
              <div className="mb-4 text-sm text-green-700">
                Created client. Business ID: {result.business_id}
              </div>
            )}
            {error && (
              <div className="mb-4 text-sm text-red-700">{error}</div>
            )}
            <form onSubmit={onSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium">Full Name</label>
                <input name="full_name" value={form.full_name} onChange={onChange} className="mt-1 w-full border rounded p-2" />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium">Email</label>
                  <input name="email" value={form.email} onChange={onChange} className="mt-1 w-full border rounded p-2" />
                </div>
                <div>
                  <label className="block text-sm font-medium">Phone</label>
                  <input name="phone" value={form.phone} onChange={onChange} className="mt-1 w-full border rounded p-2" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium">Address</label>
                <input name="address" value={form.address} onChange={onChange} className="mt-1 w-full border rounded p-2" />
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm font-medium">City</label>
                  <input name="city" value={form.city} onChange={onChange} className="mt-1 w-full border rounded p-2" />
                </div>
                <div>
                  <label className="block text-sm font-medium">State</label>
                  <input name="state" value={form.state} onChange={onChange} className="mt-1 w-full border rounded p-2" />
                </div>
                <div>
                  <label className="block text-sm font-medium">Zip</label>
                  <input name="zip_code" value={form.zip_code} onChange={onChange} className="mt-1 w-full border rounded p-2" />
                </div>
                <div>
                  <label className="block text-sm font-medium">Client Type</label>
                  <select name="client_type" value={form.client_type} onChange={onChange} className="mt-1 w-full border rounded p-2">
                    <option>Residential</option>
                    <option>Commercial</option>
                  </select>
                </div>
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
