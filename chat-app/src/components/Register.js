import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Register.css';

function Register() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Aquí verificarías que las contraseñas coincidan y enviarías los datos al backend
    if (formData.password === formData.confirmPassword) {
      // Simulación de registro exitoso
      alert('Registro exitoso! Por favor inicia sesión.');
      navigate('/login');
    } else {
      alert('Las contraseñas no coinciden');
    }
  };

  return (
    <div className="register-container">
      <div className="register-box">
        <div className="register-left">
          <h1 className="app-title">IA Datapar</h1>
        </div>
        <div className="register-right">
          <h2 className="form-title">Crear Cuenta</h2>
          <form onSubmit={handleSubmit} className="register-form">
            <div className="form-group">
              <label htmlFor="username">Nombre de usuario</label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="email">Correo electrónico</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="password">Contraseña</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="confirmPassword">Confirmar contraseña</label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
              />
            </div>
            <div className="buttons-container">
              <button type="submit" className="register-btn">Registrarse</button>
              <Link to="/login" className="login-link">Ya tengo una cuenta</Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default Register;
