import { useState, useEffect} from 'react';
import ScanUploader from '../components/ScanUploader';
import BarcodeList from '../components/BarcodeList';
import UserProfile from '../components/UserProfile';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { getUserInfo } from '../services/api';
import { Button } from '@/components/ui/button';

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
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold">Barcode Scanner</h1>
          <div className="flex gap-4">
            <Button variant="ghost" onClick={() => navigate('/edit-profile')} className="text-white hover:bg-blue-700">
              Edit Profile
            </Button>
            {!loadingAdmin && isAdmin && (
              <Button variant="ghost" onClick={() => navigate('/admin')} className="text-white hover:bg-blue-700">
                Admin
              </Button>
            )}
            <Button variant="ghost" onClick={handleLogout} className="text-white hover:bg-blue-700">
              Log out
            </Button>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-12">
        <UserProfile />
        <ScanUploader onScanSuccess={handleRefresh} />
        <BarcodeList key={refreshKey} />
      </div>
    </div>
  );
};

export default HomePage;