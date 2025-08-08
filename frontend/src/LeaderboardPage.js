import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const LeaderboardPage = () => {
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLeaderboard();
  }, []);

  const loadLeaderboard = async () => {
    try {
      const response = await axios.get(`${API}/leaderboard`);
      setLeaderboard(response.data);
    } catch (error) {
      console.error('Error loading leaderboard:', error);
    }
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Загрузка лидерборда...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">🏆 Лидерборд</h1>
          <p className="text-gray-600">Топ участников по количеству очков за пройденные тесты</p>
        </div>

        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          {leaderboard.length > 0 ? (
            <div className="divide-y divide-gray-200">
              {leaderboard.map((user, index) => (
                <div key={index} className={`p-6 flex items-center justify-between ${
                  index === 0 ? 'bg-gradient-to-r from-yellow-50 to-orange-50' :
                  index === 1 ? 'bg-gradient-to-r from-gray-50 to-gray-100' :
                  index === 2 ? 'bg-gradient-to-r from-orange-50 to-red-50' :
                  'bg-white'
                }`}>
                  <div className="flex items-center space-x-4">
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-lg ${
                      index === 0 ? 'bg-gradient-to-r from-yellow-400 to-yellow-600' :
                      index === 1 ? 'bg-gradient-to-r from-gray-400 to-gray-600' :
                      index === 2 ? 'bg-gradient-to-r from-orange-400 to-red-500' :
                      'bg-gray-400'
                    }`}>
                      {index === 0 ? '🥇' : 
                       index === 1 ? '🥈' : 
                       index === 2 ? '🥉' : 
                       user.rank}
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{user.user_name}</h3>
                      <p className="text-sm text-gray-600">
                        {user.tests_completed} тест{user.tests_completed === 1 ? '' : user.tests_completed < 5 ? 'а' : 'ов'} пройдено
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-teal-600">{user.total_points}</div>
                    <div className="text-sm text-gray-500">очков</div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🎯</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Пока никто не прошел тесты</h3>
              <p className="text-gray-600">Станьте первым, кто пройдет тест и получит очки!</p>
            </div>
          )}
        </div>

        <div className="mt-8 bg-blue-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">💡 Как набирать очки?</h3>
          <ul className="text-blue-800 space-y-1">
            <li>• Проходите тесты после изучения уроков</li>
            <li>• За каждый пройденный тест получаете +5 очков</li>
            <li>• Очки начисляются независимо от результата теста</li>
            <li>• Участвуйте в лидерборде и соревнуйтесь с другими учениками!</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default LeaderboardPage;