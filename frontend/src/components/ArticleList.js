// frontend/src/components/ArticleList.js
import React from 'react';
import { Link } from 'react-router-dom';
import { ExternalLink, Clock, FileText, Loader2 } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

const ArticleList = ({ articles, loading }) => {
  if (loading) {
    return (
      <div className="loading-container">
        <Loader2 className="spinner" size={32} />
        <p>Loading articles...</p>
      </div>
    );
  }

  if (!articles || articles.length === 0) {
    return (
      <div className="empty-state">
        <FileText size={48} className="empty-icon" />
        <h3>No articles yet</h3>
        <p>Add your first article URL above to get started with AI-powered summarization.</p>
      </div>
    );
  }

  return (
    <div className="articles-grid">
      {articles.map((article) => (
        <ArticleCard key={article.id} article={article} />
      ))}
    </div>
  );
};

const ArticleCard = ({ article }) => {
  const timeAgo = formatDistanceToNow(new Date(article.created_at), { addSuffix: true });
  
  return (
    <div className="article-card">
      <div className="article-header">
        <h4 className="article-title">
          <Link to={`/article/${article.id}`}>
            {article.title}
          </Link>
        </h4>
        <div className="article-meta">
          <span className="summary-type-badge">
            {article.summary_type}
          </span>
          <div className="article-time">
            <Clock size={14} />
            {timeAgo}
          </div>
        </div>
      </div>

      {article.summary && (
        <div className="article-summary">
          <p>{article.summary.summary_text.substring(0, 200)}...</p>
          
          {article.summary.key_points && article.summary.key_points.length > 0 && (
            <div className="key-points-preview">
              <span className="key-points-label">Key Points:</span>
              <ul className="key-points-list">
                {article.summary.key_points.slice(0, 2).map((point, index) => (
                  <li key={index}>{point}</li>
                ))}
                {article.summary.key_points.length > 2 && (
                  <li className="more-points">
                    +{article.summary.key_points.length - 2} more
                  </li>
                )}
              </ul>
            </div>
          )}
        </div>
      )}

      <div className="article-actions">
        <Link to={`/article/${article.id}`} className="view-button">
          View Full Summary
        </Link>
        <a 
          href={article.url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="external-link"
          title="Open original article"
        >
          <ExternalLink size={16} />
        </a>
      </div>
    </div>
  );
};

export default ArticleList;
