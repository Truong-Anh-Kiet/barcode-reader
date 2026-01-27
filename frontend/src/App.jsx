import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import HomePage from './pages/Home';
import AuthPage from './pages/Auth';
import ForgotPassword from './pages/ForgotPassword';
import EditProfile from './pages/EditProfile';
import AdminPanel from './pages/AdminPanel';
import ResetPassword from './pages/ResetPassword';

function ProtectedRoute({ children }) {
  const token = localStorage.getItem('token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

function App() {
  return (
    <Router>
      <div className="container">
        <Routes>
          <Route path="/login" element={<AuthPage />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/edit-profile" element={<ProtectedRoute><EditProfile /></ProtectedRoute>} />
          <Route path="/admin" element={<ProtectedRoute><AdminPanel /></ProtectedRoute>} />
          <Route path="/" element={<ProtectedRoute><HomePage /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/" replace />} />
          <Route path="/reset-password" element={<ResetPassword />} />
        </Routes>
      </div>
      <ToastContainer position="top-right" autoClose={3000} theme="colored" />
    </Router>
  );
}

export default App;