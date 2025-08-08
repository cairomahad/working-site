import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useCompleteAdmin } from './CompleteAdminPanel';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const NewLessonManagement = () => {
  const [lessons, setLessons] = useState([]);
  const [courses, setCourses] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [selectedLesson, setSelectedLesson] = useState(null);
  const [loading, setLoading] = useState(false);
  const { token } = useCompleteAdmin();

  const [formData, setFormData] = useState({
    course_id: '',
    title: '',
    description: '',
    content: '',
    lesson_type: 'text',
    video_url: '',
    order: 1
  });

  // Load data
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
      loadLessons();
      loadCourses();
    }
  }, [token]);

  // Form handlers
  const openModal = (lesson = null) => {
    if (lesson) {
      setFormData({
        course_id: lesson.course_id || '',
        title: lesson.title || '',
        description: lesson.description || '',
        content: lesson.content || '',
        lesson_type: lesson.lesson_type || 'text',
        video_url: lesson.video_url || '',
        order: lesson.order || 1
      });
      setSelectedLesson(lesson);
    } else {
      setFormData({
        course_id: '',
        title: '',
        description: '',
        content: '',
        lesson_type: 'text',
        video_url: '',
        order: 1
      });
      setSelectedLesson(null);
    }
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedLesson(null);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.title.trim() || !formData.course_id) {
      alert('Пожалуйста, заполните обязательные поля');
      return;
    }

    setLoading(true);
    try {
      if (selectedLesson) {
        // Update existing lesson
        await axios.put(`${API}/admin/lessons/${selectedLesson.id}`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } else {
        // Create new lesson
        await axios.post(`${API}/admin/lessons`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
      await loadLessons();
      closeModal();
    } catch (error) {
      console.error('Error saving lesson:', error);
      alert('Ошибка при сохранении урока: ' + (error.response?.data?.detail || error.message));
    }
    setLoading(false);
  };

  const handleDelete = async (lessonId) => {
    if (!confirm('Вы уверены, что хотите удалить этот урок?')) return;

    try {
      await axios.delete(`${API}/admin/lessons/${lessonId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      await loadLessons();
    } catch (error) {
      console.error('Error deleting lesson:', error);
      alert('Ошибка при удалении урока');
    }
  };

  const getCourseName = (courseId) => {
    const course = courses.find(c => c.id === courseId);
    return course ? course.title : 'Неизвестный курс';
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Управление уроками</h2>
        <button
          onClick={() => openModal()}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          + Добавить урок
        </button>
      </div>

      {/* Lessons List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Название
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Курс
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Тип
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Порядок
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
            {lessons.map((lesson) => (
              <tr key={lesson.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{lesson.title}</div>
                  {lesson.description && (
                    <div className="text-sm text-gray-500 truncate max-w-xs">{lesson.description}</div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {getCourseName(lesson.course_id)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    lesson.lesson_type === 'video' ? 'bg-red-100 text-red-800' :
                    lesson.lesson_type === 'mixed' ? 'bg-purple-100 text-purple-800' :
                    'bg-blue-100 text-blue-800'
                  }`}>
                    {lesson.lesson_type === 'video' ? 'Видео' : 
                     lesson.lesson_type === 'mixed' ? 'Смешанный' : 'Текст'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {lesson.order}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    lesson.is_published ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {lesson.is_published ? 'Опубликован' : 'Черновик'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    onClick={() => openModal(lesson)}
                    className="text-indigo-600 hover:text-indigo-900 mr-3"
                  >
                    Редактировать
                  </button>
                  <button
                    onClick={() => handleDelete(lesson.id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    Удалить
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {lessons.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">Уроков пока нет</p>
            <p className="text-gray-400">Создайте первый урок, нажав кнопку выше</p>
          </div>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b">
              <h3 className="text-lg font-semibold">
                {selectedLesson ? 'Редактировать урок' : 'Создать урок'}
              </h3>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Курс *
                  </label>
                  <select
                    name="course_id"
                    value={formData.course_id}
                    onChange={handleInputChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Выберите курс</option>
                    {courses.map(course => (
                      <option key={course.id} value={course.id}>
                        {course.title}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Тип урока
                  </label>
                  <select
                    name="lesson_type"
                    value={formData.lesson_type}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="text">Текстовый</option>
                    <option value="video">Видео</option>
                    <option value="mixed">Смешанный</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Название урока *
                </label>
                <input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Введите название урока"
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
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Краткое описание урока"
                />
              </div>

              {(formData.lesson_type === 'video' || formData.lesson_type === 'mixed') && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    YouTube видео URL
                  </label>
                  <input
                    type="url"
                    name="video_url"
                    value={formData.video_url}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="https://www.youtube.com/watch?v=..."
                  />
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Содержание урока
                </label>
                <textarea
                  name="content"
                  value={formData.content}
                  onChange={handleInputChange}
                  rows={6}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Основное содержание урока..."
                />
              </div>

              <div className="w-32">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Порядок
                </label>
                <input
                  type="number"
                  name="order"
                  value={formData.order}
                  onChange={handleInputChange}
                  min="1"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-4 border-t">
                <button
                  type="button"
                  onClick={closeModal}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
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

export default NewLessonManagement;