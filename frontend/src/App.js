import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useParams } from "react-router-dom";
import { 
  AuthProvider,
  useAuth, 
  Header, 
  HeroSection, 
  WhyStudySection, 
  Leaderboard, 
  Lessons,
  Quiz 
} from "./components";
import MainAdminPanel from "./MainAdminPanel";
import { CourseLevels, CourseDetail } from "./CourseComponents";
import { LessonView, TestTaking } from "./LessonComponents";
import { LessonsPage, CourseLessonsPage, LessonDetailPage } from "./LessonsPage";
import { QAMainPage, QACategoryPage, QAQuestionPage, QASearchPage, AskQuestionForm } from "./QAComponents";
import { PromocodePromo, PromocodeEntry, PromocodeSuccess, AdminContactDialog, StudentCourses } from "./PromocodeComponents";
import TestTakingComponent from "./TestTakingComponent";
import NewLeaderboardPage from "./LeaderboardPage";

// Home Page Component
const HomePage = ({ setCurrentPage }) => {
  const [teamMembers, setTeamMembers] = useState([]);
  const [loadingTeam, setLoadingTeam] = useState(true);
  const [showPromocodeEntry, setShowPromocodeEntry] = useState(false);
  const [showPromocodeSuccess, setShowPromocodeSuccess] = useState(false);
  const [showAdminContact, setShowAdminContact] = useState(false);
  const [showStudentCourses, setShowStudentCourses] = useState(false);
  const [promocodeData, setPromocodeData] = useState(null);

  useEffect(() => {
    fetchTeamMembers();
  }, []);

  const fetchTeamMembers = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/team`);
      setTeamMembers(response.data);
    } catch (error) {
      console.error('Failed to fetch team members:', error);
      // Fallback to hardcoded data if API fails
      setTeamMembers([
        { name: "Али Евтеев", subject: "Этика", image_base64: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop&crop=face" },
        { name: "Абдуль-Басит Микушкин", subject: "Основы веры", image_base64: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face" },
        { name: "Алексей Котенев", subject: "Практика веры", image_base64: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=400&fit=crop&crop=face" },
        { name: "Микаиль Ганиев", subject: "История", image_base64: "https://images.unsplash.com/photo-1519345182560-3f2917c472ef?w=400&h=400&fit=crop&crop=face" }
      ]);
    }
    setLoadingTeam(false);
  };

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
            {loadingTeam ? (
              // Loading state
              [1,2,3,4].map((i) => (
                <div key={i} className="text-center animate-pulse">
                  <div className="w-32 h-32 rounded-full bg-gray-300 mx-auto mb-4"></div>
                  <div className="h-4 bg-gray-300 rounded w-24 mx-auto mb-2"></div>
                  <div className="h-3 bg-gray-300 rounded w-16 mx-auto"></div>
                </div>
              ))
            ) : (
              teamMembers.map((member, index) => (
                <div key={member.id || index} className="text-center">
                  <div className="w-32 h-32 rounded-full overflow-hidden mx-auto mb-4">
                    <img 
                      src={member.image_base64 || member.image_url || `https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop&crop=face`} 
                      alt={member.name} 
                      className="w-full h-full object-cover" 
                    />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900">{member.name}</h3>
                  <p className="text-teal-600 font-medium">{member.subject}</p>
                </div>
              ))
            )}
          </div>
        </div>
      </section>

      {/* Promocode Modals */}
      {showPromocodeEntry && (
        <PromocodeEntry
          onSuccess={(data) => {
            setShowPromocodeEntry(false);
            setShowPromocodeSuccess(true);
            setPromocodeData(data);
          }}
          onClose={() => setShowPromocodeEntry(false)}
        />
      )}

      {showPromocodeSuccess && (
        <PromocodeSuccess
          data={promocodeData}
          onClose={() => setShowPromocodeSuccess(false)}
          onViewCourses={() => {
            setShowPromocodeSuccess(false);
            setShowStudentCourses(true);
          }}
        />
      )}

      {showAdminContact && (
        <AdminContactDialog
          onClose={() => setShowAdminContact(false)}
        />
      )}

      {showStudentCourses && (
        <StudentCourses
          studentEmail={promocodeData?.student_email || ''}
          onBack={() => setShowStudentCourses(false)}
        />
      )}
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

        {/* Navigation Section */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Исследуйте нашу платформу</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            <a
              href="/lessons"
              className="block p-6 bg-gradient-to-br from-teal-50 to-teal-100 rounded-xl hover:from-teal-100 hover:to-teal-200 transition-all duration-300 text-center group"
            >
              <div className="text-3xl mb-3">📚</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Уроки</h3>
              <p className="text-sm text-gray-600">Изучайте основы ислама</p>
            </a>
            
            <a
              href="/qa"
              className="block p-6 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl hover:from-blue-100 hover:to-blue-200 transition-all duration-300 text-center group"
            >
              <div className="text-3xl mb-3">❓</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Вопросы и ответы</h3>
              <p className="text-sm text-gray-600">Ответы имама на ваши вопросы</p>
            </a>
            
            <a
              href="/leaderboard"
              className="block p-6 bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-xl hover:from-yellow-100 hover:to-yellow-200 transition-all duration-300 text-center group"
            >
              <div className="text-3xl mb-3">🏆</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Лидерборд</h3>
              <p className="text-sm text-gray-600">Соревнуйтесь с другими</p>
            </a>
            
            <a
              href="/"
              className="block p-6 bg-gradient-to-br from-green-50 to-green-100 rounded-xl hover:from-green-100 hover:to-green-200 transition-all duration-300 text-center group"
            >
              <div className="text-3xl mb-3">🏠</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Главная</h3>
              <p className="text-sm text-gray-600">Вернуться на главную</p>
            </a>
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
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [selectedLesson, setSelectedLesson] = useState(null);

  const renderPage = () => {
    if (currentPage.startsWith('quiz-')) {
      const lessonId = parseInt(currentPage.split('-')[1]);
      return <Quiz lessonId={lessonId} setCurrentPage={setCurrentPage} />;
    }

    if (currentPage.startsWith('test-')) {
      const testId = currentPage.split('-')[1];
      return <TestTaking testId={testId} setCurrentPage={setCurrentPage} />;
    }

    switch (currentPage) {
      case 'home':
        return <HomePage setCurrentPage={setCurrentPage} />;
      case 'lessons':
        return (
          <LessonsPage 
            setCurrentPage={setCurrentPage} 
            setSelectedCourse={setSelectedCourse}
            setSelectedLesson={setSelectedLesson}
          />
        );
      case 'course-lessons':
        return (
          <CourseLessonsPage 
            course={selectedCourse}
            setCurrentPage={setCurrentPage}
            setSelectedLesson={setSelectedLesson}
          />
        );
      case 'lesson-detail':
        return (
          <LessonDetailPage 
            lesson={selectedLesson}
            course={selectedCourse}
            setCurrentPage={setCurrentPage}
          />
        );
      case 'old-lessons':
        return (
          <CourseLevels 
            setCurrentPage={setCurrentPage} 
            setSelectedCourse={setSelectedCourse} 
          />
        );
      case 'course-detail':
        return (
          <CourseDetail 
            course={selectedCourse}
            setCurrentPage={setCurrentPage}
            setSelectedLesson={setSelectedLesson}
          />
        );
      case 'lesson-view':
        return (
          <LessonView 
            lesson={selectedLesson}
            setCurrentPage={setCurrentPage}
            setSelectedCourse={setSelectedCourse}
          />
        );
      case 'leaderboard':
        return <Leaderboard />;
      case 'about':
        return <AboutPage />;
      default:
        return <HomePage setCurrentPage={setCurrentPage} />;
    }
  };

  return (
    <div className="App">
      <Header setCurrentPage={setCurrentPage} currentPage={currentPage} />
      {renderPage()}
    </div>
  );
};

// Router Component to handle admin/public routing
const AppRouter = () => {
  const { isAdmin } = useAuth();

  // If user is admin, show admin panel regardless of URL
  if (isAdmin) {
    return <MainAdminPanel />;
  }

  // For public users, show main app with React Router
  return (
    <Routes>
      <Route path="/" element={<MainApp />} />
      <Route path="/lessons" element={<LessonsPageRouter />} />
      <Route path="/lessons/:courseSlug" element={<CourseLessonsRouter />} />
      <Route path="/lessons/:courseSlug/:lessonSlug" element={<LessonDetailRouter />} />
      <Route path="/qa" element={<QAMainPageRouter />} />
      <Route path="/qa/category/:categoryId" element={<QACategoryPageRouter />} />
      <Route path="/qa/question/:slug" element={<QAQuestionPageRouter />} />
      <Route path="/qa/search" element={<QASearchPageRouter />} />
      <Route path="/leaderboard" element={<LeaderboardPage />} />
      <Route path="/about" element={<AboutPage />} />
      <Route path="/test/:testId" element={<TestRouter />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

// Route Components
const LessonsPageRouter = () => {
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [selectedLesson, setSelectedLesson] = useState(null);
  const navigate = useNavigate();

  const handleCourseSelect = (course) => {
    setSelectedCourse(course);
    navigate(`/lessons/${course.slug || course.id}`);
  };

  return (
    <div className="App">
      <Header />
      <LessonsPage 
        setSelectedCourse={handleCourseSelect}
        setSelectedLesson={setSelectedLesson}
      />
    </div>
  );
};

const CourseLessonsRouter = () => {
  const { courseSlug } = useParams();
  const navigate = useNavigate();
  const [course, setCourse] = useState(null);
  const [selectedLesson, setSelectedLesson] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCourse();
  }, [courseSlug]);

  const fetchCourse = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/courses`);
      const foundCourse = response.data.find(c => c.slug === courseSlug || c.id === courseSlug);
      setCourse(foundCourse);
    } catch (error) {
      console.error('Failed to fetch course:', error);
    }
    setLoading(false);
  };

  const handleLessonSelect = (lesson) => {
    setSelectedLesson(lesson);
    navigate(`/lessons/${courseSlug}/${lesson.slug || lesson.id}`);
  };

  if (loading) {
    return (
      <div className="App">
        <Header />
        <div className="min-h-screen bg-white flex justify-center items-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
        </div>
      </div>
    );
  }

  if (!course) {
    return (
      <div className="App">
        <Header />
        <div className="min-h-screen bg-white flex justify-center items-center">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Курс не найден</h2>
            <button
              onClick={() => navigate('/lessons')}
              className="bg-teal-500 text-white px-4 py-2 rounded-lg hover:bg-teal-600 transition-colors"
            >
              Вернуться к урокам
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <Header />
      <CourseLessonsPage 
        course={course}
        setSelectedLesson={handleLessonSelect}
      />
    </div>
  );
};

