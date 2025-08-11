import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Маппинг категорий
const CATEGORY_OPTIONS = [
  { value: 'aqidah', label: 'Вероучение' },
  { value: 'ibadah', label: 'Поклонение' },
  { value: 'muamalat', label: 'Взаимоотношения' },
  { value: 'akhlaq', label: 'Нравственность' },
  { value: 'fiqh', label: 'Фикх' },
  { value: 'hadith', label: 'Хадисы' },
  { value: 'quran', label: 'Коран' },
  { value: 'seerah', label: 'Жизнеописание Пророка' },
  { value: 'general', label: 'Общие вопросы' }
];

// Форма создания/редактирования вопроса
const QAQuestionForm = ({ question, onSave, onCancel, token }) => {
  const [formData, setFormData] = useState({
    title: '',
    question_text: '',
    answer_text: '',
    category: 'general',
    tags: [],
    is_featured: false,
    imam_name: 'Имам',
    references: []
  });
  const [newTag, setNewTag] = useState('');
  const [newReference, setNewReference] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (question) {
      setFormData({
        title: question.title || '',
        question_text: question.question_text || '',
        answer_text: question.answer_text || '',
        category: question.category || 'general',
        tags: question.tags || [],
        is_featured: question.is_featured || false,
        imam_name: question.imam_name || 'Имам',
        references: question.references || []
      });
    }
  }, [question]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const endpoint = question 
        ? `${API}/admin/qa/questions/${question.id}`
        : `${API}/admin/qa/questions`;
      
      const method = question ? 'PUT' : 'POST';
      
      const response = await axios({
        method,
        url: endpoint,
        data: formData,
        headers: { Authorization: `Bearer ${token}` }
      });

      onSave(response.data);
    } catch (error) {
      console.error('Ошибка сохранения:', error);
      alert('Ошибка сохранения вопроса');
    }
    setLoading(false);
  };

  const addTag = () => {
    if (newTag.trim() && !formData.tags.includes(newTag.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, newTag.trim()]
      }));
      setNewTag('');
    }
  };

  const removeTag = (index) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter((_, i) => i !== index)
    }));
  };

  const addReference = () => {
    if (newReference.trim() && !formData.references.includes(newReference.trim())) {
      setFormData(prev => ({
        ...prev,
        references: [...prev.references, newReference.trim()]
      }));
      setNewReference('');
    }
  };

  const removeReference = (index) => {
    setFormData(prev => ({
      ...prev,
      references: prev.references.filter((_, i) => i !== index)
    }));
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">
        {question ? 'Редактировать вопрос' : 'Создать новый вопрос'}
      </h3>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Заголовок */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Заголовок вопроса *
          </label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
            required
          />
        </div>

        {/* Категория */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Категория *
          </label>
          <select
            value={formData.category}
            onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
            required
          >
            {CATEGORY_OPTIONS.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Текст вопроса */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Текст вопроса *
          </label>
          <textarea
            value={formData.question_text}
            onChange={(e) => setFormData(prev => ({ ...prev, question_text: e.target.value }))}
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
            required
          />
        </div>

        {/* Ответ */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Ответ *
          </label>
          <textarea
            value={formData.answer_text}
            onChange={(e) => setFormData(prev => ({ ...prev, answer_text: e.target.value }))}
            rows={8}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
            required
          />
        </div>

        {/* Имя имама */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Имя отвечающего
          </label>
          <input
            type="text"
            value={formData.imam_name}
            onChange={(e) => setFormData(prev => ({ ...prev, imam_name: e.target.value }))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
          />
        </div>

        {/* Теги */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Теги
          </label>
          <div className="flex gap-2 mb-2">
            <input
              type="text"
              value={newTag}
              onChange={(e) => setNewTag(e.target.value)}
              placeholder="Добавить тег"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
            />
            <button
              type="button"
              onClick={addTag}
              className="px-4 py-2 bg-teal-600 text-white rounded-md hover:bg-teal-700"
            >
              Добавить
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {formData.tags.map((tag, index) => (
              <span
                key={index}
                className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-gray-100 text-gray-800"
              >
                #{tag}
                <button
                  type="button"
                  onClick={() => removeTag(index)}
                  className="ml-2 text-gray-500 hover:text-red-500"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* Источники */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Источники (Коран, Хадисы)
          </label>
          <div className="flex gap-2 mb-2">
            <input
              type="text"
              value={newReference}
              onChange={(e) => setNewReference(e.target.value)}
              placeholder="Например: Коран 2:43"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addReference())}
            />
            <button
              type="button"
              onClick={addReference}
              className="px-4 py-2 bg-teal-600 text-white rounded-md hover:bg-teal-700"
            >
              Добавить
            </button>
          </div>
          <div className="space-y-1">
            {formData.references.map((ref, index) => (
              <div
                key={index}
                className="flex items-center justify-between px-3 py-2 bg-teal-50 rounded-md"
              >
                <span className="text-sm">{ref}</span>
                <button
                  type="button"
                  onClick={() => removeReference(index)}
                  className="text-red-500 hover:text-red-700"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Рекомендуемый вопрос */}
        <div>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={formData.is_featured}
              onChange={(e) => setFormData(prev => ({ ...prev, is_featured: e.target.checked }))}
              className="mr-2"
            />
            <span className="text-sm font-medium text-gray-700">
              Рекомендуемый вопрос
            </span>
          </label>
        </div>

        {/* Кнопки */}
        <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Отмена
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 bg-teal-600 text-white rounded-md hover:bg-teal-700 disabled:opacity-50"
          >
            {loading ? 'Сохранение...' : 'Сохранить'}
          </button>
        </div>
      </form>
    </div>
  );
};

// Основной компонент управления Q&A
export const QAManagement = () => {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingQuestion, setEditingQuestion] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [stats, setStats] = useState(null);

  const token = localStorage.getItem('userToken');

  useEffect(() => {
    fetchQuestions();
    fetchStats();
  }, [selectedCategory, searchQuery]);

  const fetchQuestions = async () => {
    try {
      const params = {};
      if (selectedCategory) params.category = selectedCategory;
      if (searchQuery) params.search = searchQuery;

      const response = await axios.get(`${API}/admin/qa/questions`, {
        headers: { Authorization: `Bearer ${token}` },
        params
      });
      setQuestions(response.data);
    } catch (error) {
      console.error('Ошибка загрузки вопросов:', error);
    }
    setLoading(false);
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/qa/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Ошибка загрузки статистики:', error);
    }
  };

  const handleSave = (savedQuestion) => {
    if (editingQuestion) {
      setQuestions(prev => prev.map(q => q.id === savedQuestion.id ? savedQuestion : q));
    } else {
      setQuestions(prev => [savedQuestion, ...prev]);
    }
    setShowForm(false);
    setEditingQuestion(null);
    fetchStats();
  };

  const handleEdit = (question) => {
    setEditingQuestion(question);
    setShowForm(true);
  };

  const handleDelete = async (questionId) => {
    if (!window.confirm('Вы уверены, что хотите удалить этот вопрос?')) {
      return;
    }

    try {
      await axios.delete(`${API}/admin/qa/questions/${questionId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setQuestions(prev => prev.filter(q => q.id !== questionId));
      fetchStats();
    } catch (error) {
      console.error('Ошибка удаления:', error);
      alert('Ошибка удаления вопроса');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('ru-RU');
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
      </div>
    );
  }

  if (showForm) {
    return (
      <QAQuestionForm
        question={editingQuestion}
        onSave={handleSave}
        onCancel={() => {
          setShowForm(false);
          setEditingQuestion(null);
        }}
        token={token}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Управление Q&A</h1>
          <p className="text-gray-600">Вопросы и ответы имама</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700 "
        >
          Добавить вопрос
        </button>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h3 className="text-sm font-medium text-gray-500">Всего вопросов</h3>
            <p className="text-2xl font-bold text-gray-900">{stats.total_questions}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h3 className="text-sm font-medium text-gray-500">Рекомендуемые</h3>
            <p className="text-2xl font-bold text-gray-900">{stats.featured_count}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h3 className="text-sm font-medium text-gray-500">Просмотры</h3>
            <p className="text-2xl font-bold text-gray-900">{stats.total_views}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h3 className="text-sm font-medium text-gray-500">Категории</h3>
            <p className="text-2xl font-bold text-gray-900">{Object.keys(stats.questions_by_category).length}</p>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Поиск
            </label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Поиск по заголовку или тексту..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Категория
            </label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
            >
              <option value="">Все категории</option>
              {CATEGORY_OPTIONS.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Questions List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            Вопросы ({questions.length})
          </h2>
        </div>
        
        <div className="divide-y divide-gray-200">
          {questions.map((question) => (
            <div key={question.id} className="p-6">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-medium text-gray-900">
                      {question.title}
                    </h3>
                    {question.is_featured && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                        ⭐ Рекомендуемый
                      </span>
                    )}
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-teal-100 text-teal-800">
                      {CATEGORY_OPTIONS.find(c => c.value === question.category)?.label || question.category}
                    </span>
                  </div>
                  
                  <p className="text-gray-600 mb-3 line-clamp-2">
                    {question.question_text.substring(0, 150)}...
                  </p>
                  
                  <div className="flex items-center text-sm text-gray-500 space-x-4">
                    <span>👁 {question.views_count} просмотров</span>
                    <span>👤 {question.imam_name}</span>
                    <span>📅 {formatDate(question.created_at)}</span>
                  </div>
                  
                  {question.tags && question.tags.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {question.tags.slice(0, 3).map((tag, index) => (
                        <span 
                          key={index}
                          className="inline-block bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded-full"
                        >
                          #{tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                
                <div className="flex items-center space-x-2 ml-4">
                  <button
                    onClick={() => handleEdit(question)}
                    className="p-2 text-teal-600 hover:bg-teal-50 rounded-md "
                    title="Редактировать"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    onClick={() => handleDelete(question.id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-md "
                    title="Удалить"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          ))}
          
          {questions.length === 0 && (
            <div className="p-12 text-center">
              <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Вопросов не найдено</h3>
              <p className="text-gray-600">Создайте первый вопрос, чтобы начать.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default QAManagement;