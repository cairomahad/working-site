import React, { useState, useCallback } from 'react';
import { useCompleteAdmin } from './CompleteAdminPanel';

// Drag & Drop File Upload Component
const FileDropZone = ({ onFilesSelected, acceptedTypes, maxSize, children }) => {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    const validFiles = files.filter(file => {
      if (acceptedTypes && !acceptedTypes.includes(file.type)) {
        alert(`Файл ${file.name} имеет неподдерживаемый тип: ${file.type}`);
        return false;
      }
      if (maxSize && file.size > maxSize) {
        alert(`Файл ${file.name} слишком большой. Максимум: ${Math.round(maxSize / (1024*1024))}MB`);
        return false;
      }
      return true;
    });
    
    if (validFiles.length > 0) {
      onFilesSelected(validFiles);
    }
  }, [onFilesSelected, acceptedTypes, maxSize]);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  return (
    <div
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
        isDragOver 
          ? 'border-teal-500 bg-teal-50' 
          : 'border-gray-300 hover:border-gray-400'
      }`}
    >
      {children}
    </div>
  );
};

// Video Upload Component
const VideoUploadSection = () => {
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [previewData, setPreviewData] = useState(null);
  const [isValidating, setIsValidating] = useState(false);
  const { token } = useCompleteAdmin();

  const validateYouTubeUrl = (url) => {
    const regex = /(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/;
    return regex.test(url);
  };

  const handleUrlChange = (e) => {
    const url = e.target.value;
    setYoutubeUrl(url);
    
    if (validateYouTubeUrl(url)) {
      setIsValidating(true);
      // Extract video ID for preview
      const videoId = url.match(/(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/)?.[1];
      
      if (videoId) {
        setPreviewData({
          videoId,
          title: 'YouTube видео',
          thumbnail: `https://img.youtube.com/vi/${videoId}/mqdefault.jpg`
        });
      }
      setIsValidating(false);
    } else {
      setPreviewData(null);
    }
  };

  const convertToEmbedUrl = (url) => {
    if (!url) return '';
    
    // If it's already an embed URL, return as is
    if (url.includes('youtube.com/embed/')) {
      return url;
    }
    
    // Extract video ID from various YouTube URL formats
    const videoIdMatch = url.match(/(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
    
    if (videoIdMatch && videoIdMatch[1]) {
      const videoId = videoIdMatch[1];
      return `https://www.youtube.com/embed/${videoId}`;
    }
    
    return url; // Return original URL if no match found
  };

  const handleVideoUpload = async (courseId, lessonId) => {
    if (!youtubeUrl || !validateYouTubeUrl(youtubeUrl)) {
      alert('Пожалуйста, введите корректную ссылку на YouTube видео');
      return;
    }

    try {
      const embedUrl = convertToEmbedUrl(youtubeUrl);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/lessons/${lessonId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          video_url: embedUrl
        })
      });

      if (response.ok) {
        alert('YouTube видео успешно добавлено к уроку!');
        setYoutubeUrl('');
        setPreviewData(null);
      } else {
        throw new Error('Ошибка при добавлении видео');
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Ошибка при загрузке видео');
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
      <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
        <span className="text-2xl mr-3">🎥</span>
        Добавление YouTube видео
      </h3>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Ссылка на YouTube видео
          </label>
          <input
            type="url"
            value={youtubeUrl}
            onChange={handleUrlChange}
            placeholder="https://www.youtube.com/watch?v=..."
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
          />
          {youtubeUrl && !validateYouTubeUrl(youtubeUrl) && (
            <p className="text-red-500 text-sm mt-1">Неверный формат ссылки YouTube</p>
          )}
        </div>

        {previewData && (
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Предпросмотр:</h4>
            <div className="flex items-center space-x-4">
              <img 
                src={previewData.thumbnail} 
                alt="YouTube thumbnail"
                className="w-32 h-24 object-cover rounded"
              />
              <div>
                <p className="font-medium">{previewData.title}</p>
                <p className="text-sm text-gray-600">Video ID: {previewData.videoId}</p>
                <p className="text-sm text-green-600">✅ Ссылка корректна</p>
              </div>
            </div>
          </div>
        )}

        <div className="bg-blue-50 rounded-lg p-4">
          <h4 className="font-medium text-blue-900 mb-2">💡 Инструкция:</h4>
          <ol className="text-sm text-blue-800 space-y-1">
            <li>1. Скопируйте ссылку на YouTube видео</li>
            <li>2. Вставьте в поле выше</li>
            <li>3. Выберите курс и урок для добавления</li>
            <li>4. Нажмите "Добавить к уроку"</li>
          </ol>
        </div>
      </div>
    </div>
  );
};