const LessonDetailRouter = () => {
  const { courseSlug, lessonSlug } = useParams();
  const navigate = useNavigate();
  const [course, setCourse] = useState(null);
  const [lesson, setLesson] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCourseAndLesson();
  }, [courseSlug, lessonSlug]);

  const fetchCourseAndLesson = async () => {
    try {
      // Fetch course
      const coursesResponse = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/courses`);
      const foundCourse = coursesResponse.data.find(c => c.slug === courseSlug || c.id === courseSlug);
      setCourse(foundCourse);

      if (foundCourse) {
        // Fetch lessons
        const lessonsResponse = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/courses/${foundCourse.id}/lessons`);
        const foundLesson = lessonsResponse.data.find(l => l.slug === lessonSlug || l.id === lessonSlug);
        setLesson(foundLesson);
      }
    } catch (error) {
      console.error('Failed to fetch course and lesson:', error);
    }
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="App">
        <Header />
        <div className="min-h-screen bg-white flex justify-center items-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
        </div>
      </div>
    );
  }

  if (!course || !lesson) {
    return (
      <div className="App">
        <Header />
        <div className="min-h-screen bg-white flex justify-center items-center">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Урок не найден</h2>
            <button
              onClick={() => navigate('/lessons')}
              className="bg-teal-500 text-white px-4 py-2 rounded-lg hover:bg-teal-600 transition-colors"
            >
              Вернуться к урокам
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <Header />
      <LessonDetailPage 
        lesson={lesson}
        course={course}
      />
    </div>
  );
};

const TestRouter = () => {
  return (
    <div className="App">
      <Header />
      <TestTakingComponent />
    </div>
  );
};

const LeaderboardPage = () => {
  return (
    <div className="App">
      <Header />
      <Leaderboard />
    </div>
  );
};

// Q&A Route Components
const QAMainPageRouter = () => {
  return (
    <div className="App">
      <Header />
      <QAMainPage />
    </div>
  );
};

const QACategoryPageRouter = () => {
  return (
    <div className="App">
      <Header />
      <QACategoryPage />
    </div>
  );
};

const QAQuestionPageRouter = () => {
  return (
    <div className="App">
      <Header />
      <QAQuestionPage />
    </div>
  );
};

const QASearchPageRouter = () => {
  return (
    <div className="App">
      <Header />
      <QASearchPage />
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRouter />
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;