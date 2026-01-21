import React, { useEffect, useState } from 'react';
import ScanUploader from '../components/ScanUploader';
import BarcodeList from '../components/BarcodeList';
import { useNavigate } from 'react-router-dom';

const HomePage = () => {
  const navigate = useNavigate();
  const [refreshKey, setRefreshKey] = useState(0);  // Để refresh list sau scan/delete

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  // Refresh list sau mỗi lần scan/delete (có thể gọi callback từ child nếu cần)
  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto p-6">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800">Barcode Scanner Dashboard</h1>
          <button
            onClick={handleLogout}
            className="bg-red-600 text-white px-6 py-3 rounded-md hover:bg-red-700 transition"
          >
            Đăng Xuất
          </button>
        </div>
        <ScanUploader onScanSuccess={handleRefresh} />
        <BarcodeList key={refreshKey} />
      </div>
    </div>
  );
};

export default HomePage;