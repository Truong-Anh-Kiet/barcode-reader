import React, { useEffect, useState } from 'react';
import { getBarcodes, deleteBarcode } from '../services/api';

const BarcodeList = () => {
  const [barcodes, setBarcodes] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchBarcodes = async () => {
    setLoading(true);
    try {
      const data = await getBarcodes();
      setBarcodes(data);
    } catch (err) {
      setError('Failed to load list');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBarcodes();
  }, []);

  const handleDelete = async (id) => {
    try {
      await deleteBarcode(id);
      setBarcodes(barcodes.filter((item) => item.id !== id));
    } catch (err) {
      setError('Delete failed');
    }
  };

  return (
    <div className="bg-white p-8 rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-semibold">Saved Barcodes List</h2>
        <button onClick={fetchBarcodes} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
          Refresh
        </button>
      </div>
      {/* ... giữ logic loading/error */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
              {/* ... các th khác tương tự */}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {/* ... rows với class td px-6 py-4 whitespace-nowrap */}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default BarcodeList;