// Document Upload Component
const DocumentUploadSection = () => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const { token } = useCompleteAdmin();

  const acceptedDocTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  ];

  const handleFileUpload = async (files) => {
    setIsUploading(true);
    const uploadPromises = files.map(async (file) => {
      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/upload-enhanced`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: formData
        });

        if (response.ok) {
          const result = await response.json();
          return {
            ...result,
            originalName: file.name,
            uploadTime: new Date().toLocaleString()
          };
        } else {
          throw new Error(`Ошибка загрузки ${file.name}`);
        }
      } catch (error) {
        console.error('Upload error:', error);
        return { error: error.message, originalName: file.name };
      }
    });

    const results = await Promise.all(uploadPromises);
    setUploadedFiles(prev => [...prev, ...results]);
    setIsUploading(false);
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      handleFileUpload(files);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
      <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
        <span className="text-2xl mr-3">📄</span>
        Загрузка документов (PDF, DOCX)
      </h3>

      <FileDropZone
        onFilesSelected={handleFileUpload}
        acceptedTypes={acceptedDocTypes}
        maxSize={50 * 1024 * 1024} // 50MB
      >
        <div className="space-y-2">
          <div className="text-4xl text-gray-400">📁</div>
          <p className="text-lg font-medium text-gray-700">
            Перетащите файлы сюда или нажмите для выбора
          </p>
          <p className="text-sm text-gray-500">
            Поддерживаются: PDF, DOC, DOCX (до 50MB)
          </p>
          <input
            type="file"
            multiple
            accept=".pdf,.doc,.docx"
            onChange={handleFileSelect}
            className="hidden"
            id="doc-file-input"
          />
          <label
            htmlFor="doc-file-input"
            className="inline-block px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 cursor-pointer transition-colors"
          >
            Выбрать файлы
          </label>
        </div>
      </FileDropZone>

      {isUploading && (
        <div className="mt-4 p-4 bg-blue-50 rounded-lg">
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
            <span className="text-blue-700">Загрузка файлов...</span>
          </div>
        </div>
      )}

      {uploadedFiles.length > 0 && (
        <div className="mt-6">
          <h4 className="font-medium text-gray-900 mb-3">Загруженные файлы:</h4>
          <div className="space-y-2">
            {uploadedFiles.map((file, index) => (
              <div key={index} className={`p-3 rounded-lg border ${file.error ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'}`}>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">{file.originalName}</p>
                    {file.error ? (
                      <p className="text-red-600 text-sm">{file.error}</p>
                    ) : (
                      <div className="text-sm text-gray-600">
                        <p>Размер: {Math.round(file.file_size / 1024)} KB</p>
                        <p>Загружен: {file.uploadTime}</p>
                        <p className="text-teal-600">URL: {file.file_url}</p>
                      </div>
                    )}
                  </div>
                  <div className="text-2xl">
                    {file.error ? '❌' : '✅'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Test Import Component
const TestImportSection = () => {
  const [importedTests, setImportedTests] = useState([]);
  const [isImporting, setIsImporting] = useState(false);
  const [selectedCourse, setSelectedCourse] = useState('');
  const [courses, setCourses] = useState([]);
  const { token } = useCompleteAdmin();

  React.useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/courses`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await response.json();
      setCourses(data);
    } catch (error) {
      console.error('Failed to fetch courses:', error);
    }
  };

  const acceptedTestTypes = ['application/json', 'text/csv'];

  const handleTestImport = async (files) => {
    if (!selectedCourse) {
      alert('Пожалуйста, выберите курс для импорта тестов');
      return;
    }

    setIsImporting(true);
    
    for (const file of files) {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('course_id', selectedCourse);

      try {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/tests/import`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: formData
        });

        if (response.ok) {
          const result = await response.json();
          setImportedTests(prev => [...prev, {
            ...result,
            fileName: file.name,
            importTime: new Date().toLocaleString()
          }]);
        } else {
          const error = await response.json();
          alert(`Ошибка импорта ${file.name}: ${error.detail}`);
        }
      } catch (error) {
        console.error('Import error:', error);
        alert(`Ошибка импорта ${file.name}`);
      }
    }
    
    setIsImporting(false);
  };

  const createSampleJSON = () => {
    const sampleTest = {
      questions: [
        {
          text: "Сколько столпов веры в исламе?",
          question_type: "single_choice",
          options: [
            { text: "5", is_correct: false },
            { text: "6", is_correct: true },
            { text: "7", is_correct: false },
            { text: "8", is_correct: false }
          ],
          explanation: "В исламе шесть столпов веры",
          points: 1
        },
        {
          text: "Первый столп ислама - это...",
          question_type: "single_choice",
          options: [
            { text: "Намаз", is_correct: false },
            { text: "Шахада", is_correct: true },
            { text: "Закят", is_correct: false },
            { text: "Хадж", is_correct: false }
          ],
          explanation: "Шахада - свидетельство веры",
          points: 1
        }
      ]
    };

    const blob = new Blob([JSON.stringify(sampleTest, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sample_test.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
      <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
        <span className="text-2xl mr-3">📝</span>
        Импорт тестов (JSON, CSV)
      </h3>

      <div className="space-y-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Выберите курс для импорта тестов
          </label>
          <select
            value={selectedCourse}
            onChange={(e) => setSelectedCourse(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
          >
            <option value="">Выберите курс...</option>
            {courses.map(course => (
              <option key={course.id} value={course.id}>
                {course.title} ({course.level})
              </option>
            ))}
          </select>
        </div>

        <div className="flex space-x-2">
          <button
            onClick={createSampleJSON}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
          >
            📥 Скачать пример JSON
          </button>
        </div>
      </div>

      <FileDropZone
        onFilesSelected={handleTestImport}
        acceptedTypes={acceptedTestTypes}
        maxSize={10 * 1024 * 1024} // 10MB
      >
        <div className="space-y-2">
          <div className="text-4xl text-gray-400">📊</div>
          <p className="text-lg font-medium text-gray-700">
            Перетащите файлы тестов сюда
          </p>
          <p className="text-sm text-gray-500">
            Поддерживаются: JSON, CSV (до 10MB)
          </p>
          <p className="text-xs text-orange-600">
            ⚠️ Сначала выберите курс!
          </p>
        </div>
      </FileDropZone>

      {isImporting && (
        <div className="mt-4 p-4 bg-blue-50 rounded-lg">
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
            <span className="text-blue-700">Импорт тестов...</span>
          </div>
        </div>
      )}

      {importedTests.length > 0 && (
        <div className="mt-6">
          <h4 className="font-medium text-gray-900 mb-3">Импортированные тесты:</h4>
          <div className="space-y-2">
            {importedTests.map((test, index) => (
              <div key={index} className="p-3 rounded-lg bg-green-50 border border-green-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">{test.fileName}</p>
                    <div className="text-sm text-gray-600">
                      <p>Тест: {test.test?.title}</p>
                      <p>Вопросов: {test.questions_count}</p>
                      <p>Импортирован: {test.importTime}</p>
                    </div>
                  </div>
                  <div className="text-2xl">✅</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="mt-6 bg-yellow-50 rounded-lg p-4">
        <h4 className="font-medium text-yellow-900 mb-2">💡 Формат JSON файла:</h4>
        <pre className="text-xs text-yellow-800 bg-yellow-100 p-2 rounded overflow-x-auto">
{`{
  "questions": [
    {
      "text": "Вопрос?",
      "question_type": "single_choice",
      "options": [
        {"text": "Вариант 1", "is_correct": false},
        {"text": "Вариант 2", "is_correct": true}
      ],
      "explanation": "Объяснение",
      "points": 1
    }
  ]
}`}
        </pre>
      </div>
    </div>
  );
};

// Batch Operations Component
const BatchOperationsSection = () => {
  const [operations, setOperations] = useState([]);
  const { token } = useCompleteAdmin();

  const batchOperations = [
    {
      id: 'bulk_lesson_create',
      title: 'Массовое создание уроков',
      description: 'Создание нескольких уроков с файлами одновременно',
      icon: '📚'
    },
    {
      id: 'bulk_attachment',
      title: 'Массовое добавление материалов',
      description: 'Добавление множественных файлов к урокам',
      icon: '📎'
    },
    {
      id: 'course_archive',
      title: 'Архивирование курса',
      description: 'Создание архива всех материалов курса',
      icon: '📦'
    }
  ];

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
        <span className="text-2xl mr-3">⚡</span>
        Массовые операции
      </h3>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {batchOperations.map(operation => (
          <div key={operation.id} className="border border-gray-200 rounded-lg p-4 hover:border-teal-300 transition-colors">
            <div className="text-3xl mb-2">{operation.icon}</div>
            <h4 className="font-medium text-gray-900 mb-1">{operation.title}</h4>
            <p className="text-sm text-gray-600 mb-3">{operation.description}</p>
            <button className="w-full px-3 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors text-sm">
              Запустить
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

// Main Material Upload Panel Component
const MaterialUploadPanel = () => {
  return (
    <div className="space-y-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Загрузка материалов</h1>
        <p className="text-gray-600">Добавление видео, документов и тестов к курсам</p>
      </div>

      <VideoUploadSection />
      <DocumentUploadSection />
      <TestImportSection />
      <BatchOperationsSection />
    </div>
  );
};

export default MaterialUploadPanel;