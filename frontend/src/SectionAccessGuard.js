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

  // 🎯 ОБРАБОТЧИК УСПЕШНОГО ВВОДА
  const handleAccessGranted = (email) => {
    setUserEmail(email);
    if (!currentUser) {
      localStorage.setItem('user_email', email);
    }
    localStorage.setItem(`section_access_${section}`, 'granted');
    setHasAccess(true);
    setShowPromocodeEntry(false);
  };

  // 🔄 СОСТОЯНИЯ РЕНДЕРА
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
        isLoggedIn={!!currentUser}
      />
    );
  }

  return null;
};

// Модальное окно для ввода промокода - Адаптивное с умной логикой
const PromocodeEntryModal = ({ sectionTitle, onAccessGranted, currentEmail, isLoggedIn }) => {
  const [email, setEmail] = useState(currentEmail || '');
  const [promocode, setPromocode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [step, setStep] = useState(
    isLoggedIn ? 'promocode' : (currentEmail ? 'promocode' : 'email')
  );
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

    if (promocode.trim().toUpperCase() === VALID_PROMOCODE) {
      onAccessGranted(email);
    } else {
      setError('Неверный промокод');
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6 sm:p-8">
        
        {/* ЗАГОЛОВОК - Адаптивный */}
        <div className="text-center mb-6 sm:mb-8">
          <div className="mx-auto h-12 w-12 sm:h-16 sm:w-16 bg-teal-100 rounded-full flex items-center justify-center mb-4">
            <svg className="h-6 w-6 sm:h-8 sm:w-8 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-2">
            Доступ к разделу
          </h2>
          <p className="text-sm sm:text-base text-gray-600">
            Для доступа к разделу "{sectionTitle}" необходим промокод
          </p>
        </div>

        {/* УСЛОВНЫЕ ФОРМЫ */}
        {step === 'email' ? (
          <EmailForm 
            email={email}
            setEmail={setEmail}
            onSubmit={handleEmailSubmit}
          />
        ) : (
          <PromocodeForm 
            email={email}
            promocode={promocode}
            setPromocode={setPromocode}
            onSubmit={handlePromocodeSubmit}
            loading={loading}
            error={error}
            showEmailInfo={!isLoggedIn}
            onChangeEmail={() => setStep('email')}
          />
        )}
        
        {/* ИНФОРМАЦИОННЫЙ БЛОК */}
        <InfoSection />
      </div>
    </div>
  );
};

// Email Form Component для незарегистрированных
const EmailForm = ({ email, setEmail, onSubmit }) => (
  <form onSubmit={onSubmit} className="space-y-6">
    <div>
      <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
        Ваш Email
      </label>
      <input
        type="email"
        id="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent text-base"
        placeholder="your@email.com"
        required
      />
    </div>

    <button
      type="submit"
      className="w-full min-h-12 bg-teal-600 text-white py-3 px-4 rounded-lg hover:bg-teal-700 focus:ring-2 focus:ring-teal-500 focus:ring-offset-2 transition duration-200 font-medium"
    >
      Продолжить
    </button>
  </form>
);

// Promocode Form Component
const PromocodeForm = ({ 
  email, 
  promocode, 
  setPromocode, 
  onSubmit, 
  loading, 
  error, 
  showEmailInfo, 
  onChangeEmail 
}) => (
  <form onSubmit={onSubmit} className="space-y-6">
    <div>
      <label htmlFor="promocode" className="block text-sm font-medium text-gray-700 mb-2">
        Промокод
      </label>
      <input
        type="text"
        id="promocode"
        value={promocode}
        onChange={(e) => setPromocode(e.target.value.toUpperCase())}
        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent text-center text-base sm:text-lg font-mono tracking-wider"
        placeholder="ВВЕДИТЕ ПРОМОКОД"
        required
      />
      {error && (
        <p className="mt-2 text-sm text-red-600">{error}</p>
      )}
    </div>

    {showEmailInfo && (
      <div className="text-sm text-gray-600 mb-4">
        <p><strong>Email:</strong> {email}</p>
        <button
          type="button"
          onClick={onChangeEmail}
          className="text-teal-600 hover:text-teal-700 underline"
        >
          Изменить email
        </button>
      </div>
    )}

    <button
      type="submit"
      disabled={loading}
      className="w-full min-h-12 bg-teal-600 text-white py-3 px-4 rounded-lg hover:bg-teal-700 focus:ring-2 focus:ring-teal-500 focus:ring-offset-2 transition duration-200 disabled:opacity-50 font-medium"
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
);

// Info Section Component
const InfoSection = () => (
  <div className="mt-8 pt-6 border-t border-gray-200">
    <div className="text-center text-sm text-gray-500">
      <p className="mb-2">💡 <strong>Где получить промокод?</strong></p>
      <p>Промокоды предоставляются администрацией проекта "Уроки Ислама".</p>
      <p className="mt-2">Обратитесь к нашим преподавателям за получением доступа.</p>
      <div className="mt-4 p-3 bg-teal-50 rounded-lg">
        <p className="text-teal-700 text-xs">
          <strong>Для тестирования:</strong> используйте промокод <code className="bg-teal-100 px-1 rounded">DEMO2024</code>
        </p>
      </div>
    </div>
  </div>
);

export default SectionAccessGuard;