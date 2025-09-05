import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from './components';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

// Компонент защиты доступа к разделам с интеграцией useAuth
export const SectionAccessGuard = ({ section, sectionTitle, children }) => {
  const { currentUser } = useAuth();
  const [hasAccess, setHasAccess] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showPromocodeEntry, setShowPromocodeEntry] = useState(false);
  const [userEmail, setUserEmail] = useState('');

  useEffect(() => {
    // 🔐 ЛОГИКА ОПРЕДЕЛЕНИЯ ДОСТУПА
    if (currentUser && currentUser.email) {
      // ✅ ЗАРЕГИСТРИРОВАННЫЙ ПОЛЬЗОВАТЕЛЬ
      const savedAccess = localStorage.getItem(`section_access_${section}`);
      
      if (savedAccess === 'granted') {
        setUserEmail(currentUser.email);
        setHasAccess(true);
        setLoading(false);
      } else {
        // Нужен только промокод
        setUserEmail(currentUser.email);
        setLoading(false);
        setShowPromocodeEntry(true);
      }
    } else {
      // ❌ НЕЗАРЕГИСТРИРОВАННЫЙ ГОСТЬ
      const savedEmail = localStorage.getItem('user_email');
      const savedAccess = localStorage.getItem(`section_access_${section}`);
      
      if (savedAccess === 'granted' && savedEmail) {
        setUserEmail(savedEmail);
        setHasAccess(true);
        setLoading(false);
      } else {
        // Нужен email + промокод
        setLoading(false);
        setShowPromocodeEntry(true);
      }
    }
  }, [section, currentUser]);

  const checkAccess = async (email) => {
    try {
      const response = await axios.post(`${BACKEND_URL}/api/check-access`, {
        student_email: email,
        section: section
      });

      setHasAccess(response.data.has_access);
      if (!response.data.has_access) {
        setShowPromocodeEntry(true);
      }
    } catch (error) {
      console.error('Error checking access:', error);
      setHasAccess(false);
      setShowPromocodeEntry(true);
    }
    setLoading(false);
  };

  const handleAccessGranted = (email) => {
    setUserEmail(email);
    localStorage.setItem('user_email', email);
    setHasAccess(true);
    setShowPromocodeEntry(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex justify-center items-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
      </div>
    );
  }

  if (hasAccess) {
    return children;
  }

  if (showPromocodeEntry) {
    return (
      <PromocodeEntryModal
        sectionTitle={sectionTitle}
        onAccessGranted={handleAccessGranted}
        currentEmail={userEmail}
      />
    );
  }

  return null;
};

// Модальное окно для ввода промокода
const PromocodeEntryModal = ({ sectionTitle, onAccessGranted, currentEmail }) => {
  const [email, setEmail] = useState(currentEmail || '');
  const [promocode, setPromocode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [step, setStep] = useState(currentEmail ? 'promocode' : 'email');
  const VALID_PROMOCODE = 'DEMO2024';

  const handleEmailSubmit = (e) => {
    e.preventDefault();
    if (email.trim()) {
      localStorage.setItem('user_email', email.trim());
      setStep('promocode');
    }
  };

  const handlePromocodeSubmit = async (e) => {
    e.preventDefault();
    if (!promocode.trim()) return;

    setLoading(true);
setError('');

if (promocode.trim() === VALID_PROMOCODE) {
  onAccessGranted(email);
} else {
  setError('Неверный промокод');
}

setLoading(false);
};

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <div className="text-center mb-8">
          <div className="mx-auto h-16 w-16 bg-teal-100 rounded-full flex items-center justify-center mb-4">
            <svg className="h-8 w-8 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Доступ к разделу</h2>
          <p className="text-gray-600">
            Для доступа к разделу "{sectionTitle}" необходим промокод
          </p>
        </div>

        {step === 'email' ? (
          <form onSubmit={handleEmailSubmit} className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Ваш Email
              </label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                placeholder="your@email.com"
                required
              />
            </div>

            <button
              type="submit"
              className="w-full bg-teal-600 text-white py-3 px-4 rounded-lg hover:bg-teal-700 focus:ring-2 focus:ring-teal-500 focus:ring-offset-2 transition duration-200"
            >
              Продолжить
            </button>
          </form>
        ) : (
          <form onSubmit={handlePromocodeSubmit} className="space-y-6">
            <div>
              <label htmlFor="promocode" className="block text-sm font-medium text-gray-700 mb-2">
                Промокод
              </label>
              <input
                type="text"
                id="promocode"
                value={promocode}
                onChange={(e) => setPromocode(e.target.value.toUpperCase())}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent text-center text-lg font-mono tracking-wider"
                placeholder="ВВЕДИТЕ ПРОМОКОД"
                required
              />
              {error && (
                <p className="mt-2 text-sm text-red-600">{error}</p>
              )}
            </div>

            <div className="text-sm text-gray-600 mb-4">
              <p><strong>Email:</strong> {email}</p>
              <button
                type="button"
                onClick={() => setStep('email')}
                className="text-teal-600 hover:text-teal-700 underline"
              >
                Изменить email
              </button>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-teal-600 text-white py-3 px-4 rounded-lg hover:bg-teal-700 focus:ring-2 focus:ring-teal-500 focus:ring-offset-2 transition duration-200 disabled:opacity-50"
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Проверяем...
                </div>
              ) : (
                'Проверить промокод'
              )}
            </button>
          </form>
        )}

        <div className="mt-8 pt-6 border-t border-gray-200">
          <div className="text-center text-sm text-gray-500">
            <p className="mb-2">💡 <strong>Где получить промокод?</strong></p>
            <p>Промокоды предоставляются администрацией проекта "Уроки Ислама".</p>
            <p className="mt-2">Обратитесь к нашим преподавателям за получением доступа.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SectionAccessGuard;