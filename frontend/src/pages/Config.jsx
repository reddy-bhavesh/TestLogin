import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { userAPI, configAPI } from '../services/api';
import './Config.css';

function Config() {
  const [user, setUser] = useState(null);
  const [configs, setConfigs] = useState([]);
  const [users, setUsers] = useState([]);
  const [activeTab, setActiveTab] = useState('system');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });
  const navigate = useNavigate();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const userRes = await userAPI.getMe();
      setUser(userRes.data);

      if (userRes.data.role !== 'admin') {
        setMessage({ text: 'Admin access required', type: 'error' });
        setLoading(false);
        return;
      }

      const [configRes, usersRes] = await Promise.all([
        configAPI.getAll(),
        userAPI.listUsers(),
      ]);
      setConfigs(configRes.data);
      setUsers(usersRes.data);
    } catch (err) {
      console.error('Failed to fetch data:', err);
      if (err.response?.status === 401) {
        navigate('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleConfigChange = (key, value) => {
    setConfigs(configs.map(c => c.key === key ? { ...c, value } : c));
  };

  const saveConfig = async (config) => {
    setSaving(true);
    try {
      await configAPI.update(config.key, config.value, config.description);
      setMessage({ text: `${config.key} saved!`, type: 'success' });
    } catch (err) {
      setMessage({ text: 'Failed to save', type: 'error' });
    } finally {
      setSaving(false);
    }
  };

  const handleRoleChange = async (userId, newRole) => {
    try {
      await userAPI.updateRole(userId, newRole);
      setUsers(users.map(u => u.id === userId ? { ...u, role: newRole } : u));
      setMessage({ text: 'Role updated!', type: 'success' });
    } catch (err) {
      setMessage({ text: 'Failed to update role', type: 'error' });
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (user?.role !== 'admin') {
    return (
      <div className="forms-container">
        <nav className="nav-bar">
          <div className="nav-left"><span className="nav-logo">POC Web App</span></div>
          <div className="nav-right">
            <a href="/forms" className="nav-link">Profile</a>
            <a href="/config" className="nav-link active">Configuration</a>
            <button onClick={handleLogout} className="btn-logout">Logout</button>
          </div>
        </nav>
        <main className="config-main">
          <div className="access-denied">
            <h2>⚠️ Access Denied</h2>
            <p>Admin privileges required to access this page.</p>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="forms-container">
      <nav className="nav-bar">
        <div className="nav-left"><span className="nav-logo">POC Web App</span></div>
        <div className="nav-right">
          <a href="/forms" className="nav-link">Profile</a>
          <a href="/config" className="nav-link active">Configuration</a>
          <button onClick={handleLogout} className="btn-logout">Logout</button>
        </div>
      </nav>

      <main className="config-main">
        <div className="config-card">
          <h2>System Configuration</h2>
          <p className="subtitle">Manage app settings and user permissions</p>

          <div className="tabs">
            <button
              className={`tab ${activeTab === 'system' ? 'active' : ''}`}
              onClick={() => setActiveTab('system')}
            >
              ⚙️ System Settings
            </button>
            <button
              className={`tab ${activeTab === 'users' ? 'active' : ''}`}
              onClick={() => setActiveTab('users')}
            >
              👥 User Permissions
            </button>
          </div>

          {message.text && <div className={`message ${message.type}`}>{message.text}</div>}

          {activeTab === 'system' && (
            <div className="config-list">
              {configs.map((config) => (
                <div key={config.key} className="config-item">
                  <div className="config-info">
                    <label>{config.key}</label>
                    <span className="config-desc">{config.description}</span>
                  </div>
                  <div className="config-actions">
                    <input
                      type="text"
                      value={config.value}
                      onChange={(e) => handleConfigChange(config.key, e.target.value)}
                    />
                    <button onClick={() => saveConfig(config)} disabled={saving}>
                      Save
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'users' && (
            <div className="users-list">
              <table>
                <thead>
                  <tr>
                    <th>Email</th>
                    <th>Name</th>
                    <th>Role</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => (
                    <tr key={u.id}>
                      <td>{u.email}</td>
                      <td>{u.full_name || '-'}</td>
                      <td>
                        <select
                          value={u.role}
                          onChange={(e) => handleRoleChange(u.id, e.target.value)}
                          disabled={u.id === user.id}
                        >
                          <option value="admin">Admin</option>
                          <option value="user">User</option>
                          <option value="viewer">Viewer</option>
                        </select>
                      </td>
                      <td>
                        <span className={`status ${u.is_active ? 'active' : 'inactive'}`}>
                          {u.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default Config;
