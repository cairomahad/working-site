import React, { useState, useEffect, createContext, useContext } from 'react';
import axios from 'axios';
import { useAuth } from './components';

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

  if (loading) {
    return <div className="flex justify-center py-12">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
    </div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Управление курсами</h1>
        <button
          onClick={handleCreateCourse}
          className="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700 flex items-center space-x-2"
        >
          <span>➕</span>
          <span>Добавить курс</span>
        </button>
      </div>

      {/* Courses Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {courses.map((course) => (
          <div key={course.id} className="bg-white rounded-lg shadow-lg overflow-hidden">
            <div className="relative h-48">
              <img
                src={course.image_url || 'https://via.placeholder.com/400x200?text=Course'}
                alt={course.title}
                className="w-full h-full object-cover"
              />
              <div className="absolute top-2 right-2">
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  course.status === 'published' ? 'bg-green-100 text-green-800' :
                  course.status === 'draft' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {course.status === 'published' ? 'Опубликован' :
                   course.status === 'draft' ? 'Черновик' : 'Архив'}
                </span>
              </div>
            </div>
            
            <div className="p-4">
              <div className="mb-2">
                <span className="text-xs font-medium text-teal-600">
                  {course.level === 'level_1' ? '1-й уровень' :
                   course.level === 'level_2' ? '2-й уровень' : '3-й уровень'}
                </span>
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">{course.title}</h3>
              <p className="text-gray-600 text-sm mb-4 line-clamp-2">{course.description}</p>
              
              <div className="flex items-center justify-between text-xs text-gray-500 mb-4">
                <span>{course.lessons_count || 0} уроков</span>
                <span>{course.tests_count || 0} тестов</span>
                <span>{course.estimated_duration_hours}ч</span>
              </div>
              
              <div className="flex space-x-2">
                <button
                  onClick={() => handleEditCourse(course)}
                  className="flex-1 bg-teal-100 text-teal-700 py-2 px-3 rounded text-sm hover:bg-teal-200"
                >
                  Редактировать
                </button>
                <button
                  onClick={() => handleDeleteCourse(course.id)}
                  className="bg-red-100 text-red-700 py-2 px-3 rounded text-sm hover:bg-red-200"
                >
                  Удалить
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

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

export default CompleteAdminProvider;