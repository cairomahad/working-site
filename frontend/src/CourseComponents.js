import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from './components';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Course Levels Component
export const CourseLevels = ({ setCurrentPage, setSelectedCourse }) => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const { currentUser } = useAuth();

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

  const groupCoursesByLevel = () => {
    const grouped = {
      level_1: courses.filter(course => course.level === 'level_1'),
      level_2: courses.filter(course => course.level === 'level_2'),
      level_3: courses.filter(course => course.level === 'level_3')
    };
    return grouped;
  };

  const getLevelTitle = (level) => {
    switch (level) {
      case 'level_1': return '1-й уровень (Основы)';
      case 'level_2': return '2-й уровень (Углубленное изучение)';
      case 'level_3': return '3-й уровень (Продвинутое изучение)';
      default: return 'Неизвестный уровень';
    }
  };

  const getLevelDescription = (level) => {
    switch (level) {
      case 'level_1': return 'Базовые знания об исламе для начинающих';
      case 'level_2': return 'Углубленное изучение исламских наук';
      case 'level_3': return 'Продвинутые курсы для опытных учеников';
      default: return '';
    }
  };

  const handleCourseClick = (course) => {
    setSelectedCourse(course);
    setCurrentPage('course-detail');
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
      </div>
    );
  }

  const groupedCourses = groupCoursesByLevel();

  return (
    <div className="min-h-screen bg-gradient-to-br from-white to-teal-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Образовательные курсы</h1>
          <p className="text-lg text-gray-600">Изучите ислам поэтапно - от основ до продвинутого уровня</p>
        </div>

        {/* Level Navigation */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          {['level_1', 'level_2', 'level_3'].map((level) => (
            <div key={level} className="bg-white rounded-lg p-6 shadow-lg text-center">
              <div className="w-16 h-16 bg-teal-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white text-2xl font-bold">
                  {level === 'level_1' ? '1' : level === 'level_2' ? '2' : '3'}
                </span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">{getLevelTitle(level)}</h3>
              <p className="text-gray-600 mb-4">{getLevelDescription(level)}</p>
              <p className="text-teal-600 font-medium">
                {groupedCourses[level].length} курсов
              </p>
            </div>
          ))}
        </div>

        {/* Courses by Level */}
        {['level_1', 'level_2', 'level_3'].map((level) => (
          <div key={level} className="mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-8">{getLevelTitle(level)}</h2>
            
            {groupedCourses[level].length === 0 ? (
              <div className="text-center py-12 bg-white rounded-lg shadow">
                <p className="text-gray-500">Курсы этого уровня скоро будут добавлены</p>
              </div>
            ) : (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {groupedCourses[level].map((course) => (
                  <CourseCard 
                    key={course.id} 
                    course={course} 
                    onClick={() => handleCourseClick(course)}
                    currentUser={currentUser}
                  />
                ))}
              </div>
            )}
          </div>
        ))}

        {/* Overall Progress */}
        {currentUser && (
          <div className="bg-white rounded-lg shadow-lg p-6 mt-12">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Ваш прогресс</h3>
            <div className="grid md:grid-cols-3 gap-4">
              {['level_1', 'level_2', 'level_3'].map((level) => (
                <div key={level} className="text-center">
                  <div className="text-2xl font-bold text-teal-600">
                    0/{groupedCourses[level].length}
                  </div>
                  <div className="text-sm text-gray-600">{getLevelTitle(level)}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Course Card Component
const CourseCard = ({ course, onClick, currentUser }) => {
  return (
    <div 
      className="bg-white rounded-lg shadow-lg hover:shadow-xl   overflow-hidden cursor-pointer group"
      onClick={onClick}
    >
      <div className="relative h-48">
        <img
          src={course.image_url || 'https://via.placeholder.com/400x200?text=Course'}
          alt={course.title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform "
        />
        <div className="absolute top-4 left-4">
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
            course.difficulty === 'Начальный' ? 'bg-green-100 text-green-800' :
            course.difficulty === 'Средний' ? 'bg-yellow-100 text-yellow-800' :
            'bg-red-100 text-red-800'
          }`}>
            {course.difficulty}
          </span>
        </div>
        <div className="absolute top-4 right-4">
          <span className="bg-white bg-opacity-90 px-2 py-1 rounded text-sm font-medium text-gray-700">
            {course.estimated_duration_hours}ч
          </span>
        </div>
      </div>
      
      <div className="p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-2">{course.title}</h3>
        <p className="text-gray-600 mb-4 line-clamp-2">{course.description}</p>
        
        <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
          <span className="flex items-center">
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C20.832 18.477 19.246 18 17.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            {course.lessons_count || 0} уроков
          </span>
          <span className="flex items-center">
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {course.tests_count || 0} тестов
          </span>
        </div>

        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <div className="w-8 h-8 rounded-full bg-teal-100 flex items-center justify-center mr-3">
              <span className="text-teal-600 text-sm font-medium">
                {course.teacher_name ? course.teacher_name.charAt(0) : 'T'}
              </span>
            </div>
            <span className="text-sm text-gray-600">{course.teacher_name}</span>
          </div>
        </div>
        
        <button className="w-full bg-teal-500 text-white py-2 px-4 rounded-lg hover:bg-teal-600  font-medium">
          {currentUser ? 'Начать изучение' : 'Войти для изучения'}
        </button>
      </div>
    </div>
  );
};

// Course Detail Component
export const CourseDetail = ({ course, setCurrentPage, setSelectedLesson }) => {
  const [lessons, setLessons] = useState([]);
  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const { currentUser } = useAuth();

  useEffect(() => {
    if (course) {
      fetchCourseContent();
    }
  }, [course]);

  const fetchCourseContent = async () => {
    try {
      const [lessonsResponse, testsResponse] = await Promise.all([
        axios.get(`${API}/courses/${course.id}/lessons`),
        axios.get(`${API}/courses/${course.id}/tests`)
      ]);
      
      setLessons(lessonsResponse.data);
      setTests(testsResponse.data);
    } catch (error) {
      console.error('Failed to fetch course content:', error);
    }
    setLoading(false);
  };

  const handleLessonClick = (lesson) => {
    setSelectedLesson(lesson);
    setCurrentPage('lesson-view');
  };

  const handleTestClick = (test) => {
    // Navigate to test page
    setCurrentPage(`test-${test.id}`);
  };

  if (!course) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-500">Курс не найден</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-white to-teal-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Back Button */}
        <button
          onClick={() => setCurrentPage('lessons')}
          className="flex items-center text-teal-600 hover:text-teal-700 mb-6"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Назад к курсам
        </button>

        {/* Course Header */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden mb-8">
          <div className="relative h-64">
            <img
              src={course.image_url || 'https://via.placeholder.com/800x300?text=Course'}
              alt={course.title}
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-black bg-opacity-40 flex items-end">
              <div className="p-6 text-white">
                <h1 className="text-3xl font-bold mb-2">{course.title}</h1>
                <p className="text-lg opacity-90">{course.description}</p>
              </div>
            </div>
          </div>
          
          <div className="p-6">
            <div className="grid md:grid-cols-4 gap-4 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-teal-600">{course.estimated_duration_hours}ч</div>
                <div className="text-sm text-gray-600">Длительность</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-teal-600">{lessons.length}</div>
                <div className="text-sm text-gray-600">Уроков</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-teal-600">{tests.length}</div>
                <div className="text-sm text-gray-600">Тестов</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-teal-600">{course.difficulty}</div>
                <div className="text-sm text-gray-600">Сложность</div>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-12 h-12 rounded-full bg-teal-100 flex items-center justify-center mr-4">
                  <span className="text-teal-600 font-medium">
                    {course.teacher_name ? course.teacher_name.charAt(0) : 'T'}
                  </span>
                </div>
                <div>
                  <div className="font-medium text-gray-900">{course.teacher_name}</div>
                  <div className="text-sm text-gray-600">Преподаватель</div>
                </div>
              </div>
              
              {currentUser && (
                <button className="bg-teal-500 text-white px-6 py-3 rounded-lg hover:bg-teal-600  font-medium">
                  Записаться на курс
                </button>
              )}
            </div>
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
          </div>
        ) : (
          <>
            {/* Course Content */}
            <div className="grid lg:grid-cols-3 gap-8">
              {/* Lessons */}
              <div className="lg:col-span-2">
                <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">Уроки курса</h2>
                  
                  {lessons.length === 0 ? (
                    <p className="text-gray-500 text-center py-8">Уроки скоро будут добавлены</p>
                  ) : (
                    <div className="space-y-4">
                      {lessons.map((lesson, index) => (
                        <LessonCard 
                          key={lesson.id} 
                          lesson={lesson} 
                          index={index}
                          onClick={() => handleLessonClick(lesson)}
                          currentUser={currentUser}
                        />
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Sidebar */}
              <div className="lg:col-span-1">
                {/* Course Tests */}
                <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
                  <h3 className="text-xl font-bold text-gray-900 mb-4">Тесты курса</h3>
                  
                  {tests.length === 0 ? (
                    <p className="text-gray-500 text-center py-4">Тесты скоро будут добавлены</p>
                  ) : (
                    <div className="space-y-3">
                      {tests.map((test) => (
                        <TestCard 
                          key={test.id} 
                          test={test} 
                          onClick={() => handleTestClick(test)}
                          currentUser={currentUser}
                        />
                      ))}
                    </div>
                  )}
                </div>

                {/* Progress */}
                {currentUser && (
                  <div className="bg-white rounded-lg shadow-lg p-6">
                    <h3 className="text-xl font-bold text-gray-900 mb-4">Прогресс</h3>
                    <div className="space-y-4">
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span>Завершено уроков</span>
                          <span>0/{lessons.length}</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div className="bg-teal-500 h-2 rounded-full" style={{ width: '0%' }}></div>
                        </div>
                      </div>
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span>Пройдено тестов</span>
                          <span>0/{tests.length}</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div className="bg-teal-500 h-2 rounded-full" style={{ width: '0%' }}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

// Lesson Card Component
const LessonCard = ({ lesson, index, onClick, currentUser }) => {
  return (
    <div 
      className="border border-gray-200 rounded-lg p-4 hover:border-teal-300 hover:shadow-md  cursor-pointer"
      onClick={onClick}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center flex-1">
          <div className="w-10 h-10 bg-teal-100 rounded-full flex items-center justify-center mr-4">
            <span className="text-teal-600 font-medium">{index + 1}</span>
          </div>
          <div className="flex-1">
            <h4 className="font-medium text-gray-900">{lesson.title}</h4>
            <p className="text-sm text-gray-600">{lesson.description}</p>
            <div className="flex items-center mt-2 space-x-4 text-xs text-gray-500">
              <span>⏱️ {lesson.estimated_duration_minutes} мин</span>
              <span>
                {lesson.lesson_type === 'video' ? '🎥 Видео' : 
                 lesson.lesson_type === 'text' ? '📝 Текст' : '📚 Смешанный'}
              </span>
            </div>
          </div>
        </div>
        
        <div className="flex items-center">
          {currentUser ? (
            <div className="w-6 h-6 border-2 border-gray-300 rounded-full"></div>
          ) : (
            <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          )}
        </div>
      </div>
    </div>
  );
};

// Test Card Component
const TestCard = ({ test, onClick, currentUser }) => {
  return (
    <div 
      className="border border-gray-200 rounded-lg p-3 hover:border-teal-300 hover:shadow-md  cursor-pointer"
      onClick={onClick}
    >
      <h4 className="font-medium text-gray-900 mb-1">{test.title}</h4>
      <div className="flex items-center justify-between text-xs text-gray-500">
        <span>{test.questions.length} вопросов</span>
        <span>{test.time_limit_minutes} мин</span>
      </div>
    </div>
  );
};

export default CourseLevels;