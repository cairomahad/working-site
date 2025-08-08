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

  useEffect(() => {
    loadTest();
  }, [testId]);

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
      const submissionData = {
        user_id: currentUser?.email || `guest_${Date.now()}`,
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
        <div className="max-w-2xl mx-auto px-4">
          <div className="bg-white rounded-lg shadow-lg p-8 text-center">
            <div className="mb-6">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">🎉</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Тест завершен!</h2>
              <p className="text-gray-600">{result.message}</p>
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
                  <div className="text-2xl font-bold text-green-600">+{result.points_earned}</div>
                  <div className="text-xs text-gray-500">очков получено</div>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <button
                onClick={() => navigate('/leaderboard')}
                className="w-full bg-teal-600 text-white py-3 px-6 rounded-lg hover:bg-teal-700 transition-colors"
              >
                Посмотреть лидерборд
              </button>
              <button
                onClick={() => navigate(-1)}
                className="w-full bg-gray-200 text-gray-700 py-3 px-6 rounded-lg hover:bg-gray-300 transition-colors"
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
              <span>🏆 +5 очков за завершение</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-teal-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${(getAnsweredCount() / test.questions.length) * 100}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Name Input */}
        {!userName && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Представьтесь, пожалуйста</h3>
            <input
              type="text"
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              placeholder="Введите ваше имя"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
              onKeyPress={(e) => e.key === 'Enter' && userName.trim() && setUserName(userName.trim())}
            />
          </div>
        )}

        {/* Questions */}
        {userName && (
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
                  className="bg-teal-600 text-white px-8 py-3 rounded-lg hover:bg-teal-700 disabled:opacity-50 transition-colors flex items-center space-x-2"
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