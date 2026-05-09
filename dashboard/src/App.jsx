import React, { useState } from 'react';
import Landing from './Landing';
import Login from './Login';
import DashboardView from './DashboardView';

function App() {
  const [currentView, setCurrentView] = useState('landing'); // 'landing', 'login', 'dashboard'

  const navigateToLogin = () => setCurrentView('login');
  const navigateToDashboard = () => setCurrentView('dashboard');
  const navigateToLanding = () => setCurrentView('landing');

  return (
    <div className="app-container">
      {currentView === 'landing' && <Landing onLoginClick={navigateToLogin} />}
      {currentView === 'login' && <Login onLoginSuccess={navigateToDashboard} />}
      {currentView === 'dashboard' && <DashboardView onLogout={navigateToLanding} />}
    </div>
  );
}

export default App;
