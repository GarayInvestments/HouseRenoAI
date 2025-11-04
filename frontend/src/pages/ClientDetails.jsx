import { useState, useEffect } from 'react';
import { ArrowLeft, User, Mail, Phone, MapPin, Calendar, FileText, Loader2 } from 'lucide-react';
import api from '../lib/api';
import useAppStore from '../stores/appStore';

export default function ClientDetails() {
  const [client, setClient] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const currentClientId = useAppStore((state) => state.currentClientId);
  const navigateToClients = useAppStore((state) => state.navigateToClients);

  useEffect(() => {
    // Handle browser back button
    const handlePopState = () => {
      navigateToClients();
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, [navigateToClients]);

  useEffect(() => {
    // Push state for browser back button support
    window.history.pushState({ view: 'client-details' }, '', '');
    
    if (currentClientId) {
      fetchClientDetails();
    }
  }, [currentClientId]);

  const fetchClientDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getClient(currentClientId);
      console.log('Client data received:', data);
      console.log('Available keys:', Object.keys(data));
      setClient(data);
    } catch (err) {
      console.error('Error fetching client details:', err);
      setError('Failed to load client details. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleBackClick = () => {
    window.history.back();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-gray-600">Loading client details...</p>
        </div>
      </div>
    );
  }

  if (error || !client) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error || 'Client not found'}</p>
          <button
            onClick={fetchClientDetails}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const clientName = client['Full Name'] || client['Client Name'] || 'Unnamed Client';
  const clientId = client['Client ID'] || client['ID'] || '';
  const email = client['Email'] || '';
  const phone = client['Phone'] || '';
  const address = client['Address'] || '';
  const city = client['City'] || '';
  const state = client['State'] || '';
  const zip = client['ZIP'] || client['Zip Code'] || '';
  const dateAdded = client['Date Added'] || client['Created Date'] || '';
  const activeProjects = client['Active Projects'] || client['Projects'] || '0';
  const notes = client['Notes'] || client['Client Notes'] || '';
  const preferredContact = client['Preferred Contact Method'] || '';
  const companyName = client['Company Name'] || '';

  return (
    <div className="p-4 md:p-6 max-w-4xl mx-auto pb-20 md:pb-6">
      {/* Back Button */}
      <button
        onClick={handleBackClick}
        className="flex items-center text-gray-600 hover:text-gray-900 mb-6"
      >
        <ArrowLeft className="h-5 w-5 mr-2" />
        <span>Back to Clients</span>
      </button>

      {/* Client Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">{clientName}</h1>
            {companyName && (
              <p className="text-lg text-gray-600 mb-1">{companyName}</p>
            )}
            <p className="text-sm text-gray-500">Client ID: {clientId}</p>
          </div>
          <div className="bg-blue-50 p-3 rounded-full">
            <User className="h-8 w-8 text-blue-600" />
          </div>
        </div>
      </div>

      {/* Contact Information */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Contact Information</h2>
        <div className="space-y-4">
          {email && (
            <div className="flex items-start">
              <Mail className="h-5 w-5 mr-3 mt-0.5 text-gray-400" />
              <div>
                <p className="text-sm text-gray-500">Email</p>
                <a href={`mailto:${email}`} className="text-blue-600 hover:underline break-all">
                  {email}
                </a>
              </div>
            </div>
          )}
          {phone && (
            <div className="flex items-start">
              <Phone className="h-5 w-5 mr-3 mt-0.5 text-gray-400" />
              <div>
                <p className="text-sm text-gray-500">Phone</p>
                <a href={`tel:${phone}`} className="text-blue-600 hover:underline">
                  {phone}
                </a>
              </div>
            </div>
          )}
          {preferredContact && (
            <div className="flex items-start">
              <FileText className="h-5 w-5 mr-3 mt-0.5 text-gray-400" />
              <div>
                <p className="text-sm text-gray-500">Preferred Contact Method</p>
                <p className="text-gray-900">{preferredContact}</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Address Information */}
      {(address || city || state || zip) && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Address</h2>
          <div className="flex items-start">
            <MapPin className="h-5 w-5 mr-3 mt-0.5 text-gray-400" />
            <div>
              {address && <p className="text-gray-900">{address}</p>}
              {(city || state || zip) && (
                <p className="text-gray-900">
                  {city}{city && (state || zip) && ', '}
                  {state} {zip}
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Client Details */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Client Details</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {dateAdded && (
            <div className="flex items-start">
              <Calendar className="h-5 w-5 mr-3 mt-0.5 text-gray-400" />
              <div>
                <p className="text-sm text-gray-500">Date Added</p>
                <p className="text-gray-900">{dateAdded}</p>
              </div>
            </div>
          )}
          <div className="flex items-start">
            <FileText className="h-5 w-5 mr-3 mt-0.5 text-gray-400" />
            <div>
              <p className="text-sm text-gray-500">Active Projects</p>
              <p className="text-gray-900 font-semibold">{activeProjects}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Notes */}
      {notes && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Notes</h2>
          <p className="text-gray-700 whitespace-pre-wrap">{notes}</p>
        </div>
      )}

      {/* All Fields (Debug/Admin View) */}
      <details className="bg-gray-50 rounded-lg border border-gray-200 p-6">
        <summary className="text-sm font-medium text-gray-700 cursor-pointer hover:text-gray-900">
          View All Fields
        </summary>
        <div className="mt-4 space-y-2">
          {Object.entries(client).map(([key, value]) => (
            <div key={key} className="flex border-b border-gray-200 pb-2">
              <span className="text-sm font-medium text-gray-600 w-1/3">{key}:</span>
              <span className="text-sm text-gray-900 w-2/3 break-all">
                {typeof value === 'object' && value !== null 
                  ? JSON.stringify(value, null, 2) 
                  : (value || '—')}
              </span>
            </div>
          ))}
        </div>
      </details>
    </div>
  );
}
