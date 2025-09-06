import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { botsAPI } from '../services/api';
import { Bot as BotIcon, Play, Square, RotateCcw, Search } from 'lucide-react';
import toast from 'react-hot-toast';

export const Bots: React.FC = () => {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery(
    ['bots', page],
    () => botsAPI.list(page, 10),
    {
      keepPreviousData: true,
    }
  );

  const startBotMutation = useMutation(botsAPI.start, {
    onSuccess: () => {
      toast.success('Bot started successfully');
      queryClient.invalidateQueries(['bots']);
    },
    onError: () => {
      toast.error('Failed to start bot');
    },
  });

  const stopBotMutation = useMutation(botsAPI.stop, {
    onSuccess: () => {
      toast.success('Bot stopped successfully');
      queryClient.invalidateQueries(['bots']);
    },
    onError: () => {
      toast.error('Failed to stop bot');
    },
  });

  const restartBotMutation = useMutation(botsAPI.restart, {
    onSuccess: () => {
      toast.success('Bot restarted successfully');
      queryClient.invalidateQueries(['bots']);
    },
    onError: () => {
      toast.error('Failed to restart bot');
    },
  });

  const bots = data?.data?.items || [];
  const total = data?.data?.total || 0;
  const totalPages = Math.ceil(total / 10);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'running':
        return 'badge-success';
      case 'stopped':
        return 'badge-warning';
      case 'error':
        return 'badge-error';
      case 'building':
        return 'badge-info';
      default:
        return 'badge-warning';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Failed to load bots</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Bot Instances</h1>
          <p className="text-gray-600">Manage deployed bot instances</p>
        </div>
        <div className="flex items-center space-x-2">
          <BotIcon className="h-5 w-5 text-gray-400" />
          <span className="text-sm text-gray-500">{total} total bots</span>
        </div>
      </div>

      {/* Search */}
      <div className="card">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search bots..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input pl-10"
          />
        </div>
      </div>

      {/* Bots Table */}
      <div className="card">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Bot
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Repository
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Health
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {bots.map((bot: any) => (
                <tr key={bot.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10">
                        <div className="h-10 w-10 rounded-full bg-green-100 flex items-center justify-center">
                          <BotIcon className="h-5 w-5 text-green-600" />
                        </div>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          {bot.bot_name}
                        </div>
                        <div className="text-sm text-gray-500">
                          ID: {bot.id.slice(0, 8)}...
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{bot.github_repo}</div>
                    <div className="text-sm text-gray-500">
                      Admin: {bot.admin_numeric_id}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`badge ${getStatusBadge(bot.status)}`}>
                      {bot.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`badge ${bot.is_healthy ? 'badge-success' : 'badge-error'}`}>
                      {bot.is_healthy ? 'Healthy' : 'Unhealthy'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(bot.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex items-center space-x-2">
                      {bot.status === 'stopped' && (
                        <button
                          onClick={() => startBotMutation.mutate(bot.id)}
                          disabled={startBotMutation.isLoading}
                          className="text-green-600 hover:text-green-900"
                          title="Start Bot"
                        >
                          <Play className="h-4 w-4" />
                        </button>
                      )}
                      {bot.status === 'running' && (
                        <button
                          onClick={() => stopBotMutation.mutate(bot.id)}
                          disabled={stopBotMutation.isLoading}
                          className="text-red-600 hover:text-red-900"
                          title="Stop Bot"
                        >
                          <Square className="h-4 w-4" />
                        </button>
                      )}
                      <button
                        onClick={() => restartBotMutation.mutate(bot.id)}
                        disabled={restartBotMutation.isLoading}
                        className="text-blue-600 hover:text-blue-900"
                        title="Restart Bot"
                      >
                        <RotateCcw className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
            <div className="flex-1 flex justify-between sm:hidden">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
                className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
              >
                Previous
              </button>
              <button
                onClick={() => setPage(Math.min(totalPages, page + 1))}
                disabled={page === totalPages}
                className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
              >
                Next
              </button>
            </div>
            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-gray-700">
                  Showing <span className="font-medium">{(page - 1) * 10 + 1}</span> to{' '}
                  <span className="font-medium">{Math.min(page * 10, total)}</span> of{' '}
                  <span className="font-medium">{total}</span> results
                </p>
              </div>
              <div>
                <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                  <button
                    onClick={() => setPage(Math.max(1, page - 1))}
                    disabled={page === 1}
                    className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                  >
                    Previous
                  </button>
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    const pageNum = Math.max(1, Math.min(totalPages - 4, page - 2)) + i;
                    return (
                      <button
                        key={pageNum}
                        onClick={() => setPage(pageNum)}
                        className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                          pageNum === page
                            ? 'z-10 bg-primary-50 border-primary-500 text-primary-600'
                            : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                        }`}
                      >
                        {pageNum}
                      </button>
                    );
                  })}
                  <button
                    onClick={() => setPage(Math.min(totalPages, page + 1))}
                    disabled={page === totalPages}
                    className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                  >
                    Next
                  </button>
                </nav>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};