import React from 'react';
import { useQuery } from 'react-query';
import { usersAPI, botsAPI, subscriptionsAPI, paymentsAPI } from '../services/api';
import {
  Users,
  Bot,
  CreditCard,
  DollarSign,
  TrendingUp,
  AlertCircle,
} from 'lucide-react';

const StatCard: React.FC<{
  title: string;
  value: string | number;
  icon: React.ComponentType<any>;
  color: string;
  change?: string;
}> = ({ title, value, icon: Icon, color, change }) => (
  <div className="card">
    <div className="flex items-center">
      <div className={`p-3 rounded-lg ${color}`}>
        <Icon className="h-6 w-6 text-white" />
      </div>
      <div className="ml-4">
        <p className="text-sm font-medium text-gray-600">{title}</p>
        <p className="text-2xl font-semibold text-gray-900">{value}</p>
        {change && (
          <p className="text-sm text-green-600 flex items-center">
            <TrendingUp className="h-4 w-4 mr-1" />
            {change}
          </p>
        )}
      </div>
    </div>
  </div>
);

export const Dashboard: React.FC = () => {
  const { data: usersData } = useQuery('users', () => usersAPI.list(1, 1));
  const { data: botsData } = useQuery('bots', () => botsAPI.list(1, 1));
  const { data: subscriptionsData } = useQuery('subscriptions', () => subscriptionsAPI.list(1, 1));
  const { data: paymentsData } = useQuery('payments', () => paymentsAPI.list(1, 1));
  const { data: pendingPayments } = useQuery('pending-payments', () => paymentsAPI.pending());
  const { data: expiringSubscriptions } = useQuery('expiring-subscriptions', () => subscriptionsAPI.expiring(7));

  const totalUsers = usersData?.data?.total || 0;
  const totalBots = botsData?.data?.total || 0;
  const totalSubscriptions = subscriptionsData?.data?.total || 0;
  const totalPayments = paymentsData?.data?.total || 0;
  const pendingPaymentsCount = pendingPayments?.data?.length || 0;
  const expiringCount = expiringSubscriptions?.data?.count || 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Overview of your Telegram Bot SaaS platform</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Users"
          value={totalUsers}
          icon={Users}
          color="bg-blue-500"
          change="+12% from last month"
        />
        <StatCard
          title="Active Bots"
          value={totalBots}
          icon={Bot}
          color="bg-green-500"
          change="+8% from last month"
        />
        <StatCard
          title="Subscriptions"
          value={totalSubscriptions}
          icon={CreditCard}
          color="bg-purple-500"
          change="+15% from last month"
        />
        <StatCard
          title="Total Revenue"
          value={`$${totalPayments * 9.99}`}
          icon={DollarSign}
          color="bg-yellow-500"
          change="+22% from last month"
        />
      </div>

      {/* Alerts */}
      {(pendingPaymentsCount > 0 || expiringCount > 0) && (
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Alerts</h3>
          <div className="space-y-3">
            {pendingPaymentsCount > 0 && (
              <div className="flex items-center p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <AlertCircle className="h-5 w-5 text-yellow-600 mr-3" />
                <div>
                  <p className="text-sm font-medium text-yellow-800">
                    {pendingPaymentsCount} payment(s) pending verification
                  </p>
                  <p className="text-sm text-yellow-600">
                    Review and approve payments in the Payments section
                  </p>
                </div>
              </div>
            )}
            {expiringCount > 0 && (
              <div className="flex items-center p-3 bg-red-50 border border-red-200 rounded-lg">
                <AlertCircle className="h-5 w-5 text-red-600 mr-3" />
                <div>
                  <p className="text-sm font-medium text-red-800">
                    {expiringCount} subscription(s) expiring in 7 days
                  </p>
                  <p className="text-sm text-red-600">
                    Send renewal reminders to users
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Recent Activity */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Users</h3>
          <div className="space-y-3">
            {usersData?.data?.items?.slice(0, 5).map((user: any) => (
              <div key={user.id} className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {user.first_name} {user.last_name}
                  </p>
                  <p className="text-sm text-gray-500">@{user.username}</p>
                </div>
                <span className="text-xs text-gray-500">
                  {new Date(user.created_at).toLocaleDateString()}
                </span>
              </div>
            )) || (
              <p className="text-sm text-gray-500">No recent users</p>
            )}
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Bots</h3>
          <div className="space-y-3">
            {botsData?.data?.items?.slice(0, 5).map((bot: any) => (
              <div key={bot.id} className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">{bot.bot_name}</p>
                  <p className="text-sm text-gray-500">{bot.github_repo}</p>
                </div>
                <span className={`badge ${
                  bot.status === 'running' ? 'badge-success' :
                  bot.status === 'error' ? 'badge-error' :
                  'badge-warning'
                }`}>
                  {bot.status}
                </span>
              </div>
            )) || (
              <p className="text-sm text-gray-500">No recent bots</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};