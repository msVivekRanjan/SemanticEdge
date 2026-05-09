import React, { useState } from 'react';

function Login({ onLoginSuccess }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = (e) => {
    e.preventDefault();
    if (email === 'admin@semanticedge.com' && password === 'admin') {
      onLoginSuccess();
    } else {
      setError('Invalid credentials. Hint: use admin@semanticedge.com / admin');
    }
  };

  return (
    <div className="login-page">
      <div className="login-card glass">
        <h2 className="headline-md" style={{fontSize: '28px', marginBottom: '8px'}}>Operator Portal Access</h2>
        <p className="subtitle body-md">Secure SemanticEdge 5G Analytics</p>
        
        <form onSubmit={handleLogin} className="login-form">
          <div className="input-group">
            <label className="label-caps">Email</label>
            <input 
              type="email" 
              placeholder="admin@semanticedge.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required 
            />
          </div>
          <div className="input-group">
            <label className="label-caps">Password</label>
            <input 
              type="password" 
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required 
            />
          </div>
          {error && <div className="error-msg">{error}</div>}
          <button type="submit" className="btn-primary w-full">Authenticate</button>
        </form>
      </div>
    </div>
  );
}

export default Login;
