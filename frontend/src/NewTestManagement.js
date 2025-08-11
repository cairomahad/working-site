import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useCompleteAdmin } from './CompleteAdminPanel';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const NewTestManagement = () => {
  const [tests, setTests] = useState([]);
  const [lessons, setLessons] = useState([]);
  const [courses, setCourses] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [selectedTest, setSelectedTest] = useState(null);
  const [loading, setLoading] = useState(false);
  const { token } = useCompleteAdmin();

  const [formData, setFormData] = useState({
    lesson_id: '',
    title: '',
    description: '',
    questions: [],
    time_limit_minutes: 10
  });

  const [newQuestion, setNewQuestion] = useState({
    question: '',
    options: ['', '', '', ''],
    correct: 0
  });

  // Load data
  const loadTests = async () => {
    try {
      const response = await axios.get(`${API}/admin/tests`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setTests(response.data);
    } catch (error) {
      console.error('Error loading tests:', error);
    }
  };

  const loadLessons = async () => {
    try {
      const response = await axios.get(`${API}/admin/lessons`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setLessons(response.data);
    } catch (error) {
      console.error('Error loading lessons:', error);
    }
  };

  const loadCourses = async () => {
    try {
      const response = await axios.get(`${API}/courses`);
      setCourses(response.data);
    } catch (error) {
      console.error('Error loading courses:', error);
    }
  };

  useEffect(() => {
    if (token) {
      loadTests();
      loadLessons();
      loadCourses();
    }
  }, [token]);

  // Form handlers
  const openModal = (test = null) => {
    if (test) {
      setFormData({
        lesson_id: test.lesson_id || '',
        title: test.title || '',
        description: test.description || '',
        questions: test.questions || [],
        time_limit_minutes: test.time_limit_minutes || 10
      });
      setSelectedTest(test);
    } else {
      setFormData({
        lesson_id: '',
        title: '',
        description: '',
        questions: [],
        time_limit_minutes: 10
      });
      setSelectedTest(null);
    }
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedTest(null);
    setNewQuestion({ question: '', options: ['', '', '', ''], correct: 0 });
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'time_limit_minutes' ? parseInt(value) : value
    }));
  };

  const handleQuestionChange = (e) => {
    const { name, value } = e.target;
    setNewQuestion(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleOptionChange = (index, value) => {
    setNewQuestion(prev => ({
      ...prev,
      options: prev.options.map((opt, i) => i === index ? value : opt)
    }));
  };

  const addQuestion = () => {
    if (!newQuestion.question.trim()) {
      alert('Введите текст вопроса');
      return;
    }

    if (newQuestion.options.some(opt => !opt.trim())) {
      alert('Заполните все варианты ответов');
      return;
    }

    const question = {
      question: newQuestion.question,
      options: [...newQuestion.options],
      correct: parseInt(newQuestion.correct)
    };

    setFormData(prev => ({
      ...prev,
      questions: [...prev.questions, question]
    }));

    setNewQuestion({ question: '', options: ['', '', '', ''], correct: 0 });
  };

  const removeQuestion = (index) => {
    setFormData(prev => ({
      ...prev,
      questions: prev.questions.filter((_, i) => i !== index)
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.title.trim() || !formData.lesson_id) {
      alert('Пожалуйста, заполните обязательные поля');
      return;
    }

    if (formData.questions.length === 0) {
      alert('Добавьте хотя бы один вопрос');
      return;
    }

    setLoading(true);
    try {
      if (selectedTest) {
        // Update existing test
        await axios.put(`${API}/admin/tests/${selectedTest.id}`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } else {
        // Create new test
        await axios.post(`${API}/admin/tests`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
      await loadTests();
      closeModal();
    } catch (error) {
      console.error('Error saving test:', error);
      alert('Ошибка при сохранении теста: ' + (error.response?.data?.detail || error.message));
    }
    setLoading(false);
  };

  const handleDelete = async (testId) => {
    if (!confirm('Вы уверены, что хотите удалить этот тест?')) return;

    try {
      await axios.delete(`${API}/admin/tests/${testId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      await loadTests();
    } catch (error) {
      console.error('Error deleting test:', error);
      alert('Ошибка при удалении теста');
    }
  };

  const getLessonName = (lessonId) => {
    const lesson = lessons.find(l => l.id === lessonId);
    return lesson ? lesson.title : 'Неизвестный урок';
  };

  const getCourseName = (lessonId) => {
    const lesson = lessons.find(l => l.id === lessonId);
    if (lesson) {
      const course = courses.find(c => c.id === lesson.course_id);
      return course ? course.title : 'Неизвестный курс';
    }
    return 'Неизвестный курс';
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Управление тестами</h2>
        <button
          onClick={() => openModal()}
          className="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700 "
        >
          + Добавить тест
        </button>
      </div>

      <div className="mb-4 text-sm text-gray-600 bg-blue-50 p-3 rounded-lg">
        💡 <strong>Система очков:</strong> За каждый пройденный тест участник получает 5 очков, независимо от результата.
        Лидерборд показывает участников с наибольшим количеством очков.
      </div>

      {/* Tests List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Название теста
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Урок
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Курс
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Вопросов
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Время
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Статус
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Действия
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {tests.map((test) => (
              <tr key={test.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{test.title}</div>
                  {test.description && (
                    <div className="text-sm text-gray-500 truncate max-w-xs">{test.description}</div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {getLessonName(test.lesson_id)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {getCourseName(test.lesson_id)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {test.questions?.length || 0}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {test.time_limit_minutes} мин
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    test.is_published ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {test.is_published ? 'Опубликован' : 'Черновик'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    onClick={() => openModal(test)}
                    className="text-indigo-600 hover:text-indigo-900 mr-3"
                  >
                    Редактировать
                  </button>
                  <button
                    onClick={() => handleDelete(test.id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    Удалить
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {tests.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">Тестов пока нет</p>
            <p className="text-gray-400">Создайте первый тест, нажав кнопку выше</p>
          </div>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b">
              <h3 className="text-lg font-semibold">
                {selectedTest ? 'Редактировать тест' : 'Создать тест'}
              </h3>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Урок *
                  </label>
                  <select
                    name="lesson_id"
                    value={formData.lesson_id}
                    onChange={handleInputChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                  >
                    <option value="">Выберите урок</option>
                    {lessons.map(lesson => (
                      <option key={lesson.id} value={lesson.id}>
                        {lesson.title}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Время (минуты)
                  </label>
                  <input
                    type="number"
                    name="time_limit_minutes"
                    value={formData.time_limit_minutes}
                    onChange={handleInputChange}
                    min="1"
                    max="120"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Название теста *
                </label>
                <input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="Введите название теста"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Описание
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="Краткое описание теста"
                />
              </div>

              {/* Questions Section */}
              <div className="border-t pt-6">
                <h4 className="text-lg font-medium mb-4">Вопросы теста</h4>
                
                {/* Existing Questions */}
                {formData.questions.length > 0 && (
                  <div className="mb-6">
                    <h5 className="text-sm font-medium text-gray-700 mb-3">Добавленные вопросы:</h5>
                    {formData.questions.map((question, index) => (
                      <div key={index} className="border border-gray-200 rounded-lg p-4 mb-3">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <p className="font-medium text-gray-900">{index + 1}. {question.question}</p>
                            <div className="mt-2 space-y-1">
                              {question.options.map((option, optIndex) => (
                                <div key={optIndex} className={`text-sm ${optIndex === question.correct ? 'text-green-600 font-medium' : 'text-gray-600'}`}>
                                  {String.fromCharCode(65 + optIndex)}) {option} {optIndex === question.correct && '✓'}
                                </div>
                              ))}
                            </div>
                          </div>
                          <button
                            type="button"
                            onClick={() => removeQuestion(index)}
                            className="text-red-600 hover:text-red-900 ml-2"
                          >
                            ✕
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Add New Question */}
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-4">
                  <h5 className="text-sm font-medium text-gray-700 mb-3">Добавить новый вопрос:</h5>
                  
                  <div className="mb-3">
                    <input
                      type="text"
                      name="question"
                      value={newQuestion.question}
                      onChange={handleQuestionChange}
                      placeholder="Введите текст вопроса"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-3 mb-3">
                    {newQuestion.options.map((option, index) => (
                      <input
                        key={index}
                        type="text"
                        value={option}
                        onChange={(e) => handleOptionChange(index, e.target.value)}
                        placeholder={`Вариант ${String.fromCharCode(65 + index)}`}
                        className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                      />
                    ))}
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <label className="block text-sm text-gray-700 mb-1">Правильный ответ:</label>
                      <select
                        name="correct"
                        value={newQuestion.correct}
                        onChange={handleQuestionChange}
                        className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                      >
                        <option value={0}>A</option>
                        <option value={1}>B</option>
                        <option value={2}>C</option>
                        <option value={3}>D</option>
                      </select>
                    </div>
                    <button
                      type="button"
                      onClick={addQuestion}
                      className="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700 "
                    >
                      Добавить вопрос
                    </button>
                  </div>
                </div>
              </div>

              <div className="flex justify-end space-x-3 pt-4 border-t">
                <button
                  type="button"
                  onClick={closeModal}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 "
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-6 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700  disabled:opacity-50"
                >
                  {loading ? 'Сохранение...' : 'Сохранить'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default NewTestManagement;