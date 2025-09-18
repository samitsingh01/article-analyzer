import React, { useState } from 'react';
import { Search, Loader2, FileText } from 'lucide-react';
import { Link } from 'react-router-dom';
import { searchArticles } from '../services/api';
import { toast } from 'react-toastify';

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
            <button
              type="submit"
              className="search-button"
              disabled={loading || !query.trim()}
            >
              {loading ? (
                <Loader2 className="spinner" size={20} />
              ) : (
                'Search'
              )}
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
                  <SearchResultCard key={index} result={result} />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const SearchResultCard = ({ result }) => {
  return (
    <div className="search-result-card">
      <div className="result-header">
        <h3 className="result-title">
          <Link to={`/article/${result.article_id}`}>
            {result.title}
          </Link>
        </h3>
        <div className="similarity-score">
          {Math.round(result.similarity_score * 100)}% match
        </div>
      </div>
      
      <p className="result-excerpt">{result.summary_excerpt}</p>
      
      <div className="result-footer">
        <span className="result-type">{result.metadata.summary_type}</span>
        <Link to={`/article/${result.article_id}`} className="view-link">
          View Article
        </Link>
      </div>
    </div>
  );
};

export default Navigation;
export { ArticleDetail, SearchPage };
