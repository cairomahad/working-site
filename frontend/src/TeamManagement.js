import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Компонент для загрузки изображений в base64
const ImageUploader = ({ onUpload, currentImage, label = "Изображение" }) => {
  const [preview, setPreview] = useState(currentImage);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Пожалуйста, выберите изображение');
      return;
    }

    // Validate file size (max 2MB)
    if (file.size > 2 * 1024 * 1024) {
      alert('Размер файла не должен превышать 2MB');
      return;
    }

    // Convert to base64
    const reader = new FileReader();
    reader.onload = (e) => {
      const base64String = e.target.result;
      setPreview(base64String);
      onUpload(base64String);
    };
    reader.readAsDataURL(file);
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
              className="w-24 h-24 object-cover rounded-full border border-gray-300"
            />
          </div>
        )}
        
        <div className="flex-1">
          <input
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-teal-50 file:text-teal-700 hover:file:bg-teal-100"
          />
        </div>
      </div>
    </div>
  );
};

// Форма создания/редактирования члена команды
const TeamMemberForm = ({ member, onSave, onCancel, token }) => {
  const [formData, setFormData] = useState({
    name: '',
    subject: '',
    image_base64: '',
    bio: '',
    email: '',
    order: 1,
    is_active: true
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (member) {
      setFormData({
        name: member.name || '',
        subject: member.subject || '',
        image_base64: member.image_base64 || member.image_url || '',
        bio: member.bio || '',
        email: member.email || '',
        order: member.order || 1,
        is_active: member.is_active !== undefined ? member.is_active : true
      });
    }
  }, [member]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const endpoint = member 
        ? `${API}/admin/team/${member.id}`
        : `${API}/admin/team`;
      
      const method = member ? 'PUT' : 'POST';
      
      const response = await axios({
        method,
        url: endpoint,
        data: formData,
        headers: { Authorization: `Bearer ${token}` }
      });

      onSave(response.data);
    } catch (error) {
      console.error('Ошибка сохранения:', error);
      alert('Ошибка сохранения члена команды');
    }
    setLoading(false);
  };

  const handleImageUpload = (base64String) => {
    setFormData(prev => ({
      ...prev,
      image_base64: base64String
    }));
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
        <div className="mt-3">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            {member ? 'Редактировать члена команды' : 'Добавить члена команды'}
          </h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Image Upload */}
            <ImageUploader
              currentImage={formData.image_base64}
              onUpload={handleImageUpload}
              label="Фото"
            />

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Имя *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Специализация *</label>
                <input
                  type="text"
                  value={formData.subject}
                  onChange={(e) => setFormData({...formData, subject: e.target.value})}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                  placeholder="Например: Этика, Основы веры"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Email</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Биография</label>
              <textarea
                value={formData.bio}
                onChange={(e) => setFormData({...formData, bio: e.target.value})}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                rows="3"
                placeholder="Краткое описание"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Порядок отображения</label>
                <input
                  type="number"
                  value={formData.order}
                  onChange={(e) => setFormData({...formData, order: parseInt(e.target.value)})}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                  min="1"
                  required
                />
              </div>

              <div className="flex items-center">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
                    className="mr-2"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    Активный
                  </span>
                </label>
              </div>
            </div>

            <div className="flex justify-end space-x-3 mt-6">
              <button
                type="button"
                onClick={onCancel}
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

// Основной компонент управления командой
export const TeamManagement = () => {
  const [teamMembers, setTeamMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingMember, setEditingMember] = useState(null);

  const token = localStorage.getItem('userToken');

  useEffect(() => {
    fetchTeamMembers();
  }, []);

  const fetchTeamMembers = async () => {
    try {
      const response = await axios.get(`${API}/admin/team`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setTeamMembers(response.data);
    } catch (error) {
      console.error('Ошибка загрузки команды:', error);
    }
    setLoading(false);
  };

  const handleCreateMember = () => {
    setEditingMember(null);
    setShowForm(true);
  };

  const handleEditMember = (member) => {
    setEditingMember(member);
    setShowForm(true);
  };

  const handleDeleteMember = async (memberId) => {
    if (window.confirm('Вы уверены, что хотите удалить этого члена команды?')) {
      try {
        await axios.delete(`${API}/admin/team/${memberId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        fetchTeamMembers();
        alert('Член команды успешно удален');
      } catch (error) {
        console.error('Ошибка удаления:', error);
        alert('Ошибка удаления члена команды');
      }
    }
  };

  const handleSave = () => {
    setShowForm(false);
    fetchTeamMembers();
    alert('Член команды успешно сохранен');
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Управление командой</h1>
        <button
          onClick={handleCreateMember}
          className="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700 flex items-center space-x-2"
        >
          <span>➕</span>
          <span>Добавить члена команды</span>
        </button>
      </div>

      {/* Team Members Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {teamMembers.map((member) => (
          <div key={member.id} className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center space-x-4 mb-4">
              {member.image_base64 || member.image_url ? (
                <img
                  src={member.image_base64 || member.image_url}
                  alt={member.name}
                  className="w-16 h-16 rounded-full object-cover"
                />
              ) : (
                <div className="w-16 h-16 rounded-full bg-teal-100 flex items-center justify-center">
                  <span className="text-teal-600 text-xl font-bold">
                    {member.name.charAt(0).toUpperCase()}
                  </span>
                </div>
              )}
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900">{member.name}</h3>
                <p className="text-teal-600 font-medium">{member.subject}</p>
                <p className="text-sm text-gray-500">Порядок: {member.order}</p>
              </div>
            </div>
            
            {member.bio && (
              <p className="text-gray-600 text-sm mb-4">{member.bio}</p>
            )}
            
            {member.email && (
              <p className="text-gray-500 text-sm mb-4">Email: {member.email}</p>
            )}

            <div className="flex items-center justify-between mb-4">
              <span className={`px-2 py-1 rounded-full text-xs ${
                member.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {member.is_active ? 'Активен' : 'Неактивен'}
              </span>
            </div>
            
            <div className="flex space-x-2">
              <button
                onClick={() => handleEditMember(member)}
                className="flex-1 bg-teal-100 text-teal-700 py-2 px-3 rounded text-sm hover:bg-teal-200"
              >
                Редактировать
              </button>
              <button
                onClick={() => handleDeleteMember(member.id)}
                className="bg-red-100 text-red-700 py-2 px-3 rounded text-sm hover:bg-red-200"
              >
                Удалить
              </button>
            </div>
          </div>
        ))}
      </div>

      {teamMembers.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-500">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Команда пуста</h3>
            <p className="text-gray-600">Добавьте первого члена команды, чтобы начать.</p>
          </div>
        </div>
      )}

      {showForm && (
        <TeamMemberForm
          member={editingMember}
          onSave={handleSave}
          onCancel={() => setShowForm(false)}
          token={token}
        />
      )}
    </div>
  );
};

export default TeamManagement;