import React, { useState, useEffect } from 'react';
import axios from 'axios';

// Компонент для ввода промокода
export const PromocodeEntry = ({ onSuccess, onClose }) => {
  const [promocode, setPromocode] = useState('');
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [promocodeInfo, setPromocodeInfo] = useState(null);

  const handlePromocodeChange = async (code) => {
    setPromocode(code);
    setError('');
    
    if (code.trim().length >= 3) {
      try {
        const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/promocodes/info/${code.trim()}`);
        setPromocodeInfo(response.data);
      } catch (error) {
        setPromocodeInfo(null);
      }
    } else {
      setPromocodeInfo(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!promocode.trim() || !email.trim()) {
      setError('Пожалуйста, заполните все поля');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${process.env.REACT_APP_BACKEND_URL}/api/promocodes/validate`, {
        code: promocode.trim(),
        student_email: email.trim()
      });

      if (response.data.success) {
        onSuccess(response.data);
      }
    } catch (error) {
      setError(error.response?.data?.detail || 'Ошибка при активации промокода');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-emerald-600 to-emerald-700 p-6 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-white">🎫 Активация промокода</h2>
            <button 
              onClick={onClose}
              className="text-white hover:text-emerald-200 text-2xl font-bold"
            >
              ×
            </button>
          </div>
          <p className="text-emerald-100 mt-2">Введите ваш промокод для получения доступа к курсам</p>
        </div>

        {/* Content */}
        <div className="p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Promocode Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Промокод
              </label>
              <input
                type="text"
                value={promocode}
                onChange={(e) => handlePromocodeChange(e.target.value.toUpperCase())}
                placeholder="Введите промокод (например: ШАМИЛЬ)"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-center text-lg font-bold tracking-widest"
                maxLength={20}
              />
            </div>

            {/* Promocode Info */}
            {promocodeInfo && (
              <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <span className="text-emerald-600 text-lg">✅</span>
                  <span className="ml-2 font-semibold text-emerald-800">Промокод найден!</span>
                </div>
                <p className="text-emerald-700 text-sm mb-2">{promocodeInfo.description}</p>
                {promocodeInfo.price_rub && (
                  <p className="text-emerald-600 font-bold">Стоимость: {promocodeInfo.price_rub} ₽</p>
                )}
                {promocodeInfo.courses && promocodeInfo.courses.length > 0 && (
                  <div className="mt-2">
                    <p className="text-sm font-medium text-emerald-700">Доступные курсы:</p>
                    <ul className="text-sm text-emerald-600 mt-1">
                      {promocodeInfo.courses.slice(0, 3).map((course, index) => (
                        <li key={index}>• {course.title}</li>
                      ))}
                      {promocodeInfo.courses.length > 3 && (
                        <li>• и еще {promocodeInfo.courses.length - 3} курсов...</li>
                      )}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Email Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Ваш email для доступа к курсам"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                required
              />
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading || !promocode.trim() || !email.trim()}
              className="w-full bg-gradient-to-r from-emerald-600 to-emerald-700 text-white py-3 px-6 rounded-lg font-semibold hover:from-emerald-700 hover:to-emerald-800  duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Активация...
                </span>
              ) : (
                'Активировать промокод'
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

// Компонент с информацией о покупке промокода
export const PromocodePromo = ({ onOpenEntry, onContactAdmin }) => {
  return (
    <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-2xl p-8 shadow-lg border border-emerald-200">
      {/* Header */}
      <div className="text-center mb-6">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-emerald-500 to-emerald-600 rounded-full mb-4">
          <span className="text-3xl">🎫</span>
        </div>
        <h3 className="text-2xl font-bold text-gray-800 mb-2">Полный доступ ко всем курсам</h3>
        <p className="text-gray-600">Получите неограниченный доступ ко всей библиотеке курсов по исламу</p>
      </div>

      {/* Features */}
      <div className="space-y-3 mb-6">
        <div className="flex items-center">
          <span className="text-emerald-600 mr-3">✅</span>
          <span className="text-gray-700">Доступ ко всем курсам платформы</span>
        </div>
        <div className="flex items-center">
          <span className="text-emerald-600 mr-3">✅</span>
          <span className="text-gray-700">Все тесты и интерактивные материалы</span>
        </div>
        <div className="flex items-center">
          <span className="text-emerald-600 mr-3">✅</span>
          <span className="text-gray-700">Дополнительные файлы и конспекты</span>
        </div>
        <div className="flex items-center">
          <span className="text-emerald-600 mr-3">✅</span>
          <span className="text-gray-700">Пожизненный доступ</span>
        </div>
        <div className="flex items-center">
          <span className="text-emerald-600 mr-3">✅</span>
          <span className="text-gray-700">Новые курсы добавляются бесплатно</span>
        </div>
      </div>

      {/* Price */}
      <div className="bg-white rounded-xl p-6 mb-6 border-2 border-emerald-200">
        <div className="text-center">
          <div className="flex items-center justify-center mb-2">
            <span className="text-4xl font-bold text-emerald-600">4900</span>
            <span className="text-2xl text-emerald-600 ml-1">₽</span>
          </div>
          <p className="text-gray-600 text-sm">Единовременный платеж</p>
          <p className="text-emerald-600 font-semibold mt-1">Промокод: ШАМИЛЬ</p>
        </div>
      </div>

      {/* Buttons */}
      <div className="space-y-3">
        <button
          onClick={onOpenEntry}
          className="w-full bg-gradient-to-r from-emerald-600 to-emerald-700 text-white py-4 px-6 rounded-xl font-semibold hover:from-emerald-700 hover:to-emerald-800  duration-200 transform hover:scale-105"
        >
          📝 У меня есть промокод
        </button>
        
        <button
          onClick={onContactAdmin}
          className="w-full bg-white text-emerald-700 py-4 px-6 rounded-xl font-semibold border-2 border-emerald-200 hover:bg-emerald-50  duration-200"
        >
          💬 Купить промокод
        </button>
      </div>

      {/* Contact Info */}
      <div className="mt-6 p-4 bg-emerald-500 bg-opacity-10 rounded-lg">
        <div className="text-center">
          <p className="text-emerald-800 font-semibold mb-1">📞 Связь с администратором</p>
          <p className="text-emerald-700 text-sm">Для покупки промокода свяжитесь с нами</p>
        </div>
      </div>
    </div>
  );
};

// Компонент успешной активации
export const PromocodeSuccess = ({ data, onClose, onViewCourses }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full">
        {/* Header */}
        <div className="bg-gradient-to-r from-green-500 to-green-600 p-6 rounded-t-2xl text-center">
          <div className="text-6xl mb-4">🎉</div>
          <h2 className="text-2xl font-bold text-white">Поздравляем!</h2>
          <p className="text-green-100 mt-2">Промокод успешно активирован</p>
        </div>

        {/* Content */}
        <div className="p-6">
          <div className="text-center mb-6">
            <h3 className="text-xl font-semibold text-gray-800 mb-2">
              Промокод "{data.promocode?.code}" активирован
            </h3>
            <p className="text-gray-600">{data.promocode?.description}</p>
          </div>

          {/* Courses */}
          {data.courses && data.courses.length > 0 && (
            <div className="bg-gray-50 rounded-lg p-4 mb-6">
              <h4 className="font-semibold text-gray-800 mb-3">Доступные курсы:</h4>
              <div className="space-y-2">
                {data.courses.map((course, index) => (
                  <div key={index} className="flex items-center">
                    <span className="text-green-600 mr-2">📚</span>
                    <span className="text-gray-700">{course.title}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Buttons */}
          <div className="space-y-3">
            <button
              onClick={onViewCourses}
              className="w-full bg-gradient-to-r from-green-600 to-green-700 text-white py-3 px-6 rounded-lg font-semibold hover:from-green-700 hover:to-green-800  duration-200"
            >
              Перейти к курсам
            </button>
            
            <button
              onClick={onClose}
              className="w-full bg-gray-200 text-gray-700 py-3 px-6 rounded-lg font-semibold hover:bg-gray-300  duration-200"
            >
              Закрыть
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Компонент диалога с админом
export const AdminContactDialog = ({ onClose }) => {
  const [message, setMessage] = useState('');
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    // Имитация отправки сообщения (здесь можно интегрировать с Telegram или email)
    setTimeout(() => {
      setSent(true);
      setLoading(false);
    }, 1500);
  };

  if (sent) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 text-center">
          <div className="text-5xl mb-4">✅</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Сообщение отправлено!</h2>
          <p className="text-gray-600 mb-6">Администратор свяжется с вами в ближайшее время для оформления покупки промокода.</p>
          <button
            onClick={onClose}
            className="w-full bg-emerald-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-emerald-700  duration-200"
          >
            Понятно
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 p-6 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-white">💬 Связь с администратором</h2>
            <button 
              onClick={onClose}
              className="text-white hover:text-blue-200 text-2xl font-bold"
            >
              ×
            </button>
          </div>
          <p className="text-blue-100 mt-2">Оставьте заявку на покупку промокода</p>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Price Info */}
          <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4 mb-6">
            <div className="text-center">
              <h3 className="font-bold text-emerald-800 mb-2">🎫 Промокод "ШАМИЛЬ"</h3>
              <div className="text-3xl font-bold text-emerald-600 mb-1">4900 ₽</div>
              <p className="text-emerald-700 text-sm">Полный доступ ко всем курсам</p>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Ваше имя
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Как к вам обращаться?"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Ваш email для связи"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Сообщение
              </label>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Хочу приобрести промокод для доступа ко всем курсам..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 h-24 resize-none"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white py-3 px-6 rounded-lg font-semibold hover:from-blue-700 hover:to-blue-800  duration-200 disabled:opacity-50"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Отправляем...
                </span>
              ) : (
                'Отправить заявку'
              )}
            </button>
          </form>

          {/* Contact Info */}
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <div className="text-center text-sm text-gray-600">
              <p>Или свяжитесь с нами напрямую:</p>
              <p className="font-semibold text-gray-800 mt-1">admin@uroki-islama.ru</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Компонент для отображения курсов студента
export const StudentCourses = ({ studentEmail, onBack }) => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStudentCourses();
  }, [studentEmail]);

  const fetchStudentCourses = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/student/${studentEmail}/courses`);
      setCourses(response.data);
    } catch (error) {
      console.error('Failed to fetch student courses:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Загружаем ваши курсы...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex items-center mb-6">
        <button
          onClick={onBack}
          className="mr-4 text-emerald-600 hover:text-emerald-700"
        >
          ← Назад
        </button>
        <h1 className="text-3xl font-bold text-gray-800">Мои курсы</h1>
      </div>

      {courses.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📚</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-4">У вас пока нет доступных курсов</h2>
          <p className="text-gray-600 mb-6">Активируйте промокод, чтобы получить доступ к курсам</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {courses.map((course) => (
            <div key={course.id} className="bg-white rounded-xl shadow-lg hover:shadow-xl   overflow-hidden">
              {course.image_url && (
                <img 
                  src={course.image_url} 
                  alt={course.title}
                  className="w-full h-48 object-cover"
                />
              )}
              <div className="p-6">
                <h3 className="text-xl font-semibold text-gray-800 mb-2">{course.title}</h3>
                <p className="text-gray-600 text-sm mb-4">{course.description}</p>
                <div className="flex items-center justify-between">
                  <span className="text-emerald-600 font-semibold">{course.level}</span>
                  <span className="text-gray-500 text-sm">{course.estimated_duration_hours}ч</span>
                </div>
                <button className="w-full mt-4 bg-emerald-600 text-white py-2 px-4 rounded-lg hover:bg-emerald-700  duration-200">
                  Начать изучение
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};