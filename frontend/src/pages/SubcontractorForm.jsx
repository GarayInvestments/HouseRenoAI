import { useState, useRef } from 'react';
import { Upload, AlertCircle, CheckCircle, Loader2, X } from 'lucide-react';
import api from '../lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import ErrorState from '../components/ErrorState';

const TRADES = [
  'ELECTRICAL',
  'PLUMBING',
  'HVAC',
  'ROOFING',
  'CARPENTRY',
  'MASONRY',
  'PAINTING',
  'FLOORING',
  'LANDSCAPING',
  'CONCRETE',
  'FRAMING',
  'DRYWALL',
  'INSULATION',
  'OTHER'
];

const STATES = [
  'NC', 'SC', 'VA', 'GA', 'TN', 'WV', 'PA', 'KY', 'OH', 'MD'
];

/**
 * Public-facing subcontractor form for clients to submit their subcontractors.
 * Can be submitted for a specific project or permit.
 * 
 * Usage:
 * <SubcontractorForm projectId={projectId} permitId={permitId} />
 * or in standalone mode with URL params
 */
export default function SubcontractorForm({ projectId = null, permitId = null }) {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
    company_name: '',
    trade: 'ELECTRICAL',
    license_number: '',
    license_state: 'NC',
    bond_number: '',
    bond_amount: '',
    notes: '',
    project_id: projectId || '',
    permit_id: permitId || '',
  });

  const [files, setFiles] = useState({
    coi_file: null,
    workers_comp_file: null,
  });

  const [fileNames, setFileNames] = useState({
    coi_file: '',
    workers_comp_file: '',
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  const coiInputRef = useRef(null);
  const workersCompInputRef = useRef(null);

  // Get project/permit ID from URL if not provided as props
  const getProjectIdFromUrl = () => {
    const params = new URLSearchParams(window.location.search);
    return params.get('projectId') || params.get('project_id');
  };

  const getPermitIdFromUrl = () => {
    const params = new URLSearchParams(window.location.search);
    return params.get('permitId') || params.get('permit_id');
  };

  const effectiveProjectId = formData.project_id || getProjectIdFromUrl();
  const effectivePermitId = formData.permit_id || getPermitIdFromUrl();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError(null); // Clear error on input change
  };

  const handleFileSelect = (e, fileType) => {
    const file = e.target.files?.[0];
    if (file) {
      setFiles(prev => ({
        ...prev,
        [fileType]: file
      }));
      setFileNames(prev => ({
        ...prev,
        [fileType]: file.name
      }));
      setError(null);
    }
  };

  const removeFile = (fileType) => {
    setFiles(prev => ({
      ...prev,
      [fileType]: null
    }));
    setFileNames(prev => ({
      ...prev,
      [fileType]: ''
    }));
    if (fileType === 'coi_file') coiInputRef.current.value = '';
    if (fileType === 'workers_comp_file') workersCompInputRef.current.value = '';
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate required fields
    if (!formData.full_name) {
      setError('Name is required');
      return;
    }
    if (!formData.email) {
      setError('Email is required');
      return;
    }
    if (!formData.phone) {
      setError('Phone is required');
      return;
    }
    if (!effectiveProjectId && !effectivePermitId) {
      setError('Project or Permit ID must be provided');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Create FormData for file uploads
      const submitData = new FormData();
      
      // Add form fields
      Object.entries(formData).forEach(([key, value]) => {
        if (value || key === 'project_id' || key === 'permit_id') {
          submitData.append(key, value);
        }
      });

      // Use correct IDs
      submitData.set('project_id', effectiveProjectId || '');
      submitData.set('permit_id', effectivePermitId || '');

      // Add files
      if (files.coi_file) {
        submitData.append('coi_file', files.coi_file);
      }
      if (files.workers_comp_file) {
        submitData.append('workers_comp_file', files.workers_comp_file);
      }

      // Submit via centralized API service (handles token if present)
      const result = await api.request('/subcontractors/form', {
        method: 'POST',
        body: submitData,
      });
      
      setSuccess(true);
      setSuccessMessage(
        `Success! Subcontractor ${formData.full_name} submitted for approval. (ID: ${result.business_id})`
      );
      
      // Reset form
      setTimeout(() => {
        setFormData({
          full_name: '',
          email: '',
          phone: '',
          company_name: '',
          trade: 'ELECTRICAL',
          license_number: '',
          license_state: 'NC',
          bond_number: '',
          bond_amount: '',
          notes: '',
          project_id: projectId || '',
          permit_id: permitId || '',
        });
        setFiles({
          coi_file: null,
          workers_comp_file: null,
        });
        setFileNames({
          coi_file: '',
          workers_comp_file: '',
        });
        setSuccess(false);
      }, 3000);
    } catch (err) {
      console.error('Form submission error:', err);
      setError(err.message || 'Failed to submit form. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Subcontractor Information Form
          </h1>
          <p className="text-gray-600 mt-2">
            Please provide details about the subcontractors working on your project.
            All information will be reviewed and approved by our team.
          </p>
        </div>

        {/* Success Message */}
        {success && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-start gap-3">
            <CheckCircle className="text-green-600 flex-shrink-0 mt-0.5" size={20} />
            <div>
              <p className="text-green-800 font-medium">Form Submitted Successfully</p>
              <p className="text-green-700 text-sm mt-1">{successMessage}</p>
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
            <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={20} />
            <div>
              <p className="text-red-800 font-medium">Error</p>
              <p className="text-red-700 text-sm mt-1">{error}</p>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Basic Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Full Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleInputChange}
                    placeholder="John Smith"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Company Name
                  </label>
                  <input
                    type="text"
                    name="company_name"
                    value={formData.company_name}
                    onChange={handleInputChange}
                    placeholder="ABC Electrical"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    placeholder="john@example.com"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Phone <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    placeholder="(555) 123-4567"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Trade & License */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Trade & Licensing</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Trade <span className="text-red-500">*</span>
                </label>
                <select
                  name="trade"
                  value={formData.trade}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {TRADES.map(trade => (
                    <option key={trade} value={trade}>
                      {trade}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    License Number
                  </label>
                  <input
                    type="text"
                    name="license_number"
                    value={formData.license_number}
                    onChange={handleInputChange}
                    placeholder="e.g., EC-123456"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    License State
                  </label>
                  <select
                    name="license_state"
                    value={formData.license_state}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {STATES.map(state => (
                      <option key={state} value={state}>{state}</option>
                    ))}
                  </select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Bonding & Insurance */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Bonding & Insurance</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Bond Number (Mecklenburg County)
                  </label>
                  <input
                    type="text"
                    name="bond_number"
                    value={formData.bond_number}
                    onChange={handleInputChange}
                    placeholder="Bond #"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Bond Amount ($)
                  </label>
                  <input
                    type="number"
                    name="bond_amount"
                    value={formData.bond_amount}
                    onChange={handleInputChange}
                    placeholder="50000"
                    step="1000"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              {/* Certificate of Insurance */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Certificate of Insurance (COI)
                </label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
                  {fileNames.coi_file ? (
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Upload size={20} className="text-green-600" />
                        <span className="text-sm text-gray-700">{fileNames.coi_file}</span>
                      </div>
                      <button
                        type="button"
                        onClick={() => removeFile('coi_file')}
                        className="text-gray-400 hover:text-red-600"
                      >
                        <X size={20} />
                      </button>
                    </div>
                  ) : (
                    <div>
                      <Upload size={24} className="mx-auto mb-2 text-gray-400" />
                      <p className="text-sm text-gray-600">
                        <button
                          type="button"
                          onClick={() => coiInputRef.current?.click()}
                          className="text-blue-600 hover:underline font-medium"
                        >
                          Click to upload
                        </button>
                        {' '}or drag and drop
                      </p>
                      <p className="text-xs text-gray-500 mt-1">PDF, JPG, PNG up to 10MB</p>
                    </div>
                  )}
                  <input
                    ref={coiInputRef}
                    type="file"
                    onChange={(e) => handleFileSelect(e, 'coi_file')}
                    accept=".pdf,.jpg,.jpeg,.png"
                    className="hidden"
                  />
                </div>
              </div>

              {/* Workers Compensation */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Workers Compensation Insurance
                </label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
                  {fileNames.workers_comp_file ? (
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Upload size={20} className="text-green-600" />
                        <span className="text-sm text-gray-700">{fileNames.workers_comp_file}</span>
                      </div>
                      <button
                        type="button"
                        onClick={() => removeFile('workers_comp_file')}
                        className="text-gray-400 hover:text-red-600"
                      >
                        <X size={20} />
                      </button>
                    </div>
                  ) : (
                    <div>
                      <Upload size={24} className="mx-auto mb-2 text-gray-400" />
                      <p className="text-sm text-gray-600">
                        <button
                          type="button"
                          onClick={() => workersCompInputRef.current?.click()}
                          className="text-blue-600 hover:underline font-medium"
                        >
                          Click to upload
                        </button>
                        {' '}or drag and drop
                      </p>
                      <p className="text-xs text-gray-500 mt-1">PDF, JPG, PNG up to 10MB</p>
                    </div>
                  )}
                  <input
                    ref={workersCompInputRef}
                    type="file"
                    onChange={(e) => handleFileSelect(e, 'workers_comp_file')}
                    accept=".pdf,.jpg,.jpeg,.png"
                    className="hidden"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Additional Notes */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Additional Information</CardTitle>
            </CardHeader>
            <CardContent>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Notes
              </label>
              <textarea
                name="notes"
                value={formData.notes}
                onChange={handleInputChange}
                placeholder="Any additional information about this subcontractor..."
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </CardContent>
          </Card>

          {/* Project/Permit Info */}
          {(effectiveProjectId || effectivePermitId) && (
            <Card className="bg-blue-50 border-blue-200">
              <CardContent className="pt-6">
                <p className="text-sm text-gray-700">
                  <span className="font-medium">Submitting for:</span>
                  {effectiveProjectId && <span className="ml-2 text-blue-700">Project ID: {effectiveProjectId}</span>}
                  {effectiveProjectId && effectivePermitId && <span className="mx-1">•</span>}
                  {effectivePermitId && <span className="text-blue-700">Permit ID: {effectivePermitId}</span>}
                </p>
              </CardContent>
            </Card>
          )}

          {/* Submit Button */}
          <div className="flex gap-4">
            <Button
              type="submit"
              disabled={loading}
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
            >
              {loading ? (
                <>
                  <Loader2 size={16} className="mr-2 animate-spin" />
                  Submitting...
                </>
              ) : (
                'Submit Subcontractor Information'
              )}
            </Button>
            <Button
              type="button"
              onClick={() => window.history.back()}
              variant="outline"
              className="px-8"
            >
              Cancel
            </Button>
          </div>
        </form>

        {/* Info Box */}
        <div className="mt-8 p-4 bg-gray-50 border border-gray-200 rounded-lg">
          <h3 className="font-medium text-gray-900 mb-2">What Happens Next?</h3>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>✓ Your subcontractor information will be reviewed by our team</li>
            <li>✓ We'll verify licenses and insurance documents</li>
            <li>✓ You'll receive a confirmation email when approved</li>
            <li>✓ Any issues will be communicated via email</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
