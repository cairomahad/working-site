import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from './components';
import { PromocodeEntry } from './PromocodeComponents';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Main Lessons Page Component - similar to islam.school/lessons
export const LessonsPage = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showPromocodeEntry, setShowPromocodeEntry] = useState(false);
  const [showPremiumInfo, setShowPremiumInfo] = useState(false);
  const [selectedPremiumCourse, setSelectedPremiumCourse] = useState(null);
  const [userEmail, setUserEmail] = useState('');
  const { currentUser } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      const response = await axios.get(`${API}/courses`);
      setCourses(response.data);
    } catch (error) {
      console.error('Failed to fetch courses:', error);
    }
    setLoading(false);
  };

  const handleCourseClick = async (course) => {
    // Проверяем, является ли курс премиум (например, "Культура Ислама")
    if (course.title === "Культура Ислама") {
      // Проверяем доступ пользователя к этому курсу
      if (currentUser && currentUser.email) {
        try {
          const response = await axios.get(`${API}/student/${currentUser.email}/courses`);
          const hasAccess = response.data.some(userCourse => userCourse.id === course.id);
          
          if (hasAccess) {
            // У пользователя есть доступ, переходим к курсу
            navigate(`/lessons/${course.slug || course.id}`);
          } else {
            // Нет доступа, показываем информацию о премиум курсе
            setSelectedPremiumCourse(course);
            setUserEmail(currentUser.email);
            setShowPremiumInfo(true);
          }
        } catch (error) {
          console.error('Ошибка проверки доступа:', error);
          // Показываем информацию о премиум курсе при ошибке
          setSelectedPremiumCourse(course);
          setUserEmail(currentUser?.email || '');
          setShowPremiumInfo(true);
        }
      } else {
        // Пользователь не авторизован, показываем информацию о курсе
        setSelectedPremiumCourse(course);
        setUserEmail('');
        setShowPremiumInfo(true);
      }
    } else {
      // Обычный курс, открываем без проверки
      navigate(`/lessons/${course.slug || course.id}`);
    }
  };

  // Course configurations
  const getCourseConfig = (title) => {
    const titleLower = title.toLowerCase();
    if (titleLower.includes('основы') || titleLower.includes('вер')) {
      return {
        icon: (
          <svg className="w-12 h-12 text-teal-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
          </svg>
        ),
        description: 'Чем ислам отличается от других религий. Во что верят мусульмане.',
        hasLiterature: true,
        literatureUrl: '/files/simplethings.pdf'
      };
    } else if (titleLower.includes('практик')) {
      return {
        icon: (
          <svg className="w-12 h-12 text-teal-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm.31-8.86c-1.77-.45-2.34-.94-2.34-1.67 0-.84.79-1.43 2.1-1.43 1.38 0 1.9.66 1.94 1.64h1.71c-.05-1.34-.87-2.57-2.49-2.97V5H10.9v1.69c-1.51.32-2.72 1.3-2.72 2.81 0 1.79 1.49 2.69 3.66 3.21 1.95.46 2.34 1.15 2.34 1.87 0 .53-.39 1.39-2.1 1.39-1.6 0-2.23-.72-2.32-1.64H8.04c.1 1.7 1.36 2.66 2.86 2.97V19h2.34v-1.67c1.52-.29 2.72-1.16 2.72-2.89-.01-2.2-1.9-2.96-3.65-3.3z"/>
          </svg>
        ),
        description: 'Основные ежедневные ритуалы в жизни мусульманина.',
        hasLiterature: true,
        literatureUrl: 'https://drive.google.com/file/d/1AH8avYSHM8KDWw6xRMfVJVTVtFhjBzIi/view'
      };
    } else if (titleLower.includes('этик')) {
      return {
        icon: (
          <svg className="w-12 h-12 text-teal-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
          </svg>
        ),
        description: 'Отношения человека с Творцом, своей душой и окружением.',
        hasLiterature: false
      };
    } else if (titleLower.includes('истор')) {
      return {
        icon: (
          <svg className="w-12 h-12 text-teal-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M9 11H7v6h2v-6zm4 0h-2v6h2v-6zm4 0h-2v6h2v-6zm2.5-9H19v2h-1.5v17c0 .55-.45 1-1 1h-9c-.55 0-1-.45-1-1V4H5V2h3.5c.28 0 .5-.22.5-.5s.22-.5.5-.5h3c.28 0 .5.22.5.5s.22.5.5.5z"/>
          </svg>
        ),
        description: 'Мир от сотворения до конца времён. Пророки, Писания, цивилизации.',
        hasLiterature: false
      };
    } else if (titleLower.includes('культур')) {
      return {
        icon: (
          <svg className="w-12 h-12 text-amber-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
          </svg>
        ),
        description: 'Премиум курс: Углубленное изучение исламской культуры и цивилизации. 🔒 Требуется промокод.',
        hasLiterature: false,
        isPremium: true
      };
    }
    return {
      icon: (
        <svg className="w-12 h-12 text-teal-500" fill="currentColor" viewBox="0 0 24 24">
          <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
        </svg>
      ),
      description: 'Изучение основ исламской религии и культуры.',
      hasLiterature: false
    };
  };

  // Function to convert YouTube URL to embed format
  const convertToEmbedUrl = (url) => {
    if (!url) return '';
    
    // If it's already an embed URL, return as is
    if (url.includes('youtube.com/embed/')) {
      return url;
    }
    
    // Extract video ID from various YouTube URL formats
    const videoIdMatch = url.match(/(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
    
    if (videoIdMatch && videoIdMatch[1]) {
      const videoId = videoIdMatch[1];
      return `https://www.youtube.com/embed/${videoId}`;
    }
    
    return url; // Return original URL if no match found
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex justify-center items-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Progress Notification for Non-registered Users */}
      {!currentUser && (
        <div className="bg-gradient-to-r from-teal-400 to-teal-500 text-white py-4">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-center">
              <div className="flex items-center space-x-3">
                <div className="w-6 h-6 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-bold">!</span>
                </div>
                <p className="text-sm md:text-base">
                  Вы смогли бы сохранять и отслеживать прогресс после регистрации, а в конце обучения получить сертификат!
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Content - Full Width */}
      <div className="min-h-screen">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="max-w-6xl">
            <h1 className="text-3xl font-bold text-gray-900 mb-8">Уроки</h1>
            
            {/* Courses List */}
            <div className="space-y-8">
              {courses.map((course, index) => {
                const config = getCourseConfig(course.title);
                const lessonsCount = course.lessons_count || 10; // Default to 10 for demo
                
                return (
                  <div
                    key={course.id}
                    className={`relative bg-white rounded-lg border transition-all duration-300 cursor-pointer group ${
                      config.isPremium 
                        ? 'border-amber-300 hover:border-amber-400 hover:shadow-amber-100 hover:shadow-lg' 
                        : 'border-gray-200 hover:shadow-md'
                    }`}
                    onClick={() => handleCourseClick(course)}
                  >
                    {/* Premium Badge */}
                    {config.isPremium && (
                      <div className="absolute -top-2 -right-2 bg-gradient-to-r from-amber-400 to-amber-500 text-white px-3 py-1 rounded-full text-xs font-bold shadow-lg">
                        ⭐ ПРЕМИУМ
                      </div>
                    )}
                    
                    <div className={`p-6 ${config.isPremium ? 'bg-gradient-to-br from-amber-50 to-yellow-50' : ''}`}>
                      <div className="flex items-start space-x-6">
                        {/* Course Icon */}
                        <div className="flex-shrink-0">
                          {config.icon}
                        </div>
                        
                        {/* Course Content */}
                        <div className="flex-1">
                          <h2 className="text-2xl font-bold text-teal-600 mb-2 group-hover:text-teal-700 transition-colors">
                            {course.title}
                          </h2>
                          <p className="text-gray-600 mb-4 text-sm leading-relaxed">
                            {config.description}
                          </p>
                          
                          {/* Progress Circles */}
                          <div className="flex items-center space-x-2 mb-4">
                            {[...Array(lessonsCount)].map((_, i) => (
                              <div
                                key={i}
                                className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                                  i === 0 ? 'bg-teal-500 border-teal-500' : 
                                  i === lessonsCount - 1 ? 'bg-teal-500 border-teal-500' :
                                  'border-teal-300 bg-white'
                                }`}
                              >
                                {(i === 0 || i === lessonsCount - 1) && (
                                  <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                  </svg>
                                )}
                                {(i > 0 && i < lessonsCount - 1) && (
                                  <svg className="w-4 h-4 text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                  </svg>
                                )}
                              </div>
                            ))}
                          </div>
                          
                          {/* Additional Literature Link */}
                          {config.hasLiterature && (
                            <a
                              href={config.literatureUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center text-sm text-gray-500 hover:text-teal-600 transition-colors"
                              onClick={(e) => e.stopPropagation()}
                            >
                              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                              </svg>
                              Дополнительная литература
                              <svg className="w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                              </svg>
                            </a>
                          )}
                        </div>
                        
                        {/* Right side content */}
                        <div className="flex-shrink-0 text-right">
                          {course.additional_materials && (
                            <div className="mb-2">
                              <a
                                href={course.additional_materials}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-sm text-gray-500 hover:text-teal-600 transition-colors"
                                onClick={(e) => e.stopPropagation()}
                              >
                                Пособие
                                <svg className="w-3 h-3 ml-1 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                </svg>
                              </a>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {courses.length === 0 && (
              <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
                <svg className="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C20.832 18.477 19.246 18 17.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Курсы скоро будут добавлены</h3>
                <p className="text-gray-500">Платформа находится в разработке</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Premium Course Info Modal */}
      {showPremiumInfo && selectedPremiumCourse && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className="bg-gradient-to-r from-amber-400 to-amber-500 p-6 rounded-t-2xl">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <span className="text-3xl mr-3">⭐</span>
                  <div>
                    <h2 className="text-2xl font-bold text-white">Премиум курс</h2>
                    <p className="text-amber-100">{selectedPremiumCourse.title}</p>
                  </div>
                </div>
                <button 
                  onClick={() => {
                    setShowPremiumInfo(false);
                    setSelectedPremiumCourse(null);
                  }}
                  className="text-white hover:text-amber-200 text-2xl font-bold"
                >
                  ×
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="p-6">
              <div className="text-center mb-6">
                <img 
                  src={selectedPremiumCourse.image_url || "https://images.unsplash.com/photo-1547036967-23d11aacaee0?w=800&h=400&fit=crop"} 
                  alt={selectedPremiumCourse.title}
                  className="w-full h-48 object-cover rounded-lg mb-4"
                />
                <h3 className="text-xl font-bold text-gray-800 mb-2">{selectedPremiumCourse.title}</h3>
                <p className="text-gray-600 text-sm leading-relaxed">{selectedPremiumCourse.description}</p>
              </div>

              {/* Course Details */}
              <div className="bg-amber-50 rounded-lg p-4 mb-6">
                <h4 className="font-semibold text-amber-800 mb-3">🎓 Что включено в курс:</h4>
                <div className="space-y-2 text-sm text-amber-700">
                  <div className="flex items-center">
                    <span className="mr-2">📚</span>
                    <span>3 углубленных урока по исламской культуре</span>
                  </div>
                  <div className="flex items-center">
                    <span className="mr-2">🎥</span>
                    <span>Видеоматериалы и интерактивный контент</span>
                  </div>
                  <div className="flex items-center">
                    <span className="mr-2">⏱️</span>
                    <span>Примерно {selectedPremiumCourse.estimated_duration_hours} часов изучения</span>
                  </div>
                  <div className="flex items-center">
                    <span className="mr-2">📜</span>
                    <span>Сертификат по завершению</span>
                  </div>
                  <div className="flex items-center">
                    <span className="mr-2">💝</span>
                    <span>Пожизненный доступ к материалам</span>
                  </div>
                </div>
              </div>

              {/* Price Info */}
              <div className="bg-white border-2 border-amber-200 rounded-lg p-4 mb-6">
                <div className="text-center">
                  <h4 className="font-bold text-gray-800 mb-2">💎 Доступ по промокоду</h4>
                  <div className="text-2xl font-bold text-amber-600 mb-1">4900 ₽</div>
                  <p className="text-gray-600 text-sm">Полный доступ ко всем курсам платформы</p>
                  <p className="text-amber-600 font-semibold mt-1">Промокод: ШАМИЛЬ</p>
                </div>
              </div>

              {/* Buttons */}
              <div className="space-y-3">
                <button
                  onClick={() => {
                    setShowPremiumInfo(false);
                    setShowPromocodeEntry(true);
                  }}
                  className="w-full bg-gradient-to-r from-amber-500 to-amber-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-amber-600 hover:to-amber-700 transition-all duration-200"
                >
                  🎫 У меня есть промокод
                </button>
                
                <button
                  onClick={() => {
                    // Показать контактную информацию или переход к покупке
                    alert('Для покупки промокода свяжитесь с нами по email: admin@uroki-islama.ru');
                  }}
                  className="w-full bg-white text-amber-600 py-3 px-6 rounded-lg font-semibold border-2 border-amber-200 hover:bg-amber-50 transition-all duration-200"
                >
                  💰 Купить промокод
                </button>
                
                <button
                  onClick={() => {
                    setShowPremiumInfo(false);
                    setSelectedPremiumCourse(null);
                  }}
                  className="w-full bg-gray-200 text-gray-700 py-3 px-6 rounded-lg font-semibold hover:bg-gray-300 transition-all duration-200"
                >
                  Закрыть
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Promocode Modal */}
      {showPromocodeEntry && selectedPremiumCourse && (
        <PromocodeEntry
          onSuccess={(data) => {
            setShowPromocodeEntry(false);
            setSelectedPremiumCourse(null);
            // После успешной активации промокода переходим к курсу
            if (selectedPremiumCourse) {
              navigate(`/lessons/${selectedPremiumCourse.slug || selectedPremiumCourse.id}`);
            }
          }}
          onClose={() => {
            setShowPromocodeEntry(false);
            // Возвращаемся к информационному окну
            setShowPremiumInfo(true);
          }}
        />
      )}
    </div>
  );
};

// Course Lessons List Component - similar to course detail page
export const CourseLessonsPage = ({ course }) => {
  const [lessons, setLessons] = useState([]);
  const [loading, setLoading] = useState(true);
  const { currentUser } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (course) {
      fetchLessons();
    }
  }, [course]);

  const fetchLessons = async () => {
    try {
      const response = await axios.get(`${API}/courses/${course.id}/lessons`);
      setLessons(response.data);
    } catch (error) {
      console.error('Failed to fetch lessons:', error);
    }
    setLoading(false);
  };

  const handleLessonClick = (lesson) => {
    navigate(`/lessons/${course.slug || course.id}/${lesson.slug || lesson.id}`);
  };

  const handleBackToLessons = () => {
    navigate('/lessons');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex justify-center items-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Header Section */}
      <div className="bg-gradient-to-r from-teal-500 to-teal-600 text-white py-12">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <button
            onClick={handleBackToLessons}
            className="mb-4 text-teal-100 hover:text-white flex items-center"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            ← Назад к урокам
          </button>
          <h1 className="text-3xl md:text-4xl font-bold mb-2">{course.title}</h1>
          <p className="text-xl text-teal-100">
            {course.description}
          </p>
        </div>
      </div>

      {/* Lessons List */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="space-y-4">
          {lessons.map((lesson, index) => (
            <div
              key={lesson.id}
              className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-all duration-300 cursor-pointer group"
              onClick={() => handleLessonClick(lesson)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center mb-2">
                    <div className="w-8 h-8 bg-teal-100 rounded-full flex items-center justify-center mr-4">
                      <span className="text-teal-600 font-medium">{index + 1}</span>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 group-hover:text-teal-600 transition-colors">
                      {lesson.title}
                    </h3>
                  </div>
                  
                  {lesson.description && (
                    <p className="text-gray-600 mb-3 ml-12">
                      {lesson.description}
                    </p>
                  )}
                  
                  <div className="flex items-center text-sm text-gray-500 ml-12">
                    {lesson.type === 'video' && (
                      <span className="flex items-center mr-4">
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h1m4 0h1m2-5a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Видео урок
                      </span>
                    )}
                    {lesson.type === 'text' && (
                      <span className="flex items-center mr-4">
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        Текстовый урок
                      </span>
                    )}
                    {lesson.estimated_duration && (
                      <span className="flex items-center">
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {lesson.estimated_duration} мин
                      </span>
                    )}
                  </div>
                </div>
                
                <div className="text-gray-400 group-hover:text-teal-500 transition-colors">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            </div>
          ))}
        </div>

        {lessons.length === 0 && (
          <div className="text-center py-12">
            <svg className="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C20.832 18.477 19.246 18 17.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Уроки скоро будут добавлены</h3>
            <p className="text-gray-500">Этот курс находится в разработке</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Individual Lesson Detail Component - similar to islam.school lesson page
export const LessonDetailPage = ({ lesson, course }) => {
  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const { currentUser } = useAuth();
  const navigate = useNavigate();

  // Function to convert YouTube URL to embed format
  const convertToEmbedUrl = (url) => {
    if (!url) return '';
    
    // If it's already an embed URL, return as is
    if (url.includes('youtube.com/embed/')) {
      return url;
    }
    
    // Extract video ID from various YouTube URL formats
    const videoIdMatch = url.match(/(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
    
    if (videoIdMatch && videoIdMatch[1]) {
      const videoId = videoIdMatch[1];
      return `https://www.youtube.com/embed/${videoId}`;
    }
    
    return url; // Return original URL if no match found
  };

  useEffect(() => {
    if (lesson) {
      fetchLessonTests();
    }
  }, [lesson]);

  const fetchLessonTests = async () => {
    try {
      const response = await axios.get(`${API}/lessons/${lesson.id}/tests`);
      setTests(response.data);
    } catch (error) {
      console.error('Failed to fetch lesson tests:', error);
    }
    setLoading(false);
  };

  const handleBackToCourse = () => {
    navigate(`/lessons/${course?.slug || course?.id}`);
  };

  const handleStartTest = (testId) => {
    navigate(`/test/${testId}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex justify-center items-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Header Section */}
      <div className="bg-gradient-to-r from-teal-500 to-teal-600 text-white py-8">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <button
            onClick={handleBackToCourse}
            className="mb-4 text-teal-100 hover:text-white flex items-center"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            ← Назад к {course?.title}
          </button>
          <h1 className="text-2xl md:text-3xl font-bold">{lesson.title}</h1>
        </div>
      </div>

      {/* Lesson Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Video Content */}
        {lesson.video_url && (
          <div className="mb-8">
            <div className="relative w-full" style={{ paddingBottom: '56.25%' }}>
              <iframe
                src={convertToEmbedUrl(lesson.video_url)}
                title={lesson.title}
                className="absolute top-0 left-0 w-full h-full rounded-lg"
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                allowFullScreen
                referrerPolicy="strict-origin-when-cross-origin"
              />
            </div>
          </div>
        )}

        {/* Text Content */}
        {lesson.content && (
          <div className="bg-white rounded-lg border border-gray-200 p-8 mb-8">
            <div className="prose max-w-none">
              <div dangerouslySetInnerHTML={{ __html: lesson.content }} />
            </div>
          </div>
        )}

        {/* Attachments */}
        {lesson.attachment_url && (
          <div className="bg-gray-50 rounded-lg p-6 mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Материалы к уроку</h3>
            <a
              href={lesson.attachment_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center text-teal-600 hover:text-teal-700 font-medium"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Скачать дополнительные материалы
            </a>
          </div>
        )}

        {/* Tests Section */}
        {tests.length > 0 && (
          <div className="bg-gradient-to-r from-teal-50 to-cyan-50 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Тесты к уроку</h3>
            <div className="space-y-3">
              {tests.map((test) => (
                <div key={test.id} className="flex items-center justify-between bg-white rounded-lg p-4 border border-gray-200">
                  <div>
                    <h4 className="font-medium text-gray-900">{test.title}</h4>
                    <p className="text-sm text-gray-600">
                      {test.questions_count} вопросов • {test.time_limit} мин • Проходной балл: {test.passing_score}%
                    </p>
                  </div>
                  <button
                    onClick={() => handleStartTest(test.id)}
                    className="bg-teal-500 text-white px-4 py-2 rounded-lg hover:bg-teal-600 transition-colors"
                  >
                    Начать тест
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Questions Section for Non-registered Users */}
        {!currentUser && (
          <div className="bg-gray-50 rounded-lg p-6 mt-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Вопросы к уроку</h3>
            <p className="text-gray-600 mb-4">Вы пока не задавали вопросов к этому уроку.</p>
            <p className="text-sm text-gray-500 mb-4">
              Вы смогли бы задавать вопросы учителям после регистрации
            </p>
            <p className="text-xs text-gray-400">
              Пожалуйста, убедитесь, что Ваш вопрос соответствует предмету {course?.title} и теме урока, 
              задан по существу и изложен полностью в одном сообщении.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};