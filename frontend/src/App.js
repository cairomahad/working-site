import React, { useState } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { 
  AuthProvider, 
  Header, 
  HeroSection, 
  WhyStudySection, 
  Leaderboard, 
  Lessons,
  Quiz 
} from "./components";
import { AdminPanel, AdminProvider } from "./AdminPanel";

// Home Page Component
const HomePage = ({ setCurrentPage }) => {
  const handleStartLearning = () => {
    setCurrentPage('lessons');
  };

  return (
    <div>
      <HeroSection onStartLearning={handleStartLearning} />
      <WhyStudySection />
      
      {/* Features Section */}
      <section className="bg-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Чем хороша учеба в "Уроки Ислама"?
            </h2>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center p-6">
              <div className="w-16 h-16 bg-teal-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Легко!</h3>
              <p className="text-gray-600">Проходите короткие тесты дома, в дороге или на работе.</p>
            </div>
            
            <div className="text-center p-6">
              <div className="w-16 h-16 bg-teal-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Бесплатно!</h3>
              <p className="text-gray-600">Вы ни за что не платите и не смотрите рекламу.</p>
            </div>
            
            <div className="text-center p-6">
              <div className="w-16 h-16 bg-teal-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Объективно!</h3>
              <p className="text-gray-600">Знания, объединяющие верующих.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="bg-gray-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Наша команда</h2>
            <p className="text-lg text-gray-600">Опытные преподаватели и знатоки ислама</p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              { name: "Али Евтеев", subject: "Этика", image: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop&crop=face" },
              { name: "Абдуль-Басит Микушкин", subject: "Основы веры", image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face" },
              { name: "Алексей Котенев", subject: "Практика веры", image: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=400&fit=crop&crop=face" },
              { name: "Микаиль Ганиев", subject: "История", image: "https://images.unsplash.com/photo-1519345182560-3f2917c472ef?w=400&h=400&fit=crop&crop=face" }
            ].map((teacher, index) => (
              <div key={index} className="text-center">
                <div className="w-32 h-32 rounded-full overflow-hidden mx-auto mb-4">
                  <img src={teacher.image} alt={teacher.name} className="w-full h-full object-cover" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900">{teacher.name}</h3>
                <p className="text-teal-600 font-medium">{teacher.subject}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

// About Page Component
const AboutPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-white to-teal-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">О проекте</h1>
          <p className="text-lg text-gray-600">Узнайте больше о нашей образовательной платформе</p>
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Наша миссия</h2>
          <p className="text-gray-700 leading-relaxed mb-6">
            Мы создали эту платформу, чтобы сделать изучение основ ислама доступным для всех желающих. 
            Наша цель — предоставить качественное исламское образование на русском языке, основанное на 
            достоверных источниках и традиционных знаниях.
          </p>
          
          <h3 className="text-xl font-semibold text-gray-900 mb-3">Что вы найдете на нашей платформе:</h3>
          <ul className="list-disc list-inside text-gray-700 space-y-2 mb-6">
            <li>Структурированные уроки по основам ислама</li>
            <li>Интерактивные тесты для закрепления знаний</li>
            <li>Система баллов и достижений</li>
            <li>Возможность соревноваться с другими учениками</li>
            <li>Материалы от проверенных источников</li>
          </ul>

          <h3 className="text-xl font-semibold text-gray-900 mb-3">Как это работает:</h3>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center p-4 bg-teal-50 rounded-lg">
              <h4 className="font-semibold text-gray-900 mb-2">1. Изучение</h4>
              <p className="text-gray-600 text-sm">Читайте материалы урока</p>
            </div>
            <div className="text-center p-4 bg-teal-50 rounded-lg">
              <h4 className="font-semibold text-gray-900 mb-2">2. Тестирование</h4>
              <p className="text-gray-600 text-sm">Проходите тесты на время</p>
            </div>
            <div className="text-center p-4 bg-teal-50 rounded-lg">
              <h4 className="font-semibold text-gray-900 mb-2">3. Прогресс</h4>
              <p className="text-gray-600 text-sm">Отслеживайте свои достижения</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Связаться с нами</h2>
          <p className="text-gray-700 mb-4">
            Если у вас есть вопросы или предложения, мы всегда готовы помочь.
          </p>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">Email:</h4>
              <p className="text-teal-600">info@uroki-islama.ru</p>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">Техническая поддержка:</h4>
              <p className="text-teal-600">support@uroki-islama.ru</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Main App Component (Public Site)
const MainApp = () => {
  const [currentPage, setCurrentPage] = useState('home');
  const [showAdminPanel, setShowAdminPanel] = useState(false);

  // Check if URL contains admin and show admin panel
  React.useEffect(() => {
    if (window.location.pathname.includes('admin')) {
      setShowAdminPanel(true);
    }
  }, []);

  if (showAdminPanel) {
    return (
      <AdminProvider>
        <AdminPanel />
      </AdminProvider>
    );
  }

  const renderPage = () => {
    if (currentPage.startsWith('quiz-')) {
      const lessonId = parseInt(currentPage.split('-')[1]);
      return <Quiz lessonId={lessonId} setCurrentPage={setCurrentPage} />;
    }

    switch (currentPage) {
      case 'home':
        return <HomePage setCurrentPage={setCurrentPage} />;
      case 'lessons':
        return <Lessons setCurrentPage={setCurrentPage} />;
      case 'leaderboard':
        return <Leaderboard />;
      case 'about':
        return <AboutPage />;
      default:
        return <HomePage setCurrentPage={setCurrentPage} />;
    }
  };

  return (
    <AuthProvider>
      <div className="App">
        <Header setCurrentPage={setCurrentPage} currentPage={currentPage} />
        {renderPage()}
        
        {/* Admin Panel Access */}
        <div style={{ position: 'fixed', bottom: '10px', right: '10px' }}>
          <button 
            onClick={() => window.location.href = '/admin'}
            className="bg-gray-800 text-white px-3 py-2 rounded-lg text-sm hover:bg-gray-700 shadow-lg"
          >
            🔧 Админ панель
          </button>
        </div>
      </div>
    </AuthProvider>
  );
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/admin/*" element={
          <AdminProvider>
            <AdminPanel />
          </AdminProvider>
        } />
        <Route path="/*" element={<MainApp />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;