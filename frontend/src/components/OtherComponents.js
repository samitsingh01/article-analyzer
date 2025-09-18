
import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, ExternalLink, Clock, Tag, Loader2, Search, FileText } from 'lucide-react';
import { getArticle, searchArticles } from '../services/api';
import { formatDistanceToNow } from 'date-fns';
import { toast } from 'react-toastify';

const ArticleDetail = () => {
  const { id } = useParams();
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadArticle = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getArticle(id);
      setArticle(data);
    } catch (err) {
      console.error('Error loading article:', err);
      setError(err.message);
      toast.error('Failed to load article');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadArticle();
  }, [id]);

  if (loading) {
    return (
      <div className="article-detail loading">
        <Loader2 className="spinner" size={32} />
        <p>Loading article...</p>
      </div>
    );
  }

  if (error || !article) {
    return (
      <div className="article-detail error">
        <h2>Article not found</h2>
        <p>{error || 'The requested article could not be found.'}</p>
        <Link to="/" className="back-button">
          <ArrowLeft size={18} />
          Back to Home
        </Link>
      </div>
    );
  }

  const timeAgo = formatDistanceToNow(new Date(article.created_at), { addSuffix: true });

  return (
    <div className="article-detail">
      <div className="article-header">
        <Link to="/" className="back-button">
          <ArrowLeft size={18} />
          Back to Articles
        </Link>
        <div className="article-meta">
          <div className="meta-item">
            <Clock size={16} />
            {timeAgo}
          </div>
          <div className="meta-item">
            <Tag size={16} />
            {article.summary_type}
          </div>
          <a href={article.url} target="_blank" rel="noopener noreferrer" className="external-link-button">
            <ExternalLink size={16} />
            Original Article
          </a>
        </div>
      </div>
      <div className="article-content">
        <h1 className="article-title">{article.title}</h1>
        {article.summary && (
          <div className="summary-section">
            <h2>Summary</h2>
            <div className="summary-text">{article.summary.summary_text}</div>
            {article.summary.key_points && article.summary.key_points.length > 0 && (
              <div className="key-points-section">
                <h3>Key Points</h3>
                <ul className="key-points">
                  {article.summary.key_points.map((point, index) => (
                    <li key={index}>{point}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

const SearchPage = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) {
      toast.error('Please enter a search query');
      return;
    }

    try {
      setLoading(true);
      const data = await searchArticles(query.trim(), 10);
      setResults(data.results || []);
      setHasSearched(true);
    } catch (error) {
      console.error('Search error:', error);
      toast.error('Search failed');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="search-page">
      <div className="search-container">
        <div className="search-header">
          <h1>Search Articles</h1>
          <p>Find relevant articles using AI-powered semantic search</p>
        </div>
        <form onSubmit={handleSearch} className="search-form">
          <div className="search-input-container">
            <Search className="search-icon" size={20} />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search for topics, keywords, or concepts..."
              className="search-input"
              disabled={loading}
            />
            <button type="submit" className="search-button" disabled={loading || !query.trim()}>
              {loading ? <Loader2 className="spinner" size={20} /> : 'Search'}
            </button>
          </div>
        </form>
        <div className="search-results">
          {loading && (
            <div className="loading-container">
              <Loader2 className="spinner" size={32} />
              <p>Searching articles...</p>
            </div>
          )}
          {!loading && hasSearched && results.length === 0 && (
            <div className="no-results">
              <FileText size={48} className="no-results-icon" />
              <h3>No results found</h3>
              <p>Try different keywords or check your spelling.</p>
            </div>
          )}
          {!loading && results.length > 0 && (
            <div className="results-container">
              <h2>Search Results ({results.length})</h2>
              <div className="results-list">
                {results.map((result, index) => (
                  <div key={index} className="search-result-card">
                    <div className="result-header">
                      <h3 className="result-title">
                        <Link to={`/article/${result.article_id}`}>{result.title}</Link>
                      </h3>
                      <div className="similarity-score">
                        {Math.round(result.similarity_score * 100)}% match
                      </div>
                    </div>
                    <p className="result-excerpt">{result.summary_excerpt}</p>
                    <div className="result-footer">
                      <span className="result-type">{result.metadata.summary_type}</span>
                      <Link to={`/article/${result.article_id}`} className="view-link">View Article</Link>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export { ArticleDetail, SearchPage };
