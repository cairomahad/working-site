import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from './components';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TestTakingComponent = () => {
  const { testId } = useParams();
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  
  const [test, setTest] = useState(null);
  const [answers, setAnswers] = useState({});
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [timeLeft, setTimeLeft] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [userName, setUserName] = useState('');
  const [showNameInput, setShowNameInput] = useState(false); // По умолчанию false, будет определено в useEffect

  // Generate consistent user ID based on full name
  const generateConsistentUserId = (fullName) => {
    if (currentUser?.email) {
      return currentUser.email;
    }
    
    // For guests, create consistent ID based on full name
    const cleanName = fullName.toLowerCase().trim().replace(/\s+/g, '_');
    
    // Get or create device ID from localStorage
    let deviceId = localStorage.getItem('device_id');
    if (!deviceId) {
      deviceId = Date.now().toString() + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('device_id', deviceId);
    }
    
    // Create consistent user ID: guest_[name]_[device_id]
    return `guest_${cleanName}_${deviceId}`;
  };

  const handleStartTest = () => {
    if (!userName.trim() || userName.trim().length < 3) {
      alert('Пожалуйста, введите ваше полное имя (минимум 3 символа)');
      return;
    }
    setShowNameInput(false);
  };

  useEffect(() => {
    loadTest();
  }, [testId]);

  // Автоматическое определение пользователя
  useEffect(() => {
    if (currentUser && currentUser.email) {
      // Зарегистрированный пользователь - автоматически используем его данные
      const displayName = currentUser.name || currentUser.displayName || currentUser.email.split('@')[0];
      setUserName(displayName);
      setShowNameInput(false); // Не показываем форму ввода имени
    } else {
      // Незарегистрированный пользователь - показываем форму ввода
      setShowNameInput(true);
    }
  }, [currentUser]);

  useEffect(() => {
    if (timeLeft > 0) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    } else if (timeLeft === 0 && test && !result) {
      handleSubmit(); // Auto-submit when time runs out
    }
  }, [timeLeft]);

  const loadTest = async () => {
    try {
      const response = await axios.get(`${API}/tests/${testId}`);
      setTest(response.data);
      setTimeLeft(response.data.time_limit_minutes * 60); // Convert to seconds
      setAnswers({});
    } catch (error) {
      console.error('Error loading test:', error);
      alert('Ошибка загрузки теста');
      navigate(-1);
    }
    setLoading(false);
  };

  const handleAnswerChange = (questionIndex, answerIndex) => {
    setAnswers(prev => ({
      ...prev,
      [`q${questionIndex}`]: answerIndex
    }));
  };

  const handleSubmit = async () => {
    if (!userName.trim()) {
      alert('Пожалуйста, введите ваше имя');
      return;
    }

    setSubmitting(true);
    try {
      const userId = generateConsistentUserId(userName.trim());
      
      const submissionData = {
        user_id: userId,
        user_name: userName.trim(),
        answers: answers
      };

      const response = await axios.post(`${API}/tests/${testId}/submit`, submissionData);
      setResult(response.data);
    } catch (error) {
      console.error('Error submitting test:', error);
      alert('Ошибка при отправке теста');
    }
    setSubmitting(false);
  };

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getAnsweredCount = () => {
    return Object.keys(answers).length;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Загрузка теста...</p>
        </div>
      </div>
    );
  }

  if (!test) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Тест не найден</h2>
          <button 
            onClick={() => navigate(-1)}
            className="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700"
          >
            Назад
          </button>
        </div>
      </div>
    );
  }

  if (result) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-4xl mx-auto px-4">
          <div className="bg-white rounded-lg shadow-lg p-8 text-center mb-8">
            <div className="mb-6">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">{result.is_retake ? '📝' : '🎉'}</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                {result.is_retake ? 'Тест завершен повторно!' : 'Тест завершен!'}
              </h2>
              <p className="text-gray-600">{result.message}</p>
              {result.is_retake && (
                <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <p className="text-sm text-yellow-800">
                    💡 Вы уже проходили этот тест ранее. Баллы начисляются только за первое прохождение.
                  </p>
                </div>
              )}
            </div>

            <div className="bg-gray-50 rounded-lg p-6 mb-6">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold text-teal-600">{result.score}</div>
                  <div className="text-sm text-gray-600">из {result.total_questions}</div>
                  <div className="text-xs text-gray-500">правильных</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-purple-600">{result.percentage.toFixed(1)}%</div>
                  <div className="text-xs text-gray-500">результат</div>
                </div>
                <div>
                  <div className={`text-2xl font-bold ${result.points_earned > 0 ? 'text-green-600' : 'text-gray-500'}`}>
                    {result.points_earned > 0 ? `+${result.points_earned}` : '0'}
                  </div>
                  <div className="text-xs text-gray-500">
                    {result.is_retake ? 'повтор' : 'очков получено'}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Correct Answers Section */}
          {result.correct_answers && (
            <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <span className="text-2xl mr-2">📋</span>
                Правильные ответы
              </h3>
              <div className="space-y-4">
                {result.correct_answers.map((answer, index) => (
                  <div key={index} className={`p-4 rounded-lg border-2 ${
                    answer.is_correct ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'
                  }`}>
                    <h4 className="font-medium text-gray-900 mb-3">
                      {index + 1}. {answer.question}
                    </h4>
                    <div className="space-y-2 text-sm">
                      {test && test.questions[index] && test.questions[index].options.map((option, optIndex) => (
                        <div key={optIndex} className={`flex items-center p-2 rounded ${
                          optIndex === answer.correct_answer ? 'bg-green-100 border border-green-300' :
                          optIndex === answer.user_answer && !answer.is_correct ? 'bg-red-100 border border-red-300' :
                          'bg-gray-50'
                        }`}>
                          <span className="font-medium text-gray-700 mr-2 w-6">
                            {String.fromCharCode(65 + optIndex)})
                          </span>
                          <span className="text-gray-900 flex-1">{option}</span>
                          {optIndex === answer.correct_answer && (
                            <span className="text-green-600 font-medium ml-2">✓ Правильно</span>
                          )}
                          {optIndex === answer.user_answer && optIndex !== answer.correct_answer && (
                            <span className="text-red-600 font-medium ml-2">✗ Ваш ответ</span>
                          )}
                        </div>
                      ))}
                    </div>
                    <div className="mt-2 text-sm">
                      <span className={`font-medium ${answer.is_correct ? 'text-green-600' : 'text-red-600'}`}>
                        {answer.is_correct ? '✓ Верно' : '✗ Неверно'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="space-y-3">
              <button
                onClick={() => window.location.reload()}
                className="w-full bg-orange-500 text-white py-3 px-6 rounded-lg hover:bg-orange-600  flex items-center justify-center space-x-2"
              >
                <span>🔄</span>
                <span>Пройти тест заново</span>
              </button>
              <button
                onClick={() => navigate('/leaderboard')}
                className="w-full bg-teal-600 text-white py-3 px-6 rounded-lg hover:bg-teal-700 "
              >
                Посмотреть лидерборд
              </button>
              <button
                onClick={() => navigate(-1)}
                className="w-full bg-gray-200 text-gray-700 py-3 px-6 rounded-lg hover:bg-gray-300 "
              >
                Вернуться к уроку
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{test.title}</h1>
              <p className="text-gray-600">{test.description}</p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-teal-600">
                {formatTime(timeLeft)}
              </div>
              <div className="text-sm text-gray-500">осталось времени</div>
            </div>
          </div>
          
          {/* Progress */}
          <div className="mt-4">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>Прогресс: {getAnsweredCount()} из {test.questions.length}</span>
              <span>🏆 5 очков за завершение + по 1 за правильный ответ (только первое прохождение)</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-teal-600 h-2 rounded-full  "
                style={{ width: `${(getAnsweredCount() / test.questions.length) * 100}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Name Input */}
        {showNameInput && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Представьтесь, пожалуйста</h3>
            <div className="space-y-4">
              <div>
                <input
                  type="text"
                  value={userName}
                  onChange={(e) => setUserName(e.target.value)}
                  placeholder="Введите ваше имя (например: Ахмед Магомедов)"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                  autoFocus
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      handleStartTest();
                    }
                  }}
                />
                <p className="text-sm text-gray-500 mt-2">
                  Введите ваше имя.
                </p>
              </div>
              <button
                onClick={handleStartTest}
                disabled={!userName.trim() || userName.trim().length < 3}
                className="w-full bg-teal-600 text-white py-3 px-6 rounded-lg hover:bg-teal-700 disabled:bg-gray-400 disabled:cursor-not-allowed "
              >
                Начать тест
              </button>
            </div>
          </div>
        )}

        {/* Questions */}
        {!showNameInput && (
          <div className="space-y-6">
            {test.questions.map((question, questionIndex) => (
              <div key={questionIndex} className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  {questionIndex + 1}. {question.question}
                </h3>
                
                <div className="space-y-3">
                  {question.options.map((option, optionIndex) => (
                    <label key={optionIndex} className="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                      <input
                        type="radio"
                        name={`question_${questionIndex}`}
                        value={optionIndex}
                        checked={answers[`q${questionIndex}`] === optionIndex}
                        onChange={() => handleAnswerChange(questionIndex, optionIndex)}
                        className="text-teal-600 focus:ring-teal-500 mr-3"
                      />
                      <span className="font-medium text-gray-700 mr-2">
                        {String.fromCharCode(65 + optionIndex)})
                      </span>
                      <span className="text-gray-900">{option}</span>
                    </label>
                  ))}
                </div>
              </div>
            ))}

            {/* Submit Button */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex justify-between items-center">
                <div className="text-sm text-gray-600">
                  Отвечено на {getAnsweredCount()} из {test.questions.length} вопросов
                </div>
                <button
                  onClick={handleSubmit}
                  disabled={submitting}
                  className="bg-teal-600 text-white px-8 py-3 rounded-lg hover:bg-teal-700 disabled:opacity-50  flex items-center space-x-2"
                >
                  {submitting ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Отправка...</span>
                    </>
                  ) : (
                    <>
                      <span>Завершить тест</span>
                      <span>🚀</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TestTakingComponent;