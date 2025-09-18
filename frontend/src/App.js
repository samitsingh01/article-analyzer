// frontend/src/App.js
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Components
import ArticleForm from './components/ArticleForm';
import ArticleList from './components/ArticleList';
import { ArticleDetail, SearchPage } from './components/OtherComponents';
import Navigation from './components/Navigation';

// Services
import { getArticles } from './services/api';

// Styles
import './App.css';

function App() {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(false);

  // Load articles on component mount
  useEffect(() => {
    loadArticles();
  }, []);

  const loadArticles = async () => {
    try {
      setLoading(true);
      const data = await getArticles();
      setArticles(data);
    } catch (err) {
      console.error('Error loading articles:', err);
      toast.error('Failed to load articles');
    } finally {
      setLoading(false);
    }
  };

  const handleArticleCreated = (newArticle) => {
    setArticles(prev => [newArticle, ...prev]);
    toast.success('Article summarized successfully!');
  };

  return (
    <Router>
      <div className="App">
        <Navigation />
        
        <main className="main-content">
          <Routes>
            <Route 
              path="/" 
              element={
                <HomePage 
                  onArticleCreated={handleArticleCreated}
                  articles={articles}
                  loading={loading}
                  onRefresh={loadArticles}
                />
              } 
            />
            <Route path="/article/:id" element={<ArticleDetail />} />
            <Route path="/search" element={<SearchPage />} />
          </Routes>
        </main>

        <ToastContainer
          position="top-right"
          autoClose={5000}
          hideProgressBar={false}
          newestOnTop={false}
          closeOnClick
          rtl={false}
          pauseOnFocusLoss
          draggable
          pauseOnHover
        />
      </div>
    </Router>
  );
}

// Home Page Component
function HomePage({ onArticleCreated, articles, loading, onRefresh }) {
  return (
    <div className="home-page">
      <div className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">
            Smart Article Summarizer
          </h1>
          <p className="hero-subtitle">
            Transform any article into intelligent summaries using AI-powered analysis
          </p>
        </div>
      </div>

      <div className="content-container">
        <div className="form-section">
          <ArticleForm onArticleCreated={onArticleCreated} />
        </div>

        <div className="articles-section">
          <div className="section-header">
            <h2>Recent Summaries</h2>
            <button 
              onClick={onRefresh}
              className="refresh-button"
              disabled={loading}
            >
              {loading ? 'Loading...' : 'Refresh'}
            </button>
          </div>
          
          <ArticleList articles={articles} loading={loading} />
        </div>
      </div>
    </div>
  );
}

export default App;
