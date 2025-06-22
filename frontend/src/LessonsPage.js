import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from './components';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Main Lessons Page Component - similar to islam.school/lessons
export const LessonsPage = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
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

  const handleCourseClick = (course) => {
    navigate(`/lessons/${course.slug || course.id}`);
  };

  // Course subject images
  const getSubjectImage = (title) => {
    const titleLower = title.toLowerCase();
    if (titleLower.includes('основы') || titleLower.includes('вер')) {
      return 'https://images.pexels.com/photos/16126230/pexels-photo-16126230.jpeg';
    } else if (titleLower.includes('практик')) {
      return 'https://images.pexels.com/photos/16313080/pexels-photo-16313080.jpeg';
    } else if (titleLower.includes('этик')) {
      return 'https://images.unsplash.com/photo-1698043649093-05c5d835f290';
    } else if (titleLower.includes('истор')) {
      return 'https://images.unsplash.com/photo-1563827044778-badfd8b48a83';
    }
    return 'https://images.pexels.com/photos/16126230/pexels-photo-16126230.jpeg';
  };

  const getSubjectDescription = (title) => {
    const titleLower = title.toLowerCase();
    if (titleLower.includes('основы') || titleLower.includes('вер')) {
      return 'Чем ислам отличается от других религий. Во что верят мусульмане.';
    } else if (titleLower.includes('практик')) {
      return 'Основные ежедневные ритуалы в жизни мусульманина.';
    } else if (titleLower.includes('этик')) {
      return 'Отношения человека с Творцом, своей душой и окружением.';
    } else if (titleLower.includes('истор')) {
      return 'Мир от сотворения до конца времён. Пророки, Писания, цивилизации.';
    }
    return 'Изучение основ исламской религии и культуры.';
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
      <div className="bg-gradient-to-r from-teal-500 to-teal-600 text-white py-16">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">Уроки</h1>
          <p className="text-xl text-teal-100 max-w-2xl mx-auto">
            Изучайте ислам поэтапно с нашими структурированными курсами
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        
        {/* Progress Notification for Non-registered Users */}
        {!currentUser && (
          <div className="mb-8 p-4 bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-lg">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-amber-800">
                  Вы смогли бы сохранять и отслеживать прогресс после регистрации, а в конце обучения получить сертификат!
                </h3>
              </div>
            </div>
          </div>
        )}

        {/* Course Cards Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-2 gap-6 mb-12">
          {courses.map((course) => (
            <div
              key={course.id}
              className="bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition-all duration-300 cursor-pointer group"
              onClick={() => handleCourseClick(course)}
            >
              <div className="relative h-48">
                <img
                  src={course.image_url || getSubjectImage(course.title)}
                  alt={course.title}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
                <div className="absolute bottom-4 left-4 right-4">
                  <h3 className="text-white text-xl font-bold mb-1">{course.title}</h3>
                </div>
              </div>
              
              <div className="p-6">
                <p className="text-gray-600 mb-4 leading-relaxed">
                  {course.description || getSubjectDescription(course.title)}
                </p>
                
                <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                  <span className="flex items-center">
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C20.832 18.477 19.246 18 17.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                    {course.lessons_count || 0} уроков
                  </span>
                  <span className="flex items-center">
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {course.estimated_duration_hours}ч
                  </span>
                </div>

                {course.additional_materials && (
                  <div className="mb-4">
                    <a
                      href={course.additional_materials}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-teal-600 hover:text-teal-700 text-sm font-medium flex items-center"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      Дополнительная литература
                    </a>
                  </div>
                )}

                <button className="w-full bg-teal-500 text-white py-3 px-4 rounded-lg hover:bg-teal-600 transition-colors font-medium">
                  Начать изучение
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Additional Services Section */}
        <div className="bg-gradient-to-r from-teal-50 to-cyan-50 rounded-lg p-8 text-center">
          <div className="max-w-md mx-auto">
            <div className="w-20 h-20 mx-auto mb-4">
              <svg className="w-full h-full text-teal-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Консультация имама</h3>
            <p className="text-gray-600 mb-4">
              Получите персональные ответы на вопросы по исламу от квалифицированных преподавателей
            </p>
            <button className="bg-teal-500 text-white py-2 px-6 rounded-lg hover:bg-teal-600 transition-colors font-medium">
              Задать вопрос
            </button>
          </div>
        </div>
      </div>
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
export const LessonDetailPage = ({ lesson, course, setCurrentPage }) => {
  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const { currentUser } = useAuth();

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
    setCurrentPage('course-lessons');
  };

  const handleStartTest = (testId) => {
    setCurrentPage(`test-${testId}`);
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
                src={lesson.video_url}
                title={lesson.title}
                className="absolute top-0 left-0 w-full h-full rounded-lg"
                frameBorder="0"
                allowFullScreen
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