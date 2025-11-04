import { useState, useEffect } from 'react';
import { Search, Phone, Mail, MapPin, User, Loader2 } from 'lucide-react';
import api from '../lib/api';
import useAppStore from '../stores/appStore';

export default function Clients() {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const navigateToClient = useAppStore((state) => state.navigateToClient);

  useEffect(() => {
    fetchClients();
  }, []);

  const fetchClients = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getClients();
      setClients(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Error fetching clients:', err);
      setError('Failed to load clients. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const filteredClients = clients.filter((client) => {
    if (!searchQuery) return true;
    
    const query = searchQuery.toLowerCase();
    const clientName = (client['Client Name'] || '').toLowerCase();
    const email = (client['Email'] || '').toLowerCase();
    const phone = (client['Phone'] || '').toLowerCase();
    const address = (client['Address'] || '').toLowerCase();
    
    return (
      clientName.includes(query) ||
      email.includes(query) ||
      phone.includes(query) ||
      address.includes(query)
    );
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-gray-600">Loading clients...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={fetchClients}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 md:p-6 max-w-7xl mx-auto pb-20 md:pb-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">Clients</h1>
        <p className="text-gray-600">
          {filteredClients.length} {filteredClients.length === 1 ? 'client' : 'clients'}
        </p>
      </div>

      {/* Search Bar */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
          <input
            type="text"
            placeholder="Search by name, email, phone, or address..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Clients Grid */}
      {filteredClients.length === 0 ? (
        <div className="text-center py-12">
          <User className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 text-lg">
            {searchQuery ? 'No clients match your search.' : 'No clients found.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
          {filteredClients.map((client, index) => {
            const clientId = client['Client ID'] || client['ID'] || index;
            const clientName = client['Client Name'] || 'Unnamed Client';
            const email = client['Email'] || '';
            const phone = client['Phone'] || '';
            const address = client['Address'] || '';
            const city = client['City'] || '';
            const state = client['State'] || '';
            const projectCount = client['Active Projects'] || client['Projects'] || '0';

            return (
              <div
                key={clientId}
                onClick={() => navigateToClient(clientId)}
                className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow cursor-pointer"
              >
                {/* Client Name */}
                <div className="mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">{clientName}</h3>
                  <p className="text-sm text-gray-500">ID: {clientId}</p>
                </div>

                {/* Contact Info */}
                <div className="space-y-2 mb-4">
                  {email && (
                    <div className="flex items-start text-sm text-gray-600">
                      <Mail className="h-4 w-4 mr-2 mt-0.5 flex-shrink-0 text-gray-400" />
                      <span className="break-all">{email}</span>
                    </div>
                  )}
                  {phone && (
                    <div className="flex items-center text-sm text-gray-600">
                      <Phone className="h-4 w-4 mr-2 flex-shrink-0 text-gray-400" />
                      <span>{phone}</span>
                    </div>
                  )}
                  {(address || city || state) && (
                    <div className="flex items-start text-sm text-gray-600">
                      <MapPin className="h-4 w-4 mr-2 mt-0.5 flex-shrink-0 text-gray-400" />
                      <span>
                        {address && `${address}`}
                        {(city || state) && (
                          <span className="block text-xs text-gray-500">
                            {city}{city && state && ', '}{state}
                          </span>
                        )}
                      </span>
                    </div>
                  )}
                </div>

                {/* Projects Count */}
                <div className="pt-4 border-t border-gray-100">
                  <span className="text-sm font-medium text-gray-700">
                    {projectCount} Active {projectCount === '1' ? 'Project' : 'Projects'}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
