// frontend/src/components/ArticleForm.js
import React, { useState } from 'react';
import { Plus, Link, Loader2 } from 'lucide-react';
import { createArticle } from '../services/api';
import { toast } from 'react-toastify';

const ArticleForm = ({ onArticleCreated }) => {
  const [url, setUrl] = useState('');
  const [summaryType, setSummaryType] = useState('comprehensive');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!url.trim()) {
      toast.error('Please enter a valid URL');
      return;
    }

    try {
      setLoading(true);
      const articleData = {
        url: url.trim(),
        summary_type: summaryType
      };

      const newArticle = await createArticle(articleData);
      onArticleCreated(newArticle);
      setUrl('');
      setSummaryType('comprehensive');
    } catch (error) {
      toast.error(error.message || 'Failed to process article');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="article-form-container">
      <form onSubmit={handleSubmit} className="article-form">
        <div className="form-header">
          <Link className="form-icon" size={24} />
          <h3>Add New Article</h3>
        </div>

        <div className="form-group">
          <label htmlFor="url">Article URL</label>
          <input
            id="url"
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com/article"
            className="url-input"
            disabled={loading}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="summaryType">Summary Type</label>
          <select
            id="summaryType"
            value={summaryType}
            onChange={(e) => setSummaryType(e.target.value)}
            className="summary-select"
            disabled={loading}
          >
            <option value="brief">Brief (2-3 sentences)</option>
            <option value="comprehensive">Comprehensive (detailed)</option>
            <option value="detailed">Detailed (in-depth analysis)</option>
          </select>
        </div>

        <button
          type="submit"
          className={`submit-button ${loading ? 'loading' : ''}`}
          disabled={loading}
        >
          {loading ? (
            <>
              <Loader2 className="spinner" size={20} />
              Processing...
            </>
          ) : (
            <>
              <Plus size={20} />
              Summarize Article
            </>
          )}
        </button>
      </form>
    </div>
  );
};

export default ArticleForm;
