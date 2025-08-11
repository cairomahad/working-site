import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, useParams } from 'react-router-dom';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Маппинг категорий на русские названия
const CATEGORY_NAMES = {
  'aqidah': 'Вероучение',
  'ibadah': 'Поклонение',
  'muamalat': 'Взаимоотношения', 
  'akhlaq': 'Нравственность',
  'fiqh': 'Фикх',
  'hadith': 'Хадисы',
  'quran': 'Коран',
  'seerah': 'Жизнеописание Пророка',
  'general': 'Общие вопросы'
};

// Компонент категории
const CategoryCard = ({ category, onClick }) => {
  return (
    <div 
      onClick={() => onClick(category.id)}
      className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md cursor-pointer hover:border-teal-300"
    >
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {category.name}
          </h3>
          <p className="text-sm text-gray-600">
            {category.count} {category.count === 1 ? 'вопрос' : category.count < 5 ? 'вопроса' : 'вопросов'}
          </p>
        </div>
        <div className="text-teal-600">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </div>
      </div>
    </div>
  );
};

// Компонент карточки вопроса
const QuestionCard = ({ question, onClick, showCategory = true }) => {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div 
      onClick={() => onClick(question)}
      className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md cursor-pointer hover:border-teal-300"
    >
      <div className="mb-4">
        {showCategory && (
          <div className="flex items-center mb-2">
            <span className="inline-block bg-teal-100 text-teal-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
              {CATEGORY_NAMES[question.category] || question.category}
            </span>
          </div>
        )}
        <h3 className="text-lg font-semibold text-gray-900 mb-2 hover:text-teal-600">
          {question.title}
        </h3>
        <p className="text-gray-600 text-sm line-clamp-2">
          {question.question_text.substring(0, 150)}{question.question_text.length > 150 ? '...' : ''}
        </p>
      </div>
      
      <div className="flex items-center justify-between text-sm text-gray-500">
        <div className="flex items-center space-x-4">
          <span className="flex items-center">
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            {question.views_count}
          </span>
          <span>{question.imam_name}</span>
        </div>
        <span>{formatDate(question.created_at)}</span>
      </div>
      
      {question.tags && question.tags.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1">
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
  );
};

