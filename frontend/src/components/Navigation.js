// frontend/src/components/Navigation.js
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, Search, FileText } from 'lucide-react';

const Navigation = () => {
  const location = useLocation();

  return (
    <nav className="navigation">
      <div className="nav-container">
        <Link to="/" className="nav-brand">
          <FileText size={24} />
          Smart Summarizer
        </Link>
        
        <div className="nav-links">
          <Link 
            to="/" 
            className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
          >
            <Home size={18} />
            Home
          </Link>
          <Link 
            to="/search" 
            className={`nav-link ${location.pathname === '/search' ? 'active' : ''}`}
          >
            <Search size={18} />
            Search
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
