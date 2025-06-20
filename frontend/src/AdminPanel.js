import React, { useState, useEffect, createContext, useContext } from 'react';
import axios from 'axios';
import { StudentManagement, TeacherManagement, ApplicationManagement, ReportsComponent } from './AdminComponents';
import { LessonManagement, TestManagement } from './AdminLessonsTests';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Admin Context
const AdminContext = createContext();

export const useAdmin = () => {
  const context = useContext(AdminContext);
  if (!context) {
    throw new Error('useAdmin must be used within AdminProvider');
  }
  return context;
};

export const AdminProvider = ({ children }) => {
  const [adminUser, setAdminUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('adminToken'));

  useEffect(() => {
    if (token) {
      fetchAdminInfo();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchAdminInfo = async () => {
    try {
      const response = await axios.get(`${API}/admin/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAdminUser(response.data);
    } catch (error) {
      console.error('Failed to fetch admin info:', error);
      localStorage.removeItem('adminToken');
      setToken(null);
    }
    setLoading(false);
  };

  const login = async (username, password) => {
    try {
      console.log('Attempting login with:', username);
      const response = await axios.post(`${API}/admin/login`, {
        username,
        password
      });
      console.log('Login response:', response.data);
      const newToken = response.data.access_token;
      setToken(newToken);
      localStorage.setItem('adminToken', newToken);
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      console.error('Error response:', error.response?.data);
      return false;
    }
  };

  const logout = () => {
    setToken(null);
    setAdminUser(null);
    localStorage.removeItem('adminToken');
  };

  const value = {
    adminUser,
    token,
    login,
    logout,
    isAuthenticated: !!adminUser
  };

  return (
    <AdminContext.Provider value={value}>
      {!loading && children}
    </AdminContext.Provider>
  );
};

// Admin Login Component
export const AdminLogin = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAdmin();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const success = await login(username, password);
    if (success) {
      onLogin();
    } else {
      setError('Неверные учетные данные');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Вход в админ панель
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Панель управления "Уроки Ислама"
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Имя пользователя
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Пароль
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
              required
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-teal-600 hover:bg-teal-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-teal-500 disabled:opacity-50"
          >
            {loading ? 'Вход...' : 'Войти'}
          </button>
          <div className="text-sm text-gray-600 text-center">
            <p>По умолчанию: admin / admin123</p>
          </div>
        </form>
      </div>
    </div>
  );
};

// Admin Layout Component
export const AdminLayout = ({ children, currentPage, setCurrentPage }) => {
  const { adminUser, logout } = useAdmin();

  const menuItems = [
    { id: 'dashboard', name: 'Главная', icon: '📊' },
    { id: 'courses', name: 'Курсы', icon: '📚' },
    { id: 'lessons', name: 'Уроки', icon: '📖' },
    { id: 'tests', name: 'Тесты', icon: '📝' },
    { id: 'students', name: 'Ученики', icon: '👥' },
    { id: 'teachers', name: 'Преподаватели', icon: '👨‍🏫' },
    { id: 'applications', name: 'Заявки', icon: '📋' },
    { id: 'reports', name: 'Отчеты', icon: '📈' },
  ];

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-lg">
        <div className="p-4 border-b">
          <h1 className="text-xl font-bold text-gray-800">Админ панель</h1>
          <p className="text-sm text-gray-600">{adminUser?.full_name}</p>
        </div>
        
        <nav className="mt-4">
          {menuItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id)}
              className={`w-full text-left px-4 py-3 text-sm font-medium rounded-lg mx-2 mb-1 flex items-center space-x-3 ${
                currentPage === item.id
                  ? 'bg-teal-100 text-teal-700'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <span>{item.icon}</span>
              <span>{item.name}</span>
            </button>
          ))}
        </nav>

        <div className="absolute bottom-4 left-4 right-4">
          <button
            onClick={logout}
            className="w-full px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg flex items-center space-x-2"
          >
            <span>🚪</span>
            <span>Выйти</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <div className="p-6">
          {children}
        </div>
      </div>
    </div>
  );
};

// Dashboard Component
export const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const { token } = useAdmin();

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/admin/dashboard`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
    setLoading(false);
  };

  if (loading) {
    return <div className="flex justify-center py-12">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
    </div>;
  }

  const statCards = [
    { title: 'Всего студентов', value: stats?.total_students || 0, icon: '👥', color: 'bg-blue-500' },
    { title: 'Активные студенты', value: stats?.active_students || 0, icon: '✅', color: 'bg-green-500' },
    { title: 'Курсы', value: stats?.total_courses || 0, icon: '📚', color: 'bg-purple-500' },
    { title: 'Преподаватели', value: stats?.total_teachers || 0, icon: '👨‍🏫', color: 'bg-orange-500' },
    { title: 'Новые заявки', value: stats?.pending_applications || 0, icon: '📋', color: 'bg-red-500' },
    { title: 'Тесты сегодня', value: stats?.completed_tests_today || 0, icon: '📝', color: 'bg-teal-500' },
  ];

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Панель управления</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {statCards.map((card, index) => (
          <div key={index} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className={`${card.color} rounded-lg p-3 mr-4`}>
                <span className="text-white text-2xl">{card.icon}</span>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">{card.title}</p>
                <p className="text-2xl font-bold text-gray-900">{card.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Активность по дням</h3>
          <div className="text-center py-12 text-gray-500">
            <p>График активности</p>
            <p className="text-sm">(Будет реализован с библиотекой графиков)</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Популярные курсы</h3>
          <div className="text-center py-12 text-gray-500">
            <p>Статистика по курсам</p>
            <p className="text-sm">(Загружается...)</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Course Management Component
export const CourseManagement = () => {
  const [courses, setCourses] = useState([]);
  const [teachers, setTeachers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingCourse, setEditingCourse] = useState(null);
  const { token } = useAdmin();

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

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Название
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Преподаватель
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Сложность
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Статус
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Действия
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {courses.map((course) => (
              <tr key={course.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{course.title}</div>
                  <div className="text-sm text-gray-500">{course.description}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {course.teacher_name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    course.difficulty === 'Легко' ? 'bg-green-100 text-green-800' :
                    course.difficulty === 'Средне' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {course.difficulty}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    course.status === 'published' ? 'bg-green-100 text-green-800' :
                    course.status === 'draft' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {course.status === 'published' ? 'Опубликован' :
                     course.status === 'draft' ? 'Черновик' : 'Архив'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    onClick={() => handleEditCourse(course)}
                    className="text-teal-600 hover:text-teal-900 mr-3"
                  >
                    Редактировать
                  </button>
                  <button
                    onClick={() => handleDeleteCourse(course.id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    Удалить
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <CourseModal
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

// Course Modal Component
const CourseModal = ({ course, teachers, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    title: course?.title || '',
    description: course?.description || '',
    teacher_id: course?.teacher_id || '',
    teacher_name: course?.teacher_name || '',
    difficulty: course?.difficulty || 'Легко',
    duration_minutes: course?.duration_minutes || 15,
    questions_count: course?.questions_count || 5,
    image_url: course?.image_url || '',
    status: course?.status || 'draft'
  });
  const [loading, setLoading] = useState(false);
  const { token } = useAdmin();

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

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div className="mt-3">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            {course ? 'Редактировать курс' : 'Добавить курс'}
          </h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
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

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Сложность</label>
                <select
                  value={formData.difficulty}
                  onChange={(e) => setFormData({...formData, difficulty: e.target.value})}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                >
                  <option value="Легко">Легко</option>
                  <option value="Средне">Средне</option>
                  <option value="Сложно">Сложно</option>
                </select>
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

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Длительность (мин)</label>
                <input
                  type="number"
                  value={formData.duration_minutes}
                  onChange={(e) => setFormData({...formData, duration_minutes: parseInt(e.target.value)})}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                  min="1"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Количество вопросов</label>
                <input
                  type="number"
                  value={formData.questions_count}
                  onChange={(e) => setFormData({...formData, questions_count: parseInt(e.target.value)})}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                  min="1"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">URL изображения</label>
              <input
                type="url"
                value={formData.image_url}
                onChange={(e) => setFormData({...formData, image_url: e.target.value})}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
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

// Main Admin Panel Component
export const AdminPanel = () => {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const { isAuthenticated } = useAdmin();

  // Add debug logging
  console.log('AdminPanel rendered, isAuthenticated:', isAuthenticated);

  if (!isAuthenticated) {
    return <AdminLogin onLogin={() => setCurrentPage('dashboard')} />;
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <AdminDashboard />;
      case 'courses':
        return <CourseManagement />;
      case 'students':
        return <StudentManagement />;
      case 'teachers':
        return <TeacherManagement />;
      case 'applications':
        return <ApplicationManagement />;
      case 'reports':
        return <ReportsComponent />;
      default:
        return <AdminDashboard />;
    }
  };

  return (
    <AdminLayout currentPage={currentPage} setCurrentPage={setCurrentPage}>
      {renderPage()}
    </AdminLayout>
  );
};

export default AdminPanel;