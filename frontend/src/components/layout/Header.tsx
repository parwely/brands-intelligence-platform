// frontend/src/components/layout/Header.tsx
'use client'
import React, { useState, useEffect } from 'react'
import { Bell, Search, User, Menu, Settings, AlertTriangle } from 'lucide-react'
import { apiService } from '@/services/api'

interface HeaderProps {
  onMenuClick?: () => void
}

export function Header({ onMenuClick }: HeaderProps) {
  const [notifications, setNotifications] = useState(0)
  const [crisisAlerts, setCrisisAlerts] = useState(0)
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [systemStatus, setSystemStatus] = useState<'online' | 'offline' | 'warning'>('online')

  useEffect(() => {
    const loadAlerts = async () => {
      try {
        const { total_alerts } = await apiService.getCrisisAlerts(0.7);
        setCrisisAlerts(total_alerts);
        setNotifications(total_alerts + 2); // Add some general notifications
      } catch (error) {
        console.error('Failed to load alerts:', error);
        setSystemStatus('warning');
      }
    };

    loadAlerts();
    const interval = setInterval(loadAlerts, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement search functionality
    console.log('Searching for:', searchQuery);
  };

  return (
    <div className="sticky top-0 z-40 lg:mx-auto lg:max-w-7xl lg:px-8">
      <div className="flex h-16 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-0 lg:shadow-none">
        {/* Mobile menu button */}
        <button
          type="button"
          className="-m-2.5 p-2.5 text-gray-700 lg:hidden"
          onClick={onMenuClick}
        >
          <span className="sr-only">Open sidebar</span>
          <Menu className="h-6 w-6" aria-hidden="true" />
        </button>

        {/* Separator */}
        <div className="h-6 w-px bg-gray-900/10 lg:hidden" aria-hidden="true" />

        <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
          {/* Search */}
          <form className="relative flex flex-1" onSubmit={handleSearch}>
            <label htmlFor="search-field" className="sr-only">
              Search
            </label>
            <Search
              className="pointer-events-none absolute inset-y-0 left-0 h-full w-5 text-gray-400 ml-3"
              aria-hidden="true"
            />
            <input
              id="search-field"
              className="block h-full w-full border-0 py-0 pl-10 pr-0 text-gray-900 placeholder:text-gray-400 focus:ring-0 sm:text-sm"
              placeholder="Search brands, mentions, or keywords..."
              type="search"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </form>

          <div className="flex items-center gap-x-4 lg:gap-x-6">
            {/* Crisis Alert Button */}
            <button
              type="button"
              className={`relative rounded-full p-2 ${
                crisisAlerts > 0 
                  ? 'bg-red-50 text-red-600 hover:text-red-500' 
                  : 'bg-gray-50 text-gray-400'
              } focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2`}
              title={`${crisisAlerts} Crisis Alerts`}
            >
              <span className="sr-only">View crisis alerts</span>
              <AlertTriangle className="h-6 w-6" />
              {crisisAlerts > 0 && (
                <span className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-red-500 text-xs text-white flex items-center justify-center font-medium">
                  {crisisAlerts > 9 ? '9+' : crisisAlerts}
                </span>
              )}
            </button>

            {/* Notifications button */}
            <button
              type="button"
              className="relative -m-2.5 p-2.5 text-gray-400 hover:text-gray-500"
            >
              <span className="sr-only">View notifications</span>
              <Bell className="h-6 w-6" aria-hidden="true" />
              {notifications > 0 && (
                <span className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-indigo-500 text-xs text-white flex items-center justify-center">
                  {notifications > 9 ? '9+' : notifications}
                </span>
              )}
            </button>

            {/* Separator */}
            <div
              className="hidden lg:block lg:h-6 lg:w-px lg:bg-gray-900/10"
              aria-hidden="true"
            />

            {/* Profile dropdown */}
            <div className="relative">
              <button
                type="button"
                className="-m-1.5 flex items-center p-1.5"
                onClick={() => setIsProfileMenuOpen(!isProfileMenuOpen)}
              >
                <span className="sr-only">Open user menu</span>
                <div className="h-8 w-8 rounded-full bg-indigo-500 flex items-center justify-center">
                  <User className="h-5 w-5 text-white" />
                </div>
                <span className="hidden lg:flex lg:items-center">
                  <span className="ml-4 text-sm font-semibold leading-6 text-gray-900">
                    Brand Manager
                  </span>
                  <svg
                    className="ml-2 h-5 w-5 text-gray-400"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z"
                      clipRule="evenodd"
                    />
                  </svg>
                </span>
              </button>

              {/* Profile dropdown menu */}
              {isProfileMenuOpen && (
                <div className="absolute right-0 z-10 mt-2.5 w-48 origin-top-right rounded-md bg-white py-2 shadow-lg ring-1 ring-gray-900/5">
                  <a href="#" className="block px-3 py-1 text-sm leading-6 text-gray-900 hover:bg-gray-50">
                    Your profile
                  </a>
                  <a href="#" className="block px-3 py-1 text-sm leading-6 text-gray-900 hover:bg-gray-50">
                    Settings
                  </a>
                  <a href="#" className="block px-3 py-1 text-sm leading-6 text-gray-900 hover:bg-gray-50">
                    API Documentation
                  </a>
                  <div className="border-t border-gray-100 my-1"></div>
                  <a href="#" className="block px-3 py-1 text-sm leading-6 text-gray-900 hover:bg-gray-50">
                    Sign out
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Real-time status bar */}
      <div className={`px-4 py-2 ${
        systemStatus === 'online' 
          ? 'bg-gradient-to-r from-green-400 to-blue-500' 
          : systemStatus === 'warning'
          ? 'bg-gradient-to-r from-yellow-400 to-orange-500'
          : 'bg-gradient-to-r from-red-400 to-red-600'
      }`}>
        <div className="flex items-center justify-between text-white text-sm">
          <div className="flex items-center space-x-4">
            <div className="flex items-center">
              <div className={`h-2 w-2 rounded-full mr-2 ${
                systemStatus === 'online' ? 'bg-green-300 animate-pulse' : 'bg-yellow-300'
              }`}></div>
              <span>System Status: {systemStatus === 'online' ? 'Online' : 'Warning'}</span>
            </div>
            <div className="flex items-center">
              <span>Last Update: {new Date().toLocaleTimeString()}</span>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <span>Monitoring: 3 brands</span>
            <span>•</span>
            <span>{crisisAlerts > 0 ? `${crisisAlerts} Crisis Alerts` : '24/7 Active'}</span>
          </div>
        </div>
      </div>
    </div>
  )
}