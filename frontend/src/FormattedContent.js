import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

// Компонент для отображения богато форматированного текста
const FormattedContent = ({ content, className = "" }) => {
  // Кастомные компоненты для стилизации markdown
  const components = {
    // Заголовки
    h1: ({ children }) => (
      <h1 className="text-3xl font-bold text-gray-900 mb-6 leading-tight">
        {children}
      </h1>
    ),
    h2: ({ children }) => (
      <h2 className="text-2xl font-semibold text-gray-800 mb-4 mt-8 leading-tight">
        {children}
      </h2>
    ),
    h3: ({ children }) => (
      <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-6 leading-tight">
        {children}
      </h3>
    ),
    h4: ({ children }) => (
      <h4 className="text-lg font-medium text-gray-700 mb-2 mt-4">
        {children}
      </h4>
    ),
    
    // Параграфы с отступами
    p: ({ children }) => (
      <p className="text-gray-700 leading-relaxed mb-4 text-justify">
        {children}
      </p>
    ),
    
    // Жирный текст
    strong: ({ children }) => (
      <strong className="font-semibold text-gray-900">
        {children}
      </strong>
    ),
    
    // Курсив для цитат и акцентов
    em: ({ children }) => (
      <em className="italic text-gray-600 font-medium">
        {children}
      </em>
    ),
    
    // Списки
    ul: ({ children }) => (
      <ul className="list-disc list-inside mb-4 space-y-2 ml-4">
        {children}
      </ul>
    ),
    ol: ({ children }) => (
      <ol className="list-decimal list-inside mb-4 space-y-2 ml-4">
        {children}
      </ol>
    ),
    li: ({ children }) => (
      <li className="text-gray-700 leading-relaxed">
        {children}
      </li>
    ),
    
    // Цитаты
    blockquote: ({ children }) => (
      <blockquote className="border-l-4 border-teal-500 pl-6 py-2 my-6 bg-teal-50 rounded-r-lg">
        <div className="text-gray-700 italic">
          {children}
        </div>
      </blockquote>
    ),
    
    // Код
    code: ({ children, className }) => {
      const isInline = !className;
      
      if (isInline) {
        return (
          <code className="bg-gray-100 text-gray-800 px-2 py-1 rounded text-sm font-mono">
            {children}
          </code>
        );
      } else {
        return (
          <pre className="bg-gray-50 border border-gray-200 rounded-lg p-4 overflow-x-auto mb-4">
            <code className="text-gray-800 font-mono text-sm">
              {children}
            </code>
          </pre>
        );
      }
    },
    
    // Горизонтальная линия для разделения блоков
    hr: () => (
      <hr className="my-8 border-t border-gray-300" />
    ),
    
    // Ссылки
    a: ({ href, children }) => (
      <a 
        href={href}
        className="text-teal-600 hover:text-teal-700 underline font-medium"
        target="_blank"
        rel="noopener noreferrer"
      >
        {children}
      </a>
    ),
    
    // Таблицы
    table: ({ children }) => (
      <div className="overflow-x-auto mb-6">
        <table className="min-w-full divide-y divide-gray-200">
          {children}
        </table>
      </div>
    ),
    th: ({ children }) => (
      <th className="px-4 py-2 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
        {children}
      </th>
    ),
    td: ({ children }) => (
      <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-700 border-b border-gray-200">
        {children}
      </td>
    ),
  };

  // Если контент пустой
  if (!content) {
    return null;
  }

  // Если это обычный текст без markdown
  if (typeof content === 'string' && !content.includes('#') && !content.includes('*') && !content.includes('[')) {
    return (
      <div className={`prose max-w-none ${className}`}>
        {content.split('\n').map((line, index) => (
          <p key={index} className="text-gray-700 leading-relaxed mb-4 text-justify">
            {line}
          </p>
        ))}
      </div>
    );
  }

  return (
    <div className={`prose max-w-none ${className}`}>
      <ReactMarkdown
        components={components}
        remarkPlugins={[remarkGfm]}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

// Компонент для редактирования с предпросмотром
export const ContentEditor = ({ value, onChange, placeholder = "Введите содержание урока...", showPreview = true }) => {
  const [activeTab, setActiveTab] = React.useState('edit');

  return (
    <div className="w-full">
      {showPreview && (
        <div className="flex border-b border-gray-200 mb-4">
          <button
            type="button"
            className={`px-4 py-2 font-medium text-sm ${
              activeTab === 'edit'
                ? 'border-b-2 border-teal-500 text-teal-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setActiveTab('edit')}
          >
            Редактировать
          </button>
          <button
            type="button"
            className={`px-4 py-2 font-medium text-sm ${
              activeTab === 'preview'
                ? 'border-b-2 border-teal-500 text-teal-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setActiveTab('preview')}
          >
            Предпросмотр
          </button>
        </div>
      )}

      {(!showPreview || activeTab === 'edit') && (
        <div className="space-y-4">
          <div className="bg-teal-50 border border-teal-200 rounded-lg p-4 text-sm">
            <p className="font-medium text-teal-800 mb-2">📝 Форматирование текста:</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-teal-700">
              <div>• **жирный текст** для ключевых мыслей</div>
              <div>• *курсив* для цитат и акцентов</div>
              <div>• # Заголовок 1 ## Заголовок 2</div>
              <div>• - список или 1. нумерованный</div>
              <div>• {">"} цитата</div>
              <div>• --- разделитель</div>
            </div>
          </div>
          
          <textarea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder}
            className="w-full min-h-96 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent font-mono text-sm leading-relaxed"
            style={{ resize: 'vertical' }}
          />
        </div>
      )}

      {showPreview && activeTab === 'preview' && (
        <div className="border border-gray-200 rounded-lg p-6 bg-white min-h-96">
          {value ? (
            <FormattedContent content={value} />
          ) : (
            <p className="text-gray-400 italic text-center py-8">
              Содержание урока будет отображено здесь...
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default FormattedContent;