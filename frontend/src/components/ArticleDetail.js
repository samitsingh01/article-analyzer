import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, ExternalLink, Clock, Tag, Loader2 } from 'lucide-react';
import { getArticle } from '../services/api';
import { formatDistanceToNow } from 'date-fns';
import { toast } from 'react-toastify';

const ArticleDetail = () => {
  const { id } = useParams();
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadArticle();
  }, [id]);

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
          <a 
            href={article.url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="external-link-button"
          >
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
            <div className="summary-text">
              {article.summary.summary_text}
            </div>
            
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

