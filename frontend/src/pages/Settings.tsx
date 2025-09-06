import React from 'react';
import { Settings as SettingsIcon, Save } from 'lucide-react';

export const Settings: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-600">Configure platform settings</p>
        </div>
        <div className="flex items-center space-x-2">
          <SettingsIcon className="h-5 w-5 text-gray-400" />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* General Settings */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">General Settings</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Platform Name
              </label>
              <input
                type="text"
                defaultValue="Telegram Bot SaaS Platform"
                className="input mt-1"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Support Email
              </label>
              <input
                type="email"
                defaultValue="support@telegrambotsaas.com"
                className="input mt-1"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Max Bots Per User
              </label>
              <input
                type="number"
                defaultValue="10"
                className="input mt-1"
              />
            </div>
          </div>
          <div className="mt-6">
            <button className="btn btn-primary">
              <Save className="h-4 w-4 mr-2" />
              Save Changes
            </button>
          </div>
        </div>

        {/* Payment Settings */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Payment Settings</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Bank Account Number
              </label>
              <input
                type="text"
                defaultValue="1234567890"
                className="input mt-1"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Crypto Wallet Address
              </label>
              <input
                type="text"
                defaultValue="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
                className="input mt-1"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Default Currency
              </label>
              <select className="input mt-1">
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
                <option value="GBP">GBP</option>
              </select>
            </div>
          </div>
          <div className="mt-6">
            <button className="btn btn-primary">
              <Save className="h-4 w-4 mr-2" />
              Save Changes
            </button>
          </div>
        </div>

        {/* Notification Settings */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Notification Settings</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">
                  Email Notifications
                </label>
                <p className="text-sm text-gray-500">Send email notifications for important events</p>
              </div>
              <input type="checkbox" defaultChecked className="h-4 w-4 text-primary-600" />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">
                  Telegram Notifications
                </label>
                <p className="text-sm text-gray-500">Send Telegram notifications to admins</p>
              </div>
              <input type="checkbox" defaultChecked className="h-4 w-4 text-primary-600" />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">
                  Subscription Reminders
                </label>
                <p className="text-sm text-gray-500">Send reminders before subscription expires</p>
              </div>
              <input type="checkbox" defaultChecked className="h-4 w-4 text-primary-600" />
            </div>
          </div>
          <div className="mt-6">
            <button className="btn btn-primary">
              <Save className="h-4 w-4 mr-2" />
              Save Changes
            </button>
          </div>
        </div>

        {/* Security Settings */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Security Settings</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Session Timeout (minutes)
              </label>
              <input
                type="number"
                defaultValue="30"
                className="input mt-1"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Rate Limit (requests per minute)
              </label>
              <input
                type="number"
                defaultValue="100"
                className="input mt-1"
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">
                  Two-Factor Authentication
                </label>
                <p className="text-sm text-gray-500">Require 2FA for admin access</p>
              </div>
              <input type="checkbox" className="h-4 w-4 text-primary-600" />
            </div>
          </div>
          <div className="mt-6">
            <button className="btn btn-primary">
              <Save className="h-4 w-4 mr-2" />
              Save Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};