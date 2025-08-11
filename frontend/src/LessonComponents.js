import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from './components';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Lesson View Component
export const LessonView = ({ lesson, setCurrentPage, setSelectedCourse }) => {
  const [lessonTests, setLessonTests] = useState([]);
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
      setLessonTests(response.data);
    } catch (error) {
      console.error('Failed to fetch lesson tests:', error);
    }
    setLoading(false);
  };

  const handleBackToCourse = () => {
    setCurrentPage('course-detail');
  };

  const handleTestClick = (test) => {
    setCurrentPage(`test-${test.id}`);
  };

  if (!lesson) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-500">Урок не найден</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-white to-teal-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Navigation */}
        <button
          onClick={handleBackToCourse}
          className="flex items-center text-teal-600 hover:text-teal-700 mb-6"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Назад к курсу
        </button>

        {/* Lesson Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <div className="flex items-center mb-4">
            <div className="w-12 h-12 bg-teal-100 rounded-full flex items-center justify-center mr-4">
              {lesson.lesson_type === 'video' ? '🎥' : 
               lesson.lesson_type === 'text' ? '📝' : '📚'}
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{lesson.title}</h1>
              <p className="text-gray-600">{lesson.description}</p>
            </div>
          </div>

          <div className="flex items-center space-x-6 text-sm text-gray-500">
            <span className="flex items-center">
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {lesson.estimated_duration_minutes} минут
            </span>
            <span className="flex items-center">
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {lesson.lesson_type === 'video' ? 'Видео урок' : 
               lesson.lesson_type === 'text' ? 'Текстовый урок' : 'Смешанный урок'}
            </span>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            {/* Video Player */}
            {lesson.video_url && (
              <div className="bg-white rounded-lg shadow-lg overflow-hidden mb-8">
                <div className="aspect-w-16 aspect-h-9">
                  <iframe
                    src={lesson.video_url}
                    title={lesson.title}
                    className="w-full h-64 lg:h-80"
                    frameBorder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                  ></iframe>
                </div>
              </div>
            )}

            {/* Lesson Content */}
            <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Содержание урока</h2>
              <div 
                className="prose max-w-none"
                dangerouslySetInnerHTML={{ __html: lesson.content }}
              ></div>
            </div>

            {/* Attachments */}
            {lesson.attachments && lesson.attachments.length > 0 && (
              <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                <h3 className="text-xl font-bold text-gray-900 mb-4">Материалы к уроку</h3>
                <div className="space-y-3">
                  {lesson.attachments.map((attachment) => (
                    <div key={attachment.id} className="flex items-center justify-between border border-gray-200 rounded-lg p-3">
                      <div className="flex items-center">
                        <div className="w-8 h-8 bg-teal-100 rounded flex items-center justify-center mr-3">
                          📎
                        </div>
                        <div>
                          <div className="font-medium text-gray-900">{attachment.filename}</div>
                          <div className="text-sm text-gray-500">
                            {attachment.file_type} • {Math.round(attachment.file_size / 1024)} KB
                          </div>
                        </div>
                      </div>
                      <a
                        href={attachment.file_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-teal-600 hover:text-teal-700 font-medium"
                      >
                        Скачать
                      </a>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            {/* Lesson Progress */}
            {currentUser && (
              <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
                <h3 className="text-xl font-bold text-gray-900 mb-4">Прогресс урока</h3>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Просмотрено</span>
                      <span>0%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-teal-500 h-2 rounded-full" style={{ width: '0%' }}></div>
                    </div>
                  </div>
                  <button className="w-full bg-teal-500 text-white py-2 px-4 rounded-lg hover:bg-teal-600 ">
                    Отметить как завершенный
                  </button>
                </div>
              </div>
            )}

            {/* Lesson Tests */}
            {lessonTests.length > 0 && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h3 className="text-xl font-bold text-gray-900 mb-4">Тесты к уроку</h3>
                <div className="space-y-3">
                  {lessonTests.map((test) => (
                    <div key={test.id} className="border border-gray-200 rounded-lg p-3">
                      <h4 className="font-medium text-gray-900 mb-1">{test.title}</h4>
                      <p className="text-sm text-gray-600 mb-3">{test.description}</p>
                      <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
                        <span>{test.questions.length} вопросов</span>
                        <span>{test.time_limit_minutes} мин</span>
                        <span>Проходной балл: {test.passing_score}%</span>
                      </div>
                      <button
                        onClick={() => handleTestClick(test)}
                        className="w-full bg-teal-500 text-white py-2 px-3 rounded hover:bg-teal-600  text-sm"
                        disabled={!currentUser}
                      >
                        {currentUser ? 'Пройти тест' : 'Войти для прохождения'}
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Test Taking Component
export const TestTaking = ({ testId, setCurrentPage }) => {
  const [test, setTest] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(0);
  const [showResult, setShowResult] = useState(false);
  const [score, setScore] = useState(0);
  const [loading, setLoading] = useState(true);
  const [testStarted, setTestStarted] = useState(false);
  const { currentUser } = useAuth();

  useEffect(() => {
    fetchTest();
  }, [testId]);

  useEffect(() => {
    if (testStarted && timeLeft > 0 && !showResult) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    } else if (timeLeft === 0 && testStarted && !showResult) {
      handleSubmitTest();
    }
  }, [timeLeft, testStarted, showResult]);

  const fetchTest = async () => {
    try {
      const response = await axios.get(`${API}/tests/${testId}`);
      setTest(response.data);
      setTimeLeft(response.data.time_limit_minutes * 60);
    } catch (error) {
      console.error('Failed to fetch test:', error);
    }
    setLoading(false);
  };

  const startTest = () => {
    setTestStarted(true);
  };

  const handleAnswerSelect = (questionId, optionId) => {
    setAnswers({
      ...answers,
      [questionId]: optionId
    });
  };

  const handleNextQuestion = () => {
    if (currentQuestion < test.questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const handlePrevQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const handleSubmitTest = () => {
    // Calculate score
    let correctAnswers = 0;
    test.questions.forEach((question) => {
      const userAnswer = answers[question.id];
      if (question.question_type === 'single_choice' || question.question_type === 'true_false') {
        const correctOption = question.options.find(opt => opt.is_correct);
        if (userAnswer === correctOption?.id) {
          correctAnswers++;
        }
      }
    });

    const finalScore = Math.round((correctAnswers / test.questions.length) * 100);
    setScore(finalScore);
    setShowResult(true);

    // Save test attempt (you can implement this API call)
    // saveTestAttempt(testId, answers, finalScore);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!currentUser) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-white to-teal-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Требуется авторизация</h2>
          <p className="text-gray-600 mb-6">Войдите в систему, чтобы проходить тесты</p>
          <button
            onClick={() => setCurrentPage('lessons')}
            className="bg-teal-500 text-white px-6 py-3 rounded-lg hover:bg-teal-600 "
          >
            Назад к урокам
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-white to-teal-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
      </div>
    );
  }

  if (!test) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-white to-teal-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Тест не найден</h2>
          <button
            onClick={() => setCurrentPage('lessons')}
            className="bg-teal-500 text-white px-6 py-3 rounded-lg hover:bg-teal-600 "
          >
            Назад к урокам
          </button>
        </div>
      </div>
    );
  }

  if (!testStarted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-white to-teal-50 flex items-center justify-center">
        <div className="bg-white rounded-2xl p-8 shadow-xl max-w-md w-full mx-4">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">{test.title}</h2>
            {test.description && (
              <p className="text-gray-600 mb-6">{test.description}</p>
            )}
            
            <div className="space-y-4 mb-6 text-left">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Вопросов:</span>
                <span className="font-medium">{test.questions.length}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Время:</span>
                <span className="font-medium">{test.time_limit_minutes} минут</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Проходной балл:</span>
                <span className="font-medium">{test.passing_score}%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Попыток:</span>
                <span className="font-medium">{test.max_attempts}</span>
              </div>
            </div>
            
            <button
              onClick={startTest}
              className="w-full bg-teal-500 text-white py-3 px-4 rounded-lg hover:bg-teal-600  font-medium"
            >
              Начать тест
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (showResult) {
    const isPassed = score >= test.passing_score;
    
    return (
      <div className="min-h-screen bg-gradient-to-br from-white to-teal-50 flex items-center justify-center">
        <div className="bg-white rounded-2xl p-8 shadow-xl max-w-md w-full mx-4">
          <div className="text-center">
            <div className="w-20 h-20 mx-auto mb-6">
              {isPassed ? (
                <div className="w-full h-full bg-green-100 rounded-full flex items-center justify-center">
                  <svg className="w-10 h-10 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              ) : (
                <div className="w-full h-full bg-red-100 rounded-full flex items-center justify-center">
                  <svg className="w-10 h-10 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </div>
              )}
            </div>
            
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              {isPassed ? 'Тест пройден!' : 'Тест не пройден'}
            </h2>
            <p className="text-gray-600 mb-6">
              {isPassed ? 'Поздравляем с успешным прохождением!' : 'Попробуйте еще раз!'}
            </p>
            
            <div className="space-y-2 mb-6 text-left bg-gray-50 rounded-lg p-4">
              <div className="flex justify-between">
                <span>Ваш результат:</span>
                <span className={`font-medium ${isPassed ? 'text-green-600' : 'text-red-600'}`}>
                  {score}%
                </span>
              </div>
              <div className="flex justify-between">
                <span>Проходной балл:</span>
                <span className="font-medium">{test.passing_score}%</span>
              </div>
              <div className="flex justify-between">
                <span>Правильных ответов:</span>
                <span className="font-medium">
                  {Math.round((score / 100) * test.questions.length)} из {test.questions.length}
                </span>
              </div>
            </div>
            
            <div className="space-y-3">
              <button
                onClick={() => setCurrentPage('lessons')}
                className="w-full bg-teal-500 text-white py-3 px-4 rounded-lg hover:bg-teal-600  font-medium"
              >
                Назад к урокам
              </button>
              {!isPassed && (
                <button
                  onClick={() => window.location.reload()}
                  className="w-full bg-gray-100 text-gray-700 py-3 px-4 rounded-lg hover:bg-gray-200  font-medium"
                >
                  Попробовать снова
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  const currentQ = test.questions[currentQuestion];

  return (
    <div className="min-h-screen bg-gradient-to-br from-white to-teal-50 py-12">
      <div className="max-w-2xl mx-auto px-4">
        {/* Header */}
        <div className="bg-white rounded-2xl p-6 shadow-lg mb-6">
          <div className="flex justify-between items-center mb-4">
            <h1 className="text-xl font-bold text-gray-900">{test.title}</h1>
            <div className="text-right">
              <div className="text-sm text-gray-600">Осталось времени</div>
              <div className={`text-lg font-bold ${timeLeft < 300 ? 'text-red-500' : 'text-teal-600'}`}>
                {formatTime(timeLeft)}
              </div>
            </div>
          </div>
          
          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-600">
              Вопрос {currentQuestion + 1} из {test.questions.length}
            </div>
          </div>
          
          <div className="w-full bg-gray-200 rounded-full h-2 mt-4">
            <div 
              className="bg-teal-500 h-2 rounded-full  duration-300"
              style={{ width: `${((currentQuestion + 1) / test.questions.length) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Question */}
        <div className="bg-white rounded-2xl p-8 shadow-lg">
          <h2 className="text-xl font-medium text-gray-900 mb-8">{currentQ.text}</h2>
          
          <div className="space-y-4 mb-8">
            {currentQ.options.map((option) => (
              <button
                key={option.id}
                onClick={() => handleAnswerSelect(currentQ.id, option.id)}
                className={`w-full p-4 text-left rounded-lg border-2  ${
                  answers[currentQ.id] === option.id
                    ? 'border-teal-500 bg-teal-50'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center">
                  <div className={`w-4 h-4 rounded-full border-2 mr-3 ${
                    answers[currentQ.id] === option.id
                      ? 'border-teal-500 bg-teal-500'
                      : 'border-gray-300'
                  }`}>
                    {answers[currentQ.id] === option.id && (
                      <div className="w-full h-full rounded-full bg-white scale-50"></div>
                    )}
                  </div>
                  <span className="text-gray-900">{option.text}</span>
                </div>
              </button>
            ))}
          </div>
          
          <div className="flex justify-between">
            <button
              onClick={handlePrevQuestion}
              disabled={currentQuestion === 0}
              className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50  disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Назад
            </button>
            
            {currentQuestion === test.questions.length - 1 ? (
              <button
                onClick={handleSubmitTest}
                className="px-6 py-3 bg-teal-500 text-white rounded-lg hover:bg-teal-600  font-medium"
              >
                Завершить тест
              </button>
            ) : (
              <button
                onClick={handleNextQuestion}
                className="px-6 py-3 bg-teal-500 text-white rounded-lg hover:bg-teal-600  font-medium"
              >
                Далее
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LessonView;