// Главная страница Q&A
export const QAMainPage = () => {
  const [categories, setCategories] = useState([]);
  const [featuredQuestions, setFeaturedQuestions] = useState([]);
  const [recentQuestions, setRecentQuestions] = useState([]);
  const [popularQuestions, setPopularQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [categoriesRes, featuredRes, recentRes, popularRes] = await Promise.all([
        axios.get(`${API}/qa/categories`),
        axios.get(`${API}/qa/featured?limit=3`),
        axios.get(`${API}/qa/recent?limit=6`),
        axios.get(`${API}/qa/popular?limit=6`)
      ]);

      setCategories(categoriesRes.data);
      setFeaturedQuestions(featuredRes.data);
      setRecentQuestions(recentRes.data);
      setPopularQuestions(popularRes.data);
    } catch (error) {
      console.error('Ошибка загрузки данных Q&A:', error);
    }
    setLoading(false);
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/qa/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const handleCategoryClick = (categoryId) => {
    navigate(`/qa/category/${categoryId}`);
  };

  const handleQuestionClick = (question) => {
    navigate(`/qa/question/${question.slug}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex justify-center items-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-br from-teal-600 to-teal-700 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold mb-4">Вопросы и Ответы</h1>
            <p className="text-xl text-teal-100 mb-8">
              Найдите ответы на ваши вопросы об исламе от знающих имамов
            </p>
            
            {/* Search Bar */}
            <form onSubmit={handleSearch} className="max-w-2xl mx-auto">
              <div className="relative">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Поиск по вопросам..."
                  className="w-full px-6 py-4 text-gray-900 rounded-lg shadow-lg focus:outline-none focus:ring-2 focus:ring-teal-300"
                />
                <button
                  type="submit"
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 bg-teal-600 text-white px-4 py-2 rounded-md hover:bg-teal-700"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Featured Questions */}
        {featuredQuestions.length > 0 && (
          <section className="mb-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Рекомендуемые вопросы</h2>
            <div className="grid gap-6 lg:grid-cols-3">
              {featuredQuestions.map((question) => (
                <QuestionCard 
                  key={question.id} 
                  question={question} 
                  onClick={handleQuestionClick} 
                />
              ))}
            </div>
          </section>
        )}

        {/* Categories */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Категории</h2>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {categories.map((category) => (
              <CategoryCard 
                key={category.id} 
                category={category} 
                onClick={handleCategoryClick} 
              />
            ))}
          </div>
        </section>

        <div className="grid gap-12 lg:grid-cols-2">
          {/* Recent Questions */}
          <section>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Последние вопросы</h2>
              <button
                onClick={() => navigate('/qa/recent')}
                className="text-teal-600 hover:text-teal-700 font-medium"
              >
                Показать все →
              </button>
            </div>
            <div className="space-y-4">
              {recentQuestions.map((question) => (
                <QuestionCard 
                  key={question.id} 
                  question={question} 
                  onClick={handleQuestionClick} 
                />
              ))}
            </div>
          </section>

          {/* Popular Questions */}
          <section>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Популярные вопросы</h2>
              <button
                onClick={() => navigate('/qa/popular')}
                className="text-teal-600 hover:text-teal-700 font-medium"
              >
                Показать все →
              </button>
            </div>
            <div className="space-y-4">
              {popularQuestions.map((question) => (
                <QuestionCard 
                  key={question.id} 
                  question={question} 
                  onClick={handleQuestionClick} 
                />
              ))}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};

// Страница категории
export const QACategoryPage = () => {
  const { categoryId } = useParams();
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const navigate = useNavigate();
  
  const questionsPerPage = 12;

  useEffect(() => {
    fetchQuestions();
  }, [categoryId, currentPage]);

  const fetchQuestions = async () => {
    try {
      const skip = (currentPage - 1) * questionsPerPage;
      const response = await axios.get(`${API}/qa/questions`, {
        params: {
          category: categoryId,
          limit: questionsPerPage,
          skip: skip
        }
      });
      
      if (currentPage === 1) {
        setQuestions(response.data);
      } else {
        setQuestions(prev => [...prev, ...response.data]);
      }
      
      setHasMore(response.data.length === questionsPerPage);
    } catch (error) {
      console.error('Ошибка загрузки вопросов:', error);
    }
    setLoading(false);
  };

  const loadMore = () => {
    setCurrentPage(prev => prev + 1);
  };

  const handleQuestionClick = (question) => {
    navigate(`/qa/question/${question.slug}`);
  };

  if (loading && currentPage === 1) {
    return (
      <div className="min-h-screen bg-gray-50 flex justify-center items-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
      </div>
    );
  }

  const categoryName = CATEGORY_NAMES[categoryId] || categoryId;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-between">
            <div>
              <button
                onClick={() => navigate('/qa')}
                className="text-teal-600 hover:text-teal-700 flex items-center mb-4"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                Вернуться к категориям
              </button>
              <h1 className="text-3xl font-bold text-gray-900">{categoryName}</h1>
              <p className="text-gray-600 mt-2">
                {questions.length} {questions.length === 1 ? 'вопрос' : questions.length < 5 ? 'вопроса' : 'вопросов'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Questions List */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {questions.length > 0 ? (
          <>
            <div className="grid gap-6 lg:grid-cols-2">
              {questions.map((question) => (
                <QuestionCard 
                  key={question.id} 
                  question={question} 
                  onClick={handleQuestionClick}
                  showCategory={false}
                />
              ))}
            </div>
            
            {hasMore && (
              <div className="text-center mt-8">
                <button
                  onClick={loadMore}
                  disabled={loading}
                  className="bg-teal-600 text-white px-6 py-3 rounded-lg hover:bg-teal-700 disabled:opacity-50"
                >
                  {loading ? 'Загрузка...' : 'Показать еще'}
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-12">
            <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Вопросов не найдено</h3>
            <p className="text-gray-600">В этой категории пока нет вопросов.</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Страница конкретного вопроса
export const QAQuestionPage = () => {
  const { slug } = useParams();
  const [question, setQuestion] = useState(null);
  const [relatedQuestions, setRelatedQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchQuestion();
  }, [slug]);

  const fetchQuestion = async () => {
    try {
      const response = await axios.get(`${API}/qa/questions/slug/${slug}`);
      setQuestion(response.data);
      
      // Получить связанные вопросы той же категории
      const relatedResponse = await axios.get(`${API}/qa/questions`, {
        params: {
          category: response.data.category,
          limit: 4
        }
      });
      
      // Исключить текущий вопрос из связанных
      const filtered = relatedResponse.data.filter(q => q.id !== response.data.id);
      setRelatedQuestions(filtered);
    } catch (error) {
      console.error('Ошибка загрузки вопроса:', error);
    }
    setLoading(false);
  };

  const handleQuestionClick = (question) => {
    navigate(`/qa/question/${question.slug}`);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long', 
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex justify-center items-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
      </div>
    );
  }

  if (!question) {
    return (
      <div className="min-h-screen bg-gray-50 flex justify-center items-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Вопрос не найден</h2>
          <button
            onClick={() => navigate('/qa')}
            className="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700"
          >
            Вернуться к вопросам
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Navigation */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/qa')}
            className="text-teal-600 hover:text-teal-700 flex items-center mb-4"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Все вопросы
          </button>
          
          <div className="flex items-center text-sm text-gray-600 mb-4">
            <span>{CATEGORY_NAMES[question.category] || question.category}</span>
            <span className="mx-2">•</span>
            <span>{formatDate(question.created_at)}</span>
            <span className="mx-2">•</span>
            <span className="flex items-center">
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              {question.views_count} просмотров
            </span>
          </div>
        </div>

        {/* Question */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-8">
          <div className="p-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-6">
              {question.title}
            </h1>
            
            <div className="mb-8">
              <h2 className="text-lg font-semibold text-gray-900 mb-3">Вопрос:</h2>
              <div className="prose prose-gray max-w-none">
                <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                  {question.question_text}
                </p>
              </div>
            </div>

            <div className="border-t border-gray-200 pt-8">
              <div className="flex items-center mb-4">
                <div className="flex-shrink-0 w-10 h-10 bg-teal-100 rounded-full flex items-center justify-center">
                  <span className="text-teal-600 font-semibold text-sm">
                    {question.imam_name.charAt(0)}
                  </span>
                </div>
                <div className="ml-3">
                  <h3 className="text-lg font-semibold text-gray-900">Ответ от {question.imam_name}</h3>
                </div>
              </div>
              
              <div className="prose prose-gray max-w-none">
                <div className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                  {question.answer_text}
                </div>
              </div>
            </div>

            {/* References */}
            {question.references && question.references.length > 0 && (
              <div className="mt-8 p-4 bg-teal-50 rounded-lg border border-teal-200">
                <h4 className="font-semibold text-teal-900 mb-2">Источники:</h4>
                <ul className="text-sm text-teal-800 space-y-1">
                  {question.references.map((ref, index) => (
                    <li key={index}>• {ref}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Tags */}
            {question.tags && question.tags.length > 0 && (
              <div className="mt-6 flex flex-wrap gap-2">
                {question.tags.map((tag, index) => (
                  <span 
                    key={index}
                    className="inline-block bg-gray-100 text-gray-700 text-sm px-3 py-1 rounded-full"
                  >
                    #{tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Related Questions */}
        {relatedQuestions.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold text-gray-900">Похожие вопросы</h2>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {relatedQuestions.map((relatedQuestion) => (
                  <div
                    key={relatedQuestion.id}
                    onClick={() => handleQuestionClick(relatedQuestion)}
                    className="p-4 border border-gray-200 rounded-lg hover:shadow-md  cursor-pointer hover:border-teal-300"
                  >
                    <h3 className="font-semibold text-gray-900 mb-2 hover:text-teal-600 ">
                      {relatedQuestion.title}
                    </h3>
                    <p className="text-sm text-gray-600 line-clamp-2">
                      {relatedQuestion.question_text.substring(0, 100)}...
                    </p>
                    <div className="flex items-center mt-2 text-xs text-gray-500">
                      <span className="flex items-center">
                        <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                        {relatedQuestion.views_count}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Форма задать вопрос
export const AskQuestionForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    category: 'general',
    title: '',
    question_text: ''
  });
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Здесь можно добавить API endpoint для отправки вопросов пользователей
      // Пока что просто имитируем отправку
      console.log('Вопрос отправлен:', formData);
      
      // Имитация задержки отправки
      setTimeout(() => {
        setSubmitted(true);
        setLoading(false);
      }, 1000);
      
    } catch (error) {
      console.error('Ошибка отправки вопроса:', error);
      alert('Ошибка отправки вопроса. Попробуйте еще раз.');
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Вопрос отправлен!</h2>
            <p className="text-gray-600 mb-6">
              Спасибо за ваш вопрос. Он будет рассмотрен нашими имамами, и ответ появится в разделе "Вопросы и Ответы".
            </p>
            <div className="space-x-3">
              <button
                onClick={() => navigate('/qa')}
                className="bg-teal-600 text-white px-6 py-2 rounded-lg hover:bg-teal-700 "
              >
                Перейти к Q&A
              </button>
              <button
                onClick={() => {
                  setSubmitted(false);
                  setFormData({
                    name: '',
                    email: '',
                    category: 'general',
                    title: '',
                    question_text: ''
                  });
                }}
                className="text-teal-600 hover:text-teal-700 px-6 py-2 border border-teal-600 rounded-lg hover:bg-teal-50 "
              >
                Задать еще вопрос
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-br from-teal-600 to-teal-700 text-white py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-3xl font-bold mb-4">Задать вопрос</h1>
          <p className="text-xl text-teal-100">
            Получите ответ от знающих имамов на ваши вопросы об исламе
          </p>
        </div>
      </div>

      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Имя */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Ваше имя *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                required
              />
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email (для уведомлений) *
              </label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                required
              />
            </div>

            {/* Категория */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Категория вопроса *
              </label>
              <select
                value={formData.category}
                onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                required
              >
                <option value="general">Общие вопросы</option>
                <option value="aqidah">Вероучение</option>
                <option value="ibadah">Поклонение</option>
                <option value="muamalat">Взаимоотношения</option>
                <option value="akhlaq">Нравственность</option>
                <option value="fiqh">Фикх</option>
                <option value="hadith">Хадисы</option>
                <option value="quran">Коран</option>
                <option value="seerah">Жизнеописание Пророка</option>
              </select>
            </div>

            {/* Заголовок */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Краткое описание вопроса *
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                placeholder="Например: Как правильно совершать намаз?"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                required
              />
            </div>

            {/* Текст вопроса */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Подробное описание вопроса *
              </label>
              <textarea
                value={formData.question_text}
                onChange={(e) => setFormData(prev => ({ ...prev, question_text: e.target.value }))}
                rows={6}
                placeholder="Опишите ваш вопрос подробно. Чем детальнее вы опишете ситуацию, тем более точный ответ сможет дать имам."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                required
              />
            </div>

            {/* Информация */}
            <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-start">
                <svg className="w-5 h-5 text-blue-600 mt-0.5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div className="text-sm text-blue-800">
                  <p className="font-medium mb-1">Пожалуйста, учтите:</p>
                  <ul className="list-disc list-inside space-y-1">
                    <li>Ответ может занять от нескольких дней до недели</li>
                    <li>Мы отвечаем только на вопросы, связанные с исламом</li>
                    <li>Вопрос будет проверен модератором перед публикацией</li>
                    <li>Ответ будет опубликован в разделе Q&A для всех пользователей</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Кнопки */}
            <div className="flex justify-end space-x-3 pt-6">
              <button
                type="button"
                onClick={() => navigate('/qa')}
                className="px-6 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 "
              >
                Отмена
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700  disabled:opacity-50"
              >
                {loading ? 'Отправка...' : 'Отправить вопрос'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

// Страница поиска
export const QASearchPage = () => {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const query = params.get('q') || '';
    setSearchQuery(query);
    
    if (query) {
      fetchSearchResults(query);
    } else {
      setLoading(false);
    }
  }, []);

  const fetchSearchResults = async (query) => {
    try {
      const response = await axios.get(`${API}/qa/questions`, {
        params: {
          search: query,
          limit: 20
        }
      });
      setQuestions(response.data);
    } catch (error) {
      console.error('Ошибка поиска:', error);
    }
    setLoading(false);
  };

  const handleQuestionClick = (question) => {
    navigate(`/qa/question/${question.slug}`);
  };

  const handleNewSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/qa/search?q=${encodeURIComponent(searchQuery.trim())}`);
      fetchSearchResults(searchQuery.trim());
      setLoading(true);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex justify-center items-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <button
            onClick={() => navigate('/qa')}
            className="text-teal-600 hover:text-teal-700 flex items-center mb-4"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Все вопросы
          </button>
          
          <h1 className="text-3xl font-bold text-gray-900 mb-6">Поиск вопросов</h1>
          
          {/* Search Form */}
          <form onSubmit={handleNewSearch} className="max-w-2xl">
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Поиск по вопросам..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              />
              <button
                type="submit"
                className="absolute right-3 top-1/2 transform -translate-y-1/2 bg-teal-600 text-white px-4 py-2 rounded-md hover:bg-teal-700 "
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </button>
            </div>
          </form>
          
          {searchQuery && (
            <p className="text-gray-600 mt-4">
              Результаты поиска для "{searchQuery}": найдено {questions.length} {questions.length === 1 ? 'вопрос' : questions.length < 5 ? 'вопроса' : 'вопросов'}
            </p>
          )}
        </div>
      </div>

      {/* Results */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {questions.length > 0 ? (
          <div className="grid gap-6 lg:grid-cols-2">
            {questions.map((question) => (
              <QuestionCard 
                key={question.id} 
                question={question} 
                onClick={handleQuestionClick} 
              />
            ))}
          </div>
        ) : searchQuery ? (
          <div className="text-center py-12">
            <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Ничего не найдено</h3>
            <p className="text-gray-600">Попробуйте изменить поисковый запрос.</p>
          </div>
        ) : (
          <div className="text-center py-12">
            <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Введите поисковый запрос</h3>
            <p className="text-gray-600">Начните поиск, чтобы найти ответы на ваши вопросы.</p>
          </div>
        )}
      </div>
    </div>
  );
};