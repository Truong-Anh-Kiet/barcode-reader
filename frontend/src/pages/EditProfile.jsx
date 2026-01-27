import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { getUserInfo, updateUser } from '../services/api';

const EditProfile = () => {
  const [formData, setFormData] = useState({ fullName: '', phoneNumber: '' });
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const data = await getUserInfo();
        setFormData({ fullName: data.full_name || '', phoneNumber: data.phone_number || '' });
      } catch (err) {
        toast.error('Failed to load profile');
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await updateUser(formData);
      toast.success('Profile updated successfully');
      navigate('/');
    } catch (err) {
      toast.error('Update failed');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-lg w-full max-w-md">
        <h1 className="text-3xl font-bold text-center mb-8 text-blue-600">Edit Profile</h1>
        {loading ? <p>Loading...</p> : (
          <form onSubmit={handleSubmit} className="space-y-6">
            <input
              type="text"
              value={formData.fullName}
              onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
              placeholder="Full Name"
              className="w-full px-4 py-3 border rounded-md"
            />
            <input
              type="tel"
              value={formData.phoneNumber}
              onChange={(e) => setFormData({ ...formData, phoneNumber: e.target.value })}
              placeholder="Phone Number"
              className="w-full px-4 py-3 border rounded-md"
            />
            <button type="submit" className="w-full bg-blue-600 text-white py-3 rounded-md">Update</button>
          </form>
        )}
      </div>
    </div>
  );
};

export default EditProfile;