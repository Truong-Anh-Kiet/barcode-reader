import { useState } from 'react';
import { scanBarcode } from '../services/api';

const ScanUploader = ({ onScanSuccess }) => {
  const [file, setFile] = useState(null);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError('');
    try {
      const data = await scanBarcode(file);
      setResults(data);
      if (onScanSuccess) onScanSuccess();  // Refresh list
    } catch (err) {
      setError(err.response?.data?.detail || 'Scan failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-8 rounded-lg shadow-md mb-12">
      <h2 className="text-2xl font-semibold mb-6">Upload & Scan Barcode</h2>
      <div className="flex items-center gap-4 mb-6">
        <input
          type="file"
          accept="image/*"
          onChange={(e) => setFile(e.target.files[0])}
          className="file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
        />
        <button
          onClick={handleUpload}
          disabled={loading}
          className="bg-green-600 text-white px-6 py-3 rounded-md hover:bg-green-700 disabled:opacity-50"
        >
          {loading ? 'Scanning...' : 'Scan'}
        </button>
      </div>
      {error && <p className="text-red-600 font-medium mb-4">{error}</p>}
      {results && (
        <div>
          <h3 className="text-xl font-semibold mb-4">Detected {results.count} barcode(s)</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {results.data.map((item, idx) => (
              <div key={idx} className="bg-gray-50 p-6 rounded-lg shadow">
                <p className="font-medium"><strong>Content:</strong> {item.content}</p>
                <p className="font-medium"><strong>Type:</strong> {item.type}</p>
                {item.image_url && <img src={item.image_url} alt="Original" className="mt-4 rounded shadow" />}
                {item.processed_image_url && <img src={item.processed_image_url} alt="Processed" className="mt-4 rounded shadow" />}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ScanUploader;