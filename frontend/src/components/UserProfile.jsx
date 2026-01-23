import { useState, useEffect } from 'react';
import { getUserInfo } from '../services/api';
import { toast } from 'react-toastify';
import { UserCircleIcon } from '@heroicons/react/24/outline';

const UserProfile = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const data = await getUserInfo();
        setUser(data);
      } catch (err) {
        toast.error('Unable to load user information.');
        // Nếu lỗi 401, tự động logout (interceptor đã xử lý phần nào)
      } finally {
        setLoading(false);
      }
    };
    fetchUser();
  }, []);

  if (loading) return <div className="text-gray-500">Loading...</div>;

  if (!user) return null;

  return (
    <div className="flex items-center gap-4 bg-white px-6 py-3 rounded-lg shadow-md">
      <UserCircleIcon className="h-10 w-10 text-blue-600" />
      <div>
        <p className="font-semibold text-gray-800">
          {user.full_name || user.email}
        </p>
        <p className="text-sm text-gray-600">{user.email}</p>
        {user.is_superuser && (
          <span className="inline-block mt-1 px-3 py-1 bg-red-100 text-red-700 text-xs font-medium rounded-full">
            Admin
          </span>
        )}
      </div>
    </div>
  );
};

export default UserProfile;