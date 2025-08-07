import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const UniversalTableEditor = () => {
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState(null);
  const [tableStructure, setTableStructure] = useState(null);
  const [tableData, setTableData] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [newRecord, setNewRecord] = useState({});

  const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  // Get auth token
  const getAuthToken = () => {
    return localStorage.getItem('userToken');
  };

  // Get auth headers
  const getAuthHeaders = () => {
    const token = getAuthToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  // Load all tables
  const loadTables = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get(`${API_BASE_URL}/api/admin/tables/list`, {
        headers: getAuthHeaders()
      });
      
      if (response.data.success) {
        setTables(response.data.tables);
      } else {
        setError('Failed to load tables');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load tables');
    } finally {
      setLoading(false);
    }
  }, [API_BASE_URL]);

  // Load table structure
  const loadTableStructure = useCallback(async (tableName) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get(`${API_BASE_URL}/api/admin/tables/${tableName}/structure`, {
        headers: getAuthHeaders()
      });
      
      if (response.data.success) {
        setTableStructure(response.data.structure);
      } else {
        setError('Failed to load table structure');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load table structure');
    } finally {
      setLoading(false);
    }
  }, [API_BASE_URL]);

  // Load table data
  const loadTableData = useCallback(async (tableName, page = 1, search = '') => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get(`${API_BASE_URL}/api/admin/tables/${tableName}/data`, {
        params: { page, limit: 20, search },
        headers: getAuthHeaders()
      });
      
      if (response.data.success) {
        setTableData(response.data.table_data.data || []);
        setCurrentPage(response.data.table_data.page);
        setTotalPages(response.data.table_data.total_pages);
      } else {
        setError('Failed to load table data');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load table data');
    } finally {
      setLoading(false);
    }
  }, [API_BASE_URL]);

  // Handle table selection
  const handleTableSelect = async (tableName) => {
    setSelectedTable(tableName);
    setCurrentPage(1);
    setSearchTerm('');
    await loadTableStructure(tableName);
    await loadTableData(tableName, 1, '');
  };

  // Handle search
  const handleSearch = (e) => {
    e.preventDefault();
    if (selectedTable) {
      loadTableData(selectedTable, 1, searchTerm);
    }
  };

  // Handle page change
  const handlePageChange = (page) => {
    if (selectedTable) {
      setCurrentPage(page);
      loadTableData(selectedTable, page, searchTerm);
    }
  };

  // Create new record
  const createRecord = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.post(`${API_BASE_URL}/api/admin/tables/${selectedTable}/records`, newRecord, {
        headers: getAuthHeaders()
      });
      
      if (response.data.success) {
        setSuccess('Record created successfully');
        setShowCreateModal(false);
        setNewRecord({});
        await loadTableData(selectedTable, currentPage, searchTerm);
      } else {
        setError('Failed to create record');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create record');
    } finally {
      setLoading(false);
    }
  };

  // Update record
  const updateRecord = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.put(`${API_BASE_URL}/api/admin/tables/${selectedTable}/records/${editingRecord.id}`, editingRecord, {
        headers: getAuthHeaders()
      });
      
      if (response.data.success) {
        setSuccess('Record updated successfully');
        setShowEditModal(false);
        setEditingRecord(null);
        await loadTableData(selectedTable, currentPage, searchTerm);
      } else {
        setError('Failed to update record');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update record');
    } finally {
      setLoading(false);
    }
  };

  // Delete record
  const deleteRecord = async (recordId) => {
    if (!window.confirm('Are you sure you want to delete this record?')) {
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.delete(`${API_BASE_URL}/api/admin/tables/${selectedTable}/records/${recordId}`, {
        headers: getAuthHeaders()
      });
      
      if (response.data.success) {
        setSuccess('Record deleted successfully');
        await loadTableData(selectedTable, currentPage, searchTerm);
      } else {
        setError('Failed to delete record');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete record');
    } finally {
      setLoading(false);
    }
  };

  // Initialize new record with default values
  const initializeNewRecord = () => {
    if (tableStructure?.columns) {
      const record = {};
      tableStructure.columns.forEach(column => {
        if (column.column_name !== 'id' && column.column_name !== 'created_at' && column.column_name !== 'updated_at') {
          record[column.column_name] = '';
        }
      });
      setNewRecord(record);
    }
  };

  // Format cell value for display
  const formatCellValue = (value) => {
    if (value === null || value === undefined) return '';
    if (typeof value === 'object') return JSON.stringify(value);
    if (typeof value === 'string' && value.length > 100) {
      return value.substring(0, 100) + '...';
    }
    return String(value);
  };

  // Load initial data
  useEffect(() => {
    loadTables();
  }, [loadTables]);

  // Clear messages after 5 seconds
  useEffect(() => {
    if (error || success) {
      const timer = setTimeout(() => {
        setError(null);
        setSuccess(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [error, success]);

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-6">
          🗃️ Универсальный редактор таблиц
        </h1>

        {/* Error/Success Messages */}
        {error && (
          <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}
        {success && (
          <div className="mb-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded">
            {success}
          </div>
        )}

        {/* Table Selection */}
        <div className="mb-6">
          <h2 className="text-lg font-semibold mb-3">Выберите таблицу:</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
            {tables.map((table) => (
              <button
                key={table.table_name}
                onClick={() => handleTableSelect(table.table_name)}
                className={`p-3 rounded-lg text-sm font-medium transition-colors ${
                  selectedTable === table.table_name
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                }`}
              >
                {table.table_name}
              </button>
            ))}
          </div>
        </div>

        {/* Table Content */}
        {selectedTable && (
          <div>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">
                Таблица: {selectedTable}
              </h2>
              <button
                onClick={() => {
                  initializeNewRecord();
                  setShowCreateModal(true);
                }}
                className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg"
              >
                ➕ Добавить запись
              </button>
            </div>

            {/* Search */}
            <form onSubmit={handleSearch} className="mb-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Поиск..."
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  type="submit"
                  className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg"
                >
                  🔍 Найти
                </button>
              </div>
            </form>

            {/* Loading */}
            {loading && (
              <div className="text-center py-4">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              </div>
            )}

            {/* Table Data */}
            {!loading && tableData.length > 0 && (
              <div className="overflow-x-auto">
                <table className="w-full border-collapse border border-gray-300">
                  <thead>
                    <tr className="bg-gray-100">
                      {tableStructure?.columns?.map((column) => (
                        <th key={column.column_name} className="border border-gray-300 px-4 py-2 text-left">
                          {column.column_name}
                          <span className="text-xs text-gray-500 ml-1">({column.data_type})</span>
                        </th>
                      )) || 
                      Object.keys(tableData[0] || {}).map((key) => (
                        <th key={key} className="border border-gray-300 px-4 py-2 text-left">
                          {key}
                        </th>
                      ))}
                      <th className="border border-gray-300 px-4 py-2 text-center">Действия</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tableData.map((row, index) => (
                      <tr key={row.id || index} className="hover:bg-gray-50">
                        {tableStructure?.columns?.map((column) => (
                          <td key={column.column_name} className="border border-gray-300 px-4 py-2">
                            {formatCellValue(row[column.column_name])}
                          </td>
                        )) || 
                        Object.keys(row).map((key) => (
                          <td key={key} className="border border-gray-300 px-4 py-2">
                            {formatCellValue(row[key])}
                          </td>
                        ))}
                        <td className="border border-gray-300 px-4 py-2 text-center">
                          <div className="flex justify-center gap-2">
                            <button
                              onClick={() => {
                                setEditingRecord({ ...row });
                                setShowEditModal(true);
                              }}
                              className="bg-blue-500 hover:bg-blue-600 text-white px-2 py-1 rounded text-xs"
                            >
                              ✏️ Изменить
                            </button>
                            <button
                              onClick={() => deleteRecord(row.id)}
                              className="bg-red-500 hover:bg-red-600 text-white px-2 py-1 rounded text-xs"
                            >
                              🗑️ Удалить
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* No Data */}
            {!loading && tableData.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                Нет данных для отображения
              </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="mt-4 flex justify-center">
                <div className="flex gap-2">
                  {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                    <button
                      key={page}
                      onClick={() => handlePageChange(page)}
                      className={`px-3 py-1 rounded ${
                        currentPage === page
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-200 hover:bg-gray-300 text-gray-700'
                      }`}
                    >
                      {page}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Create Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
              <h3 className="text-lg font-semibold mb-4">Создать новую запись</h3>
              <div className="space-y-4">
                {tableStructure?.columns?.map((column) => {
                  if (column.column_name === 'id' || column.column_name === 'created_at' || column.column_name === 'updated_at') {
                    return null;
                  }
                  return (
                    <div key={column.column_name}>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {column.column_name} ({column.data_type})
                      </label>
                      <input
                        type="text"
                        value={newRecord[column.column_name] || ''}
                        onChange={(e) => setNewRecord({ ...newRecord, [column.column_name]: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  );
                })}
              </div>
              <div className="flex justify-end gap-2 mt-6">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800"
                >
                  Отмена
                </button>
                <button
                  onClick={createRecord}
                  className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg"
                >
                  Создать
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Edit Modal */}
        {showEditModal && editingRecord && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
              <h3 className="text-lg font-semibold mb-4">Редактировать запись</h3>
              <div className="space-y-4">
                {tableStructure?.columns?.map((column) => {
                  if (column.column_name === 'created_at' || column.column_name === 'updated_at') {
                    return null;
                  }
                  return (
                    <div key={column.column_name}>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {column.column_name} ({column.data_type})
                      </label>
                      <input
                        type="text"
                        value={editingRecord[column.column_name] || ''}
                        onChange={(e) => setEditingRecord({ ...editingRecord, [column.column_name]: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        disabled={column.column_name === 'id'}
                      />
                    </div>
                  );
                })}
              </div>
              <div className="flex justify-end gap-2 mt-6">
                <button
                  onClick={() => setShowEditModal(false)}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800"
                >
                  Отмена
                </button>
                <button
                  onClick={updateRecord}
                  className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg"
                >
                  Сохранить
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default UniversalTableEditor;