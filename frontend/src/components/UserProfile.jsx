import { useState, useEffect } from 'react';
import { getUserInfo } from '../services/api';
import { toast } from 'react-toastify';
import { Card, CardContent } from '@/components/ui/card';
import { UserCircleIcon } from '@heroicons/react/24/outline';
import { Badge } from '@/components/ui/badge';

const UserProfile = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const data = await getUserInfo();
        setUser(data);
      } catch (err) {
        toast.error('Failed to load user information.');
      } finally {
        setLoading(false);
      }
    };
    fetchUser();
  }, []);

  if (loading || !user) return null;

  return (
    <Card className="mb-6">
      <CardContent className="flex items-center gap-4 pt-6">
        <UserCircleIcon className="h-12 w-12 text-blue-600" />
        <div>
          <p className="text-lg font-semibold">
            {user.full_name || user.email}
          </p>
          <p className="text-sm text-muted-foreground">{user.email}</p>
          {user.is_superuser && (
            <Badge variant="destructive" className="mt-1">Admin</Badge>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default UserProfile;