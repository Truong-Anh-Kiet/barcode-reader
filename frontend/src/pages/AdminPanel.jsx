import { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import { getUsers, deleteUser } from '../services/api';
import { useNavigate } from 'react-router-dom';

const AdminPanel = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const checkAndFetch = async () => {
      try {
        const currentUser = await getUserInfo();
        if (!currentUser.is_superuser) {
          toast.error('Access denied: Admin only');
          navigate('/');
          return;
        }

        const data = await getUsers();
        setUsers(data);
      } catch (err) {
        toast.error('Failed to load data or access denied');
        navigate('/');
      } finally {
        setLoading(false);
      }
    };
    checkAndFetch();
  }, [navigate]);
  
  const handleDelete = async (id) => {
    try {
      await deleteUser(id);
      toast.success('User deleted successfully');
      setUsers(users.filter((u) => u.id !== id));
    } catch (err) {
      toast.error('Failed to delete user');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-3xl font-bold mb-6">Panel Admin</h1>
      {loading ? <p>Loading...</p> : (
        <table className="min-w-full bg-white shadow-md rounded">
          <thead>
            <tr>
              <th className="py-2 px-4 border-b">ID</th>
              <th className="py-2 px-4 border-b">Email</th>
              <th className="py-2 px-4 border-b">Full Name</th>
              <th className="py-2 px-4 border-b">Action</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id}>
                <td className="py-2 px-4 border-b">{user.id}</td>
                <td className="py-2 px-4 border-b">{user.email}</td>
                <td className="py-2 px-4 border-b">{user.full_name}</td>
                <td className="py-2 px-4 border-b">
                  <button onClick={() => handleDelete(user.id)} className="text-red-600 hover:underline">Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default AdminPanel;