import { useState } from 'react';
import ScanUploader from '../components/ScanUploader';
import BarcodeList from '../components/BarcodeList';
import UserProfile from '../components/UserProfile';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { getUserInfo } from '../services/api';

const HomePage = () => {
  const navigate = useNavigate();
  const [refreshKey, setRefreshKey] = useState(0);
  const [isAdmin, setIsAdmin] = useState(false);
  const [loadingAdmin, setLoadingAdmin] = useState(true);

  useEffect(() => {
    const checkAdmin = async () => {
      try {
        const user = await getUserInfo();
        setIsAdmin(!!user.is_superuser);
      } catch (err) {
        setIsAdmin(false);
      } finally {
        setLoadingAdmin(false);
      }
    };
    checkAdmin();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    toast.info('Logged out successfully!');
    navigate('/login');
  }

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-blue-600 text-white p-4 shadow-md">
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold">Barcode Scanner</h1>
          <div className="flex gap-4">
            <button onClick={() => navigate('/edit-profile')} className="hover:underline">Edit Profile</button>
            {!loadingAdmin && isAdmin && (
              <button onClick={() => navigate('/admin')} className="hover:underline">Admin</button>
            )}
            <button onClick={handleLogout} className="hover:underline">Log out</button>
          </div>
        </div>
      </nav>
      <div className="max-w-6xl mx-auto p-6">
        <UserProfile />
        <ScanUploader onScanSuccess={handleRefresh} />
        <BarcodeList key={refreshKey} />
      </div>
    </div>
  );
};

export default HomePage;