// App.js
import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import UserChat from './components/UserChat';
import AdminPanel from './components/AdminPanel';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');
  const [userRole, setUserRole] = useState('');
  
  const handleLogin = (user, role) => {
    setIsAuthenticated(true);
    setUsername(user);
    setUserRole(role);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setUsername('');
    setUserRole('');
  };

  const isAdmin = userRole === 'admin';

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/login" element={
            isAuthenticated ? 
            <Navigate to={isAdmin ? "/admin" : "/chat"} /> : 
            <Login onLogin={handleLogin} />
          } />
          <Route path="/register" element={
            isAuthenticated ? 
            <Navigate to={isAdmin ? "/admin" : "/chat"} /> : 
            <Register />
          } />
          <Route path="/chat" element={
            isAuthenticated ? 
            <UserChat username={username} onLogout={handleLogout} /> : 
            <Navigate to="/login" />
          } />
          <Route path="/admin/*" element={
            isAuthenticated && isAdmin ? 
            <AdminPanel username={username} onLogout={handleLogout} /> : 
            <Navigate to="/login" />
          } />
          <Route path="/" element={<Navigate to="/login" />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;