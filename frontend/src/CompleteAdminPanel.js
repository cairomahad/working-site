import React, { useState, useEffect, createContext, useContext } from 'react';
import axios from 'axios';
import { useAuth } from './components';
import { ContentEditor } from './FormattedContent';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Complete Admin Context
const CompleteAdminContext = createContext();

export const useCompleteAdmin = () => {
  const context = useContext(CompleteAdminContext);
  if (!context) {
    throw new Error('useCompleteAdmin must be used within CompleteAdminProvider');
  }
  return context;
};

export const CompleteAdminProvider = ({ children }) => {
  const [loading, setLoading] = useState(true);
  const [adminUser, setAdminUser] = useState(null);
  const [token, setToken] = useState(null);

  useEffect(() => {
    const checkAuth = () => {
      const storedToken = localStorage.getItem('userToken');
      const userData = localStorage.getItem('userData');
      
      if (storedToken && userData) {
        try {
          const user = JSON.parse(userData);
          if (user.user_type === 'admin') {
            setAdminUser(user);
            setToken(storedToken);
          }
        } catch (error) {
          console.error('Error parsing user data:', error);
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  const value = {
    adminUser,
    token,
    isAuthenticated: !!adminUser
  };

  return (
    <CompleteAdminContext.Provider value={value}>
      {!loading && children}
    </CompleteAdminContext.Provider>
  );
};

// Image Upload Component
export const ImageUploader = ({ onUpload, currentImage, label = "Изображение" }) => {
  const [uploading, setUploading] = useState(false);
  const [preview, setPreview] = useState(currentImage);
  const { token } = useCompleteAdmin();

  const handleFileSelect = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Пожалуйста, выберите изображение');
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('Размер файла не должен превышать 5MB');
      return;
    }

    setUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(`${API}/admin/upload`, formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      const imageUrl = `${BACKEND_URL}${response.data.file_url}`;
      setPreview(imageUrl);
      onUpload(imageUrl);
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Ошибка загрузки изображения');
    }

    setUploading(false);
  };

  return (
    <div className="space-y-4">
      <label className="block text-sm font-medium text-gray-700">{label}</label>
      
      <div className="flex items-center space-x-4">
        {preview && (
          <div className="relative">
            <img
              src={preview}
              alt="Preview"
              className="w-24 h-24 object-cover rounded-lg border border-gray-300"
            />
          </div>
        )}
        
        <div className="flex-1">
          <input
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-teal-50 file:text-teal-700 hover:file:bg-teal-100"
            disabled={uploading}
          />
          {uploading && (
            <p className="text-sm text-gray-500 mt-1">Загрузка...</p>
          )}
        </div>
      </div>
    </div>
  );
};

// Enhanced Course Management
export const EnhancedCourseManagement = () => {
  const [courses, setCourses] = useState([]);
  const [teachers, setTeachers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingCourse, setEditingCourse] = useState(null);
  const [expandedCourse, setExpandedCourse] = useState(null);
  const [courseLessons, setCourseLessons] = useState({});
  const [showLessonModal, setShowLessonModal] = useState(false);
  const [editingLesson, setEditingLesson] = useState(null);
  const [currentCourseId, setCurrentCourseId] = useState(null);
  const { token } = useCompleteAdmin();

  useEffect(() => {
    fetchCourses();
    fetchTeachers();
  }, []);

  const fetchCourses = async () => {
    try {
      const response = await axios.get(`${API}/admin/courses`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCourses(response.data);
    } catch (error) {
      console.error('Failed to fetch courses:', error);
    }
    setLoading(false);
  };

  const fetchTeachers = async () => {
    try {
      const response = await axios.get(`${API}/admin/teachers`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setTeachers(response.data);
    } catch (error) {
      console.error('Failed to fetch teachers:', error);
    }
  };

  const fetchCourseLessons = async (courseId) => {
    try {
      const response = await axios.get(`${API}/admin/courses/${courseId}/lessons`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCourseLessons(prev => ({
        ...prev,
        [courseId]: response.data
      }));
    } catch (error) {
      console.error('Failed to fetch lessons:', error);
      setCourseLessons(prev => ({
        ...prev,
        [courseId]: []
      }));
    }
  };

  const handleCreateCourse = () => {
    setEditingCourse(null);
    setShowModal(true);
  };

  const handleEditCourse = (course) => {
    setEditingCourse(course);
    setShowModal(true);
  };

  const handleDeleteCourse = async (courseId) => {
    if (window.confirm('Вы уверены, что хотите удалить этот курс?')) {
      try {
        await axios.delete(`${API}/admin/courses/${courseId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        fetchCourses();
      } catch (error) {
        console.error('Failed to delete course:', error);
        alert('Ошибка удаления курса');
      }
    }
  };

  const handlePublishCourse = async (course) => {
    const newStatus = course.status === 'published' ? 'draft' : 'published';
    const action = newStatus === 'published' ? 'опубликовать' : 'снять с публикации';
    
    if (window.confirm(`Вы уверены, что хотите ${action} курс "${course.title}"?`)) {
      try {
        await axios.put(`${API}/admin/courses/${course.id}`, {
          status: newStatus
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });
        fetchCourses();
        alert(`Курс успешно ${newStatus === 'published' ? 'опубликован' : 'снят с публикации'}!`);
      } catch (error) {
        console.error('Failed to update course status:', error);
        alert('Ошибка изменения статуса курса');
      }
    }
  };

  const handleToggleExpanded = (courseId) => {
    if (expandedCourse === courseId) {
      setExpandedCourse(null);
    } else {
      setExpandedCourse(courseId);
      if (!courseLessons[courseId]) {
        fetchCourseLessons(courseId);
      }
    }
  };

  const handleCreateLesson = (courseId) => {
    setCurrentCourseId(courseId);
    setEditingLesson(null);
    setShowLessonModal(true);
  };

  const handleEditLesson = (lesson, courseId) => {
    setCurrentCourseId(courseId);
    setEditingLesson(lesson);
    setShowLessonModal(true);
  };

  const handleDeleteLesson = async (lessonId, courseId) => {
    if (window.confirm('Вы уверены, что хотите удалить этот урок?')) {
      try {
        await axios.delete(`${API}/admin/lessons/${lessonId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        fetchCourseLessons(courseId);
        fetchCourses(); // Обновляем счетчики уроков
      } catch (error) {
        console.error('Failed to delete lesson:', error);
        alert('Ошибка удаления урока');
      }
    }
  };

  const handleLessonSave = () => {
    setShowLessonModal(false);
    if (currentCourseId) {
      fetchCourseLessons(currentCourseId);
      fetchCourses(); // Обновляем счетчики уроков
    }
  };

  if (loading) {
    return <div className="flex justify-center py-12">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
    </div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Управление курсами и уроками</h1>
        <button
          onClick={handleCreateCourse}
          className="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700 flex items-center space-x-2"
        >
          <span>➕</span>
          <span>Добавить курс</span>
        </button>
      </div>

      {/* Courses List */}
      <div className="space-y-4">
        {courses.map((course) => (
          <div key={course.id} className="bg-white rounded-lg shadow-lg overflow-hidden">
            <div className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-xl font-bold text-gray-900">{course.title}</h3>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      course.status === 'published' ? 'bg-green-100 text-green-800' :
                      course.status === 'draft' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {course.status === 'published' ? 'Опубликован' :
                       course.status === 'draft' ? 'Черновик' : 'Архив'}
                    </span>
                    <span className="text-xs font-medium text-teal-600">
                      {course.level === 'level_1' ? '1-й уровень' :
                       course.level === 'level_2' ? '2-й уровень' : '3-й уровень'}
                    </span>
                  </div>
                  <p className="text-gray-600 mb-3">{course.description}</p>
                  
                  <div className="flex items-center space-x-6 text-sm text-gray-500 mb-4">
                    <span>📖 {course.lessons_count || 0} уроков</span>
                    <span>📝 {course.tests_count || 0} тестов</span>
                    <span>⏱️ {course.estimated_duration_hours}ч</span>
                    <span>👨‍🏫 {course.teacher_name || 'Не назначен'}</span>
                  </div>
                </div>
                
                <div className="flex flex-col space-y-2">
                  <button
                    onClick={() => handleEditCourse(course)}
                    className="bg-teal-100 text-teal-700 py-2 px-4 rounded text-sm hover:bg-teal-200 "
                  >
                    Редактировать
                  </button>
                  <button
                    onClick={() => handlePublishCourse(course)}
                    className={`py-2 px-4 rounded text-sm  ${
                      course.status === 'published' 
                        ? 'bg-orange-100 text-orange-700 hover:bg-orange-200' 
                        : 'bg-green-100 text-green-700 hover:bg-green-200'
                    }`}
                  >
                    {course.status === 'published' ? 'Снять с публикации' : 'Опубликовать'}
                  </button>
                </div>
              </div>
              
              <div className="flex justify-between items-center mt-4 pt-4 border-t">
                <button
                  onClick={() => handleToggleExpanded(course.id)}
                  className="flex items-center space-x-2 text-teal-600 hover:text-teal-800 font-medium"
                >
                  <span>{expandedCourse === course.id ? '📁' : '📂'}</span>
                  <span>
                    {expandedCourse === course.id ? 'Скрыть уроки' : 'Показать уроки'}
                  </span>
                </button>
                
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleCreateLesson(course.id)}
                    className="bg-blue-100 text-blue-700 py-2 px-3 rounded text-sm hover:bg-blue-200 "
                  >
                    + Добавить урок
                  </button>
                  <button
                    onClick={() => handleDeleteCourse(course.id)}
                    className="bg-red-100 text-red-700 py-2 px-3 rounded text-sm hover:bg-red-200 "
                  >
                    Удалить курс
                  </button>
                </div>
              </div>
            </div>
            
            {/* Lessons Section */}
            {expandedCourse === course.id && (
              <div className="border-t bg-gray-50 p-6">
                <h4 className="text-lg font-semibold text-gray-800 mb-4">
                  Уроки курса ({courseLessons[course.id]?.length || 0})
                </h4>
                
                {courseLessons[course.id] && courseLessons[course.id].length > 0 ? (
                  <div className="space-y-3">
                    {courseLessons[course.id].map((lesson, index) => (
                      <div key={lesson.id} className="bg-white rounded-lg p-4 shadow-sm">
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-3">
                              <span className="text-sm font-medium text-gray-500">
                                #{lesson.order || index + 1}
                              </span>
                              <h5 className="font-medium text-gray-900">{lesson.title}</h5>
                              <span className={`px-2 py-1 rounded text-xs ${
                                lesson.lesson_type === 'video' ? 'bg-blue-100 text-blue-800' :
                                lesson.lesson_type === 'text' ? 'bg-green-100 text-green-800' :
                                'bg-purple-100 text-purple-800'
                              }`}>
                                {lesson.lesson_type === 'video' ? 'Видео' :
                                 lesson.lesson_type === 'text' ? 'Текст' : 'Смешанный'}
                              </span>
                              <span className={`px-2 py-1 rounded text-xs ${
                                lesson.is_published ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                              }`}>
                                {lesson.is_published ? 'Опубликован' : 'Черновик'}
                              </span>
                            </div>
                            <p className="text-sm text-gray-600 mt-1">{lesson.description}</p>
                            <div className="flex items-center space-x-4 text-xs text-gray-500 mt-2">
                              <span>⏱️ {lesson.estimated_duration_minutes || 15} мин</span>
                              {lesson.video_url && <span>🎥 Видео</span>}
                            </div>
                          </div>
                          
                          <div className="flex space-x-2">
                            <button
                              onClick={() => handleEditLesson(lesson, course.id)}
                              className="text-teal-600 hover:text-teal-800 text-sm"
                            >
                              Редактировать
                            </button>
                            <button
                              onClick={() => handleDeleteLesson(lesson.id, course.id)}
                              className="text-red-600 hover:text-red-800 text-sm"
                            >
                              Удалить
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-gray-500 mb-4">В этом курсе пока нет уроков</p>
                    <button
                      onClick={() => handleCreateLesson(course.id)}
                      className="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700"
                    >
                      Создать первый урок
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {courses.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500 mb-4">Курсы не найдены</p>
          <button
            onClick={handleCreateCourse}
            className="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700"
          >
            Создать первый курс
          </button>
        </div>
      )}

      {/* Course Modal */}
      {showModal && (
        <EnhancedCourseModal
          course={editingCourse}
          teachers={teachers}
          onClose={() => setShowModal(false)}
          onSave={() => {
            setShowModal(false);
            fetchCourses();
          }}
        />
      )}

      {/* Lesson Modal */}
      {showLessonModal && (
        <LessonModal
          lesson={editingLesson}
          courseId={currentCourseId}
          courses={courses}
          onClose={() => setShowLessonModal(false)}
          onSave={handleLessonSave}
        />
      )}
    </div>
  );
};

// Enhanced Course Modal with Image Upload
const EnhancedCourseModal = ({ course, teachers, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    title: course?.title || '',
    description: course?.description || '',
    level: course?.level || 'level_1',
    teacher_id: course?.teacher_id || '',
    teacher_name: course?.teacher_name || '',
    difficulty: course?.difficulty || 'Начальный',
    estimated_duration_hours: course?.estimated_duration_hours || 20,
    image_url: course?.image_url || '',
    order: course?.order || 1,
    prerequisites: course?.prerequisites || [],
    status: course?.status || 'draft'
  });
  const [loading, setLoading] = useState(false);
  const { token } = useCompleteAdmin();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (course) {
        await axios.put(`${API}/admin/courses/${course.id}`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } else {
        await axios.post(`${API}/admin/courses`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
      onSave();
    } catch (error) {
      console.error('Failed to save course:', error);
      alert('Ошибка сохранения курса');
    }
    setLoading(false);
  };

  const handleTeacherChange = (e) => {
    const teacherId = e.target.value;
    const teacher = teachers.find(t => t.id === teacherId);
    setFormData({
      ...formData,
      teacher_id: teacherId,
      teacher_name: teacher?.name || ''
    });
  };

  const handleImageUpload = (imageUrl) => {
    setFormData({
      ...formData,
      image_url: imageUrl
    });
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
        <div className="mt-3">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            {course ? 'Редактировать курс' : 'Добавить курс'}
          </h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Image Upload */}
            <ImageUploader
              currentImage={formData.image_url}
              onUpload={handleImageUpload}
              label="Изображение курса"
            />

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Название</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Уровень</label>
                <select
                  value={formData.level}
                  onChange={(e) => setFormData({...formData, level: e.target.value})}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                >
                  <option value="level_1">1-й уровень (Основы)</option>
                  <option value="level_2">2-й уровень (Углубленное изучение)</option>
                  <option value="level_3">3-й уровень (Продвинутое изучение)</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Описание</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                rows="3"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Преподаватель</label>
              <select
                value={formData.teacher_id}
                onChange={handleTeacherChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                required
              >
                <option value="">Выберите преподавателя</option>
                {teachers.map((teacher) => (
                  <option key={teacher.id} value={teacher.id}>
                    {teacher.name} - {teacher.subject}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Сложность</label>
                <select
                  value={formData.difficulty}
                  onChange={(e) => setFormData({...formData, difficulty: e.target.value})}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                >
                  <option value="Начальный">Начальный</option>
                  <option value="Средний">Средний</option>
                  <option value="Продвинутый">Продвинутый</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Длительность (часы)</label>
                <input
                  type="number"
                  value={formData.estimated_duration_hours}
                  onChange={(e) => setFormData({...formData, estimated_duration_hours: parseInt(e.target.value)})}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                  min="1"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Порядок</label>
                <input
                  type="number"
                  value={formData.order}
                  onChange={(e) => setFormData({...formData, order: parseInt(e.target.value)})}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                  min="1"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Статус</label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData({...formData, status: e.target.value})}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                >
                  <option value="draft">Черновик</option>
                  <option value="published">Опубликован</option>
                  <option value="archived">Архив</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end space-x-3 mt-6">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
              >
                Отмена
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 text-sm font-medium text-white bg-teal-600 hover:bg-teal-700 rounded-md disabled:opacity-50"
              >
                {loading ? 'Сохранение...' : 'Сохранить'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

// Enhanced Teacher Management with Images
export const EnhancedTeacherManagement = () => {
  const [teachers, setTeachers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingTeacher, setEditingTeacher] = useState(null);
  const { token } = useCompleteAdmin();

  useEffect(() => {
    fetchTeachers();
  }, []);

  const fetchTeachers = async () => {
    try {
      const response = await axios.get(`${API}/admin/teachers`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setTeachers(response.data);
    } catch (error) {
      console.error('Failed to fetch teachers:', error);
    }
    setLoading(false);
  };

  const handleCreateTeacher = () => {
    setEditingTeacher(null);
    setShowModal(true);
  };

  const handleEditTeacher = (teacher) => {
    setEditingTeacher(teacher);
    setShowModal(true);
  };

  const handleDeleteTeacher = async (teacherId) => {
    if (window.confirm('Вы уверены, что хотите удалить этого преподавателя?')) {
      try {
        await axios.delete(`${API}/admin/teachers/${teacherId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        fetchTeachers();
      } catch (error) {
        console.error('Failed to delete teacher:', error);
        alert('Ошибка удаления преподавателя');
      }
    }
  };

  if (loading) {
    return <div className="flex justify-center py-12">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
    </div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Управление преподавателями</h1>
        <button
          onClick={handleCreateTeacher}
          className="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700 flex items-center space-x-2"
        >
          <span>➕</span>
          <span>Добавить преподавателя</span>
        </button>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {teachers.map((teacher) => (
          <div key={teacher.id} className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center space-x-4 mb-4">
              {teacher.image_url ? (
                <img
                  src={teacher.image_url}
                  alt={teacher.name}
                  className="w-16 h-16 rounded-full object-cover"
                />
              ) : (
                <div className="w-16 h-16 rounded-full bg-teal-100 flex items-center justify-center">
                  <span className="text-teal-600 text-xl font-bold">
                    {teacher.name.charAt(0).toUpperCase()}
                  </span>
                </div>
              )}
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900">{teacher.name}</h3>
                <p className="text-teal-600 font-medium">{teacher.subject}</p>
              </div>
            </div>
            
            {teacher.bio && (
              <p className="text-gray-600 text-sm mb-4">{teacher.bio}</p>
            )}
            
            <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
              <span>Email: {teacher.email}</span>
              <span className={`px-2 py-1 rounded-full text-xs ${
                teacher.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {teacher.is_active ? 'Активен' : 'Неактивен'}
              </span>
            </div>
            
            <div className="flex space-x-2">
              <button
                onClick={() => handleEditTeacher(teacher)}
                className="flex-1 bg-teal-100 text-teal-700 py-2 px-3 rounded text-sm hover:bg-teal-200"
              >
                Редактировать
              </button>
              <button
                onClick={() => handleDeleteTeacher(teacher.id)}
                className="bg-red-100 text-red-700 py-2 px-3 rounded text-sm hover:bg-red-200"
              >
                Удалить
              </button>
            </div>
          </div>
        ))}
      </div>

      {showModal && (
        <EnhancedTeacherModal
          teacher={editingTeacher}
          onClose={() => setShowModal(false)}
          onSave={() => {
            setShowModal(false);
            fetchTeachers();
          }}
        />
      )}
    </div>
  );
};

// Enhanced Teacher Modal with Image Upload
const EnhancedTeacherModal = ({ teacher, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    name: teacher?.name || '',
    email: teacher?.email || '',
    subject: teacher?.subject || '',
    bio: teacher?.bio || '',
    image_url: teacher?.image_url || ''
  });
  const [loading, setLoading] = useState(false);
  const { token } = useCompleteAdmin();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (teacher) {
        await axios.put(`${API}/admin/teachers/${teacher.id}`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } else {
        await axios.post(`${API}/admin/teachers`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
      onSave();
    } catch (error) {
      console.error('Failed to save teacher:', error);
      alert('Ошибка сохранения преподавателя');
    }
    setLoading(false);
  };

  const handleImageUpload = (imageUrl) => {
    setFormData({
      ...formData,
      image_url: imageUrl
    });
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div className="mt-3">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            {teacher ? 'Редактировать преподавателя' : 'Добавить преподавателя'}
          </h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Image Upload */}
            <ImageUploader
              currentImage={formData.image_url}
              onUpload={handleImageUpload}
              label="Фото преподавателя"
            />

            <div>
              <label className="block text-sm font-medium text-gray-700">Имя</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Email</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Предмет</label>
              <input
                type="text"
                value={formData.subject}
                onChange={(e) => setFormData({...formData, subject: e.target.value})}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Биография</label>
              <textarea
                value={formData.bio}
                onChange={(e) => setFormData({...formData, bio: e.target.value})}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                rows="3"
              />
            </div>

            <div className="flex justify-end space-x-3 mt-6">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
              >
                Отмена
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 text-sm font-medium text-white bg-teal-600 hover:bg-teal-700 rounded-md disabled:opacity-50"
              >
                {loading ? 'Сохранение...' : 'Сохранить'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

// Lesson Modal Component for Course Management
const LessonModal = ({ lesson, courseId, courses, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    course_id: courseId || lesson?.course_id || '',
    title: lesson?.title || '',
    description: lesson?.description || '',
    content: lesson?.content || '',
    lesson_type: lesson?.lesson_type || 'text',
    video_url: lesson?.video_url || '',
    video_duration: lesson?.video_duration || null,
    order: lesson?.order || 1,
    estimated_duration_minutes: lesson?.estimated_duration_minutes || 15,
    is_published: lesson?.is_published || false
  });
  const [loading, setLoading] = useState(false);
  const { token } = useCompleteAdmin();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Process form data for correct types
      const processedData = {
        ...formData,
        video_duration: formData.video_duration === '' || formData.video_duration === null ? null : parseInt(formData.video_duration),
        order: parseInt(formData.order),
        estimated_duration_minutes: parseInt(formData.estimated_duration_minutes)
      };

      if (lesson) {
        await axios.put(`${API}/admin/lessons/${lesson.id}`, processedData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } else {
        await axios.post(`${API}/admin/lessons`, processedData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
      onSave();
    } catch (error) {
      console.error('Failed to save lesson:', error);
      console.error('Error details:', error.response?.data);
      alert('Ошибка сохранения урока');
    }
    setLoading(false);
  };

  // Convert YouTube URL to embed format
  const convertToEmbedUrl = (url) => {
    if (!url) return '';
    
    // Already an embed URL
    if (url.includes('youtube.com/embed/')) return url;
    
    // Extract video ID from various YouTube URL formats
    let videoId = '';
    if (url.includes('youtube.com/watch?v=')) {
      videoId = url.split('youtube.com/watch?v=')[1].split('&')[0];
    } else if (url.includes('youtu.be/')) {
      videoId = url.split('youtu.be/')[1].split('?')[0];
    }
    
    return videoId ? `https://www.youtube.com/embed/${videoId}` : url;
  };

  const handleVideoUrlChange = (e) => {
    const url = e.target.value;
    const embedUrl = convertToEmbedUrl(url);
    setFormData({
      ...formData,
      video_url: embedUrl
    });
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-full max-w-3xl shadow-lg rounded-md bg-white">
        <div className="mt-3">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            {lesson ? 'Редактировать урок' : 'Добавить урок'}
          </h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Курс</label>
                <select
                  value={formData.course_id}
                  onChange={(e) => setFormData({...formData, course_id: e.target.value})}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                  required
                  disabled={!!courseId} // Disable if courseId is provided
                >
                  <option value="">Выберите курс</option>
                  {courses.map((course) => (
                    <option key={course.id} value={course.id}>
                      {course.title}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Тип урока</label>
                <select
                  value={formData.lesson_type}
                  onChange={(e) => setFormData({...formData, lesson_type: e.target.value})}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                >
                  <option value="text">Текстовый</option>
                  <option value="video">Видео</option>
                  <option value="mixed">Смешанный</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Название урока</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({...formData, title: e.target.value})}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Описание</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                rows="2"
              />
            </div>

            {(formData.lesson_type === 'video' || formData.lesson_type === 'mixed') && (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">URL видео</label>
                  <input
                    type="url"
                    value={formData.video_url}
                    onChange={handleVideoUrlChange}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                    placeholder="https://www.youtube.com/watch?v=..."
                  />
                  <p className="text-xs text-gray-500 mt-1">Поддерживаются YouTube ссылки</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Длительность видео (сек)</label>
                  <input
                    type="number"
                    value={formData.video_duration}
                    onChange={(e) => setFormData({...formData, video_duration: parseInt(e.target.value) || ''})}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                    placeholder="3600"
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700">Содержание урока</label>
              <textarea
                value={formData.content}
                onChange={(e) => setFormData({...formData, content: e.target.value})}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                rows="6"
                placeholder="Введите содержание урока в формате HTML или Markdown..."
                required
              />
              <p className="text-xs text-gray-500 mt-1">Поддерживается HTML разметка</p>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Порядок</label>
                <input
                  type="number"
                  value={formData.order}
                  onChange={(e) => setFormData({...formData, order: parseInt(e.target.value)})}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                  min="1"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Время изучения (мин)</label>
                <input
                  type="number"
                  value={formData.estimated_duration_minutes}
                  onChange={(e) => setFormData({...formData, estimated_duration_minutes: parseInt(e.target.value)})}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                  min="1"
                  required
                />
              </div>
              <div className="flex items-center">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.is_published}
                    onChange={(e) => setFormData({...formData, is_published: e.target.checked})}
                    className="mr-2 h-4 w-4 text-teal-600 focus:ring-teal-500 border-gray-300 rounded"
                  />
                  <span className="text-sm font-medium text-gray-700">Опубликовать</span>
                </label>
              </div>
            </div>

            <div className="flex justify-end space-x-3 mt-6">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
              >
                Отмена
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 text-sm font-medium text-white bg-teal-600 hover:bg-teal-700 rounded-md disabled:opacity-50"
              >
                {loading ? 'Сохранение...' : 'Сохранить'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default CompleteAdminProvider;