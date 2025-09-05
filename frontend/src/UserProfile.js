import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from './components';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

// UserProfile Component - Полностью адаптивный компонент профиля пользователя
const UserProfile = () => {
  const { currentUser, logout } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (currentUser) {
      fetchUserProfile();
    } else {
      setError('Необходимо войти в систему');
      setLoading(false);
    }
  }, [currentUser]);

  const fetchUserProfile = async () => {
    try {
      setLoading(true);
      const userIdentifier = currentUser.email || currentUser.id;
      
      const response = await axios.get(`${BACKEND_URL}/api/user/profile`, {
        params: {
          user_email: userIdentifier
        }
      });
      
      setProfile(response.data);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch user profile:', err);
      setError('Не удалось загрузить профиль');
      // Fallback данные для демонстрации
      setProfile({
        user_name: currentUser.name || currentUser.email || 'Пользователь',
        total_points: 0,
        tests_completed: 0,
        rank: null,
        test_history: []
      });
    } finally {
      setLoading(false);
    }
  };

  // Loading state
  if (loading) {
    return <MobileLoadingSpinner />;
  }

  // Error state for non-authenticated users
  if (!currentUser) {
    return <AuthRequiredScreen />;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-4 sm:py-8 lg:py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* HEADER SECTION - Адаптивный */}
        <HeaderSection profile={profile} currentUser={currentUser} logout={logout} />
        
        {/* STATS GRID - Responsive */}
        <StatsGrid profile={profile} />
        
        {/* TEST HISTORY - Mobile-friendly */}
        <TestHistory profile={profile} />
        
        {/* QUICK ACTIONS - Adaptive buttons */}
        <QuickActions />
        
        {/* ERROR MESSAGE */}
        {error && (
          <div className="mt-4 p-3 bg-red-100 border border-red-300 rounded-lg">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Loading component - мобильно-оптимизированный
const MobileLoadingSpinner = () => (
  <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600 mx-auto mb-4"></div>
      <p className="text-sm sm:text-base text-gray-600">Загрузка профиля...</p>
    </div>
  </div>
);

// Auth required screen
const AuthRequiredScreen = () => (
  <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
    <div className="text-center max-w-md w-full">
      <div className="bg-white rounded-lg shadow-lg p-6 sm:p-8">
        <div className="w-16 h-16 bg-teal-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </div>
        <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-4">Вход требуется</h2>
        <p className="text-sm sm:text-base text-gray-600 mb-6">
          Войдите в систему, чтобы просмотреть свой профиль
        </p>
        <button
          onClick={() => window.location.href = '/'}
          className="w-full bg-teal-600 text-white py-3 px-4 rounded-lg hover:bg-teal-700 transition duration-200"
        >
          На главную
        </button>
      </div>
    </div>
  </div>
);

// Header Section Component - Адаптивный заголовок
const HeaderSection = ({ profile, currentUser, logout }) => (
  <div className="bg-white rounded-lg shadow-sm p-4 sm:p-6 mb-4 sm:mb-6">
    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
      {/* User Info */}
      <div className="flex items-center space-x-3 sm:space-x-4">
        <div className="w-12 h-12 sm:w-16 sm:h-16 bg-teal-100 rounded-full flex items-center justify-center">
          <span className="text-lg sm:text-xl font-bold text-teal-600">
            {(profile?.user_name || 'У')[0].toUpperCase()}
          </span>
        </div>
        <div>
          <h1 className="text-lg sm:text-xl lg:text-2xl font-bold text-gray-900">
            {profile?.user_name || currentUser?.name || 'Пользователь'}
          </h1>
          <p className="text-xs sm:text-sm text-gray-600">
            {currentUser?.email}
          </p>
        </div>
      </div>
      
      {/* Actions */}
      <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3">
        <button
          onClick={() => window.location.reload()}
          className="w-full sm:w-auto bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition duration-200 text-sm"
        >
          Обновить
        </button>
        <button
          onClick={logout}
          className="w-full sm:w-auto bg-red-100 text-red-700 px-4 py-2 rounded-lg hover:bg-red-200 transition duration-200 text-sm"
        >
          Выйти
        </button>
      </div>
    </div>
  </div>
);

// Stats Grid - Responsive статистики
const StatsGrid = ({ profile }) => (
  <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-4 sm:mb-6">
    <StatCard
      title="Общие очки"
      value={profile?.total_points || 0}
      icon="⭐"
      color="text-yellow-600"
      bgColor="bg-yellow-50"
    />
    <StatCard
      title="Тестов пройдено"
      value={profile?.tests_completed || 0}
      icon="✅"
      color="text-green-600"
      bgColor="bg-green-50"
    />
    <StatCard
      title="Ранг в лидерборде"
      value={profile?.rank ? `#${profile.rank}` : '-'}
      icon="🏆"
      color="text-purple-600"
      bgColor="bg-purple-50"
    />
    <StatCard
      title="Статус"
      value="Активен"
      icon="🟢"
      color="text-teal-600"
      bgColor="bg-teal-50"
    />
  </div>
);

// Stat Card Component
const StatCard = ({ title, value, icon, color, bgColor }) => (
  <div className={`${bgColor} rounded-lg p-3 sm:p-4`}>
    <div className="flex items-center justify-between mb-2">
      <span className="text-lg sm:text-xl">{icon}</span>
      <span className={`text-xl sm:text-2xl font-bold ${color}`}>
        {value}
      </span>
    </div>
    <p className="text-xs sm:text-sm text-gray-600 font-medium">{title}</p>
  </div>
);

// Test History - Mobile-friendly история тестов
const TestHistory = ({ profile }) => (
  <div className="bg-white rounded-lg shadow-sm p-4 sm:p-6 mb-4 sm:mb-6">
    <h2 className="text-base sm:text-lg font-bold text-gray-900 mb-4">
      История тестов
    </h2>
    
    {(!profile?.test_history || profile.test_history.length === 0) ? (
      <div className="text-center py-8">
        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <p className="text-sm sm:text-base text-gray-500 mb-2">Пока нет пройденных тестов</p>
        <p className="text-xs sm:text-sm text-gray-400">Начните изучение, чтобы увидеть результаты здесь</p>
      </div>
    ) : (
      <div className="space-y-3">
        {profile.test_history.slice(0, 5).map((test, index) => (
          <TestHistoryCard key={index} test={test} />
        ))}
        
        {profile.test_history.length > 5 && (
          <div className="text-center pt-4">
            <button className="text-teal-600 hover:text-teal-700 text-sm font-medium">
              Показать все результаты
            </button>
          </div>
        )}
      </div>
    )}
  </div>
);

// Test History Card - Адаптивная карточка теста
const TestHistoryCard = ({ test }) => {
  const percentage = test.total_questions > 0 ? Math.round((test.score / test.total_questions) * 100) : 0;
  const dateStr = new Date(test.completed_at).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  });

  return (
    <div className="border border-gray-200 rounded-lg p-3 sm:p-4">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-2 sm:space-y-0">
        <div className="flex-1">
          <div className="flex items-center justify-between sm:justify-start sm:space-x-4">
            <h3 className="text-sm sm:text-base font-medium text-gray-900">
              Тест #{test.test_id?.slice(-8) || 'Неизвестно'}
            </h3>
            <span className="text-xs sm:text-sm text-gray-500 sm:hidden">
              {dateStr}
            </span>
          </div>
          <p className="text-xs sm:text-sm text-gray-600 mt-1">
            {test.score} из {test.total_questions} правильных ({percentage}%)
          </p>
        </div>
        
        <div className="flex items-center justify-between sm:justify-end sm:space-x-4">
          <div className="hidden sm:block text-sm text-gray-500">
            {dateStr}
          </div>
          <div className="flex items-center space-x-2">
            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
              percentage >= 80 
                ? 'bg-green-100 text-green-800' 
                : percentage >= 60 
                  ? 'bg-yellow-100 text-yellow-800' 
                  : 'bg-red-100 text-red-800'
            }`}>
              {percentage}%
            </span>
            {test.points_earned > 0 && (
              <span className="text-teal-600 font-medium text-sm">
                +{test.points_earned}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Quick Actions - Адаптивные быстрые действия
const QuickActions = () => (
  <div className="bg-white rounded-lg shadow-sm p-4 sm:p-6">
    <h2 className="text-base sm:text-lg font-bold text-gray-900 mb-4">
      Быстрые действия
    </h2>
    
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4">
      <ActionButton
        href="/lessons"
        icon="📚"
        title="Изучать уроки"
        description="Продолжить обучение"
        color="bg-teal-50 hover:bg-teal-100 text-teal-700"
      />
      <ActionButton
        href="/leaderboard"
        icon="🏆"
        title="Лидерборд"
        description="Посмотреть рейтинг"
        color="bg-yellow-50 hover:bg-yellow-100 text-yellow-700"
      />
      <ActionButton
        href="/qa"
        icon="❓"
        title="Вопросы и ответы"
        description="Найти ответы"
        color="bg-blue-50 hover:bg-blue-100 text-blue-700"
      />
    </div>
  </div>
);

// Action Button Component
const ActionButton = ({ href, icon, title, description, color }) => (
  <a
    href={href}
    className={`block p-4 rounded-lg transition duration-200 ${color} text-center`}
  >
    <div className="text-2xl mb-2">{icon}</div>
    <h3 className="text-sm sm:text-base font-semibold mb-1">{title}</h3>
    <p className="text-xs sm:text-sm opacity-75">{description}</p>
  </a>
);

export default UserProfile;