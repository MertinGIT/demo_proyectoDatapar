import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './Login.css';

function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const handleSubmit = (e) => {
    e.preventDefault();
    
    // This is where you would normally authenticate with your backend
    // For now, we'll simulate authentication and role assignment
    
    if (username && password) {
      // Check if user is admin (in a real app, this would come from backend)
      const isAdmin = username.toLowerCase() === 'admin';
      const role = isAdmin ? 'admin' : 'user';
      
      // Pass both username and role to the login handler
      onLogin(username, role);
    } else {
      setError('Por favor ingrese usuario y contraseña');
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <div className="login-left">
          <h1 className="app-title">IA Datapar</h1>
        </div>
        <div className="login-right">
          <form onSubmit={handleSubmit} className="login-form">
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <div className="buttons-container">
              <button type="submit" className="login-btn">Iniciar Sesión</button>
              <Link to="/register" className="register-link">Registrarse</Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default Login;
