import React, { useState } from 'react';
import { Routes, Route, Link, useNavigate } from 'react-router-dom';
import './AdminPanel.css';

// Subcomponents for the admin panel
const Dashboard = ({ users, documents }) => (
  <div className="content-section">
    <h2>Dashboard</h2>
    <div className="dashboard-stats">
      <div className="stat-card">
        <h3>Usuarios</h3>
        <p className="stat-number">{users.length}</p>
      </div>
      <div className="stat-card">
        <h3>Documentos</h3>
        <p className="stat-number">{documents.length}</p>
      </div>
      <div className="stat-card">
        <h3>Roles</h3>
        <p className="stat-number">3</p>
      </div>
    </div>
    <div className="recent-activity">
      <h3>Actividad Reciente</h3>
      <ul>
        <li>Ana Gómez subió un nuevo documento</li>
        <li>Juan Pérez editó un usuario</li>
        <li>Carlos Ruiz fue asignado a un nuevo rol</li>
      </ul>
    </div>
  </div>
);

const UserManagement = ({ users, handleDeleteUser }) => (
  <div className="content-section">
    <h2>Gestión de Usuarios</h2>
    <div className="table-container">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Email</th>
            <th>Rol</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {users.map(user => (
            <tr key={user.id}>
              <td>{user.id}</td>
              <td>{user.name}</td>
              <td>{user.email}</td>
              <td>{user.role}</td>
              <td>
                <button className="btn-edit">Editar</button>
                <button className="btn-delete" onClick={() => handleDeleteUser(user.id)}>Eliminar</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
    <button className="btn-add">Agregar Usuario</button>
  </div>
);


const DocumentManagement = ({ documents, handleDeleteDocument }) => (
  <div className="content-section">
    <h2>Gestión de Documentos</h2>
    <div className="table-container">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Subido por</th>
            <th>Fecha</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {documents.map(doc => (
            <tr key={doc.id}>
              <td>{doc.id}</td>
              <td>{doc.name}</td>
              <td>{doc.uploadedBy}</td>
              <td>{doc.date}</td>
              <td>
                <button className="btn-view">Ver</button>
                <button className="btn-edit">Editar</button>
                <button className="btn-delete" onClick={() => handleDeleteDocument(doc.id)}>Eliminar</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
    <button className="btn-add">Cargar Documento</button>
  </div>
);

const RoleManagement = ({ setShowRoleModal }) => (
  <div className="content-section">
    <h2>Asignación de Roles</h2>
    <div className="role-management">
      <div className="role-card">
        <h3>Roles disponibles</h3>
        <ul>
          <li>
            <div className="role-name">Administrador</div>
            <div className="role-actions">
              <button className="btn-edit">Editar</button>
              <button className="btn-view" onClick={() => setShowRoleModal(true)}>Asignar</button>
            </div>
          </li>
          <li>
            <div className="role-name">Editor</div>
            <div className="role-actions">
              <button className="btn-edit">Editar</button>
              <button className="btn-view" onClick={() => setShowRoleModal(true)}>Asignar</button>
            </div>
          </li>
          <li>
            <div className="role-name">Usuario</div>
            <div className="role-actions">
              <button className="btn-edit">Editar</button>
              <button className="btn-view" onClick={() => setShowRoleModal(true)}>Asignar</button>
            </div>
          </li>
        </ul>
        <button className="btn-add">Crear Rol</button>
      </div>
    </div>
  </div>
);

const AdminPanel = ({ username, onLogout }) => {
  const navigate = useNavigate();
  const [showRoleModal, setShowRoleModal] = useState(false);
  const [users, setUsers] = useState([
    { id: '001', name: 'Juan Pérez', email: 'juan@ejemplo.com', role: 'Administrador' },
    { id: '002', name: 'Ana Gómez', email: 'ana@ejemplo.com', role: 'Editor' },
    { id: '003', name: 'Carlos Ruiz', email: 'carlos@ejemplo.com', role: 'Usuario' },
  ]);
  const [documents, setDocuments] = useState([
    { id: '001', name: 'Reporte Anual.pdf', uploadedBy: 'Juan Pérez', date: '01/03/2025' },
    { id: '002', name: 'Manual de Usuario.pdf', uploadedBy: 'Ana Gómez', date: '15/03/2025' },
    { id: '003', name: 'Presentación.pdf', uploadedBy: 'Carlos Ruiz', date: '22/03/2025' },
  ]);

  const handleDeleteUser = (id) => {
    setUsers(users.filter(user => user.id !== id));
  };

  const handleDeleteDocument = (id) => {
    setDocuments(documents.filter(doc => doc.id !== id));
  };

  const handleLogout = () => {
    onLogout();
    navigate('/login');
  };

  return (
    <div className="admin-panel">
      <div className="sidebar">
        <div className="logo">ADMIN PANEL</div>
        <div className="user-info">
          <p>Bienvenido, {username}</p>
        </div>
        <nav>
          <ul>
            <li>
              <Link to="/admin">Dashboard</Link>
            </li>
            <li>
              <Link to="/admin/documents">Gestión de Documentos</Link>
            </li>
            <li>
              <Link to="/admin/users">Gestión de Usuarios</Link>
            </li>
            <li>
              <Link to="/admin/roles">Asignación de Roles</Link>
            </li>
            <li>
              <Link to="/admin/settings">Configuración</Link>
            </li>
            <li className="logout-link">
              <button onClick={handleLogout}>Cerrar Sesión</button>
            </li>
          </ul>
        </nav>
      </div>
      <div className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard users={users} documents={documents} />} />
          <Route path="/users" element={<UserManagement users={users} handleDeleteUser={handleDeleteUser} />} />
          <Route path="/documents" element={<DocumentManagement documents={documents} handleDeleteDocument={handleDeleteDocument} />} />
          <Route path="/roles" element={<RoleManagement setShowRoleModal={setShowRoleModal} />} />
          <Route path="/settings" element={<div className="content-section"><h2>Configuración</h2><p>Opciones de configuración del sistema</p></div>} />
        </Routes>
      </div>

      {showRoleModal && (
        <div className="modal-backdrop">
          <div className="role-modal">
            <div className="modal-header">
              <h3>Asignación de Roles</h3>
              <button className="close-btn" onClick={() => setShowRoleModal(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Usuario:</label>
                <select>
                  <option value="">Seleccionar usuario</option>
                  {users.map(user => (
                    <option key={user.id} value={user.id}>{user.name}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Rol:</label>
                <select>
                  <option value="">Seleccionar rol</option>
                  <option value="admin">Administrador</option>
                  <option value="editor">Editor</option>
                  <option value="user">Usuario</option>
                </select>
              </div>
              <div className="form-group">
                <label>Permisos:</label>
                <div className="permission-item">
                  <input type="checkbox" id="read" />
                  <label htmlFor="read">Leer documentos</label>
                </div>
                <div className="permission-item">
                  <input type="checkbox" id="edit" />
                  <label htmlFor="edit">Editar documentos</label>
                </div>
                <div className="permission-item">
                  <input type="checkbox" id="manage" />
                  <label htmlFor="manage">Administrar usuarios</label>
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-save">Guardar</button>
              <button className="btn-cancel" onClick={() => setShowRoleModal(false)}>Cancelar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminPanel;