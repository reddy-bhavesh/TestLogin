import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { userAPI } from '../services/api';
import { trackAdminAction } from '../services/appInsights';
import './Forms.css';

function Forms() {
  const [user, setUser] = useState(null);
  const [formData, setFormData] = useState({
    full_name: '',
    phone: '',
    address: '',
    city: '',
    country: '',
    department: '',
    job_title: '',
    date_of_birth: '',
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });
  const navigate = useNavigate();

  useEffect(() => {
    fetchUser();
  }, []);

  const fetchUser = async () => {
    try {
      const res = await userAPI.getMe();
      setUser(res.data);
      setFormData({
        full_name: res.data.full_name || '',
        phone: res.data.phone || '',
        address: res.data.address || '',
        city: res.data.city || '',
        country: res.data.country || '',
        department: res.data.department || '',
        job_title: res.data.job_title || '',
        date_of_birth: res.data.date_of_birth || '',
      });
    } catch (err) {
      console.error('Failed to fetch user:', err);
      navigate('/login');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage({ text: '', type: '' });

    try {
      const res = await userAPI.updateMe(formData);
      setUser(res.data);
      setMessage({ text: 'Profile updated successfully!', type: 'success' });
      
      // Track profile update
      trackAdminAction(user.email, 'UPDATE_PROFILE', 'default', user.email);
    } catch (err) {
      setMessage({ text: err.response?.data?.detail || 'Failed to update profile', type: 'error' });
    } finally {
      setSaving(false);
    }
  };

  const handleAvatarUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    try {
      const res = await userAPI.uploadAvatar(file);
      setUser(res.data);
      setMessage({ text: 'Avatar uploaded successfully!', type: 'success' });
      
      // Track avatar upload
      trackAdminAction(user.email, 'UPLOAD_AVATAR', 'default', user.email);
    } catch (err) {
      setMessage({ text: 'Failed to upload avatar', type: 'error' });
    }
  };

  const handleLogout = () => {
    trackAdminAction(user?.email || 'unknown', 'USER_LOGOUT', 'default', user?.email || '');
    localStorage.removeItem('token');
    navigate('/login');
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="forms-container">
      <nav className="nav-bar">
        <div className="nav-left">
          <span className="nav-logo">POC Web App</span>
        </div>
        <div className="nav-right">
          <a href="/forms" className="nav-link active">Profile</a>
          <a href="/config" className="nav-link">Configuration</a>
          <button onClick={handleLogout} className="btn-logout">Logout</button>
        </div>
      </nav>

      <main className="forms-main">
        <div className="forms-card">
          <h2>User Profile</h2>
          <p className="subtitle">Update your personal information</p>

          <div className="avatar-section">
            <div className="avatar">
              {user?.avatar_url ? (
                <img src={user.avatar_url} alt="Avatar" />
              ) : (
                <span>{user?.full_name?.[0] || user?.email?.[0] || '?'}</span>
              )}
            </div>
            <label className="btn-upload">
              Upload Photo
              <input type="file" accept="image/*" onChange={handleAvatarUpload} hidden />
            </label>
          </div>

          <form onSubmit={handleSubmit} className="profile-form">
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input type="email" id="email" value={user?.email || ''} disabled />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="full_name">Full Name</label>
                <input
                  type="text"
                  id="full_name"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleChange}
                  placeholder="John Doe"
                />
              </div>
              <div className="form-group">
                <label htmlFor="phone">Phone Number</label>
                <input
                  type="tel"
                  id="phone"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  placeholder="+91 9876543210"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="date_of_birth">Date of Birth</label>
                <input
                  type="date"
                  id="date_of_birth"
                  name="date_of_birth"
                  value={formData.date_of_birth}
                  onChange={handleChange}
                />
              </div>
              <div className="form-group">
                <label htmlFor="job_title">Job Title</label>
                <input
                  type="text"
                  id="job_title"
                  name="job_title"
                  value={formData.job_title}
                  onChange={handleChange}
                  placeholder="Software Engineer"
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="department">Department</label>
              <input
                type="text"
                id="department"
                name="department"
                value={formData.department}
                onChange={handleChange}
                placeholder="Engineering"
              />
            </div>

            <div className="form-group">
              <label htmlFor="address">Address</label>
              <input
                type="text"
                id="address"
                name="address"
                value={formData.address}
                onChange={handleChange}
                placeholder="123 Main Street, Apt 4B"
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="city">City</label>
                <input
                  type="text"
                  id="city"
                  name="city"
                  value={formData.city}
                  onChange={handleChange}
                  placeholder="Mumbai"
                />
              </div>
              <div className="form-group">
                <label htmlFor="country">Country</label>
                <input
                  type="text"
                  id="country"
                  name="country"
                  value={formData.country}
                  onChange={handleChange}
                  placeholder="India"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Role</label>
                <input type="text" value={user?.role || ''} disabled />
              </div>
              <div className="form-group">
                <label>Status</label>
                <input type="text" value={user?.is_active ? 'Active' : 'Inactive'} disabled />
              </div>
            </div>

            {message.text && <div className={`message ${message.type}`}>{message.text}</div>}

            <button type="submit" className="btn-primary" disabled={saving}>
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}

export default Forms;
