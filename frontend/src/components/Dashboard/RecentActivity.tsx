import React from 'react';
import { Link } from 'react-router-dom';
import { 
  DocumentTextIcon, 
  PlayIcon, 
  CheckCircleIcon, 
  XCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../UI/LoadingSpinner';

interface ActivityItem {
  id: string;
  name: string;
  status?: string;
  created_at: string;
  updated_at?: string;
}

interface RecentActivityProps {
  title: string;
  items: ActivityItem[];
  loading: boolean;
  type: 'projects' | 'orchestrations';
}

export default function RecentActivity({ title, items, loading, type }: RecentActivityProps) {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      case 'running':
        return <ClockIcon className="h-5 w-5 text-blue-500 animate-spin" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/20';
      case 'failed':
        return 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/20';
      case 'running':
        return 'text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/20';
      case 'active':
        return 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/20';
      default:
        return 'text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-700';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) {
      return 'Just now';
    } else if (diffInHours < 24) {
      return `${diffInHours}h ago`;
    } else {
      const diffInDays = Math.floor(diffInHours / 24);
      return `${diffInDays}d ago`;
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
            {title}
          </h3>
          <Link
            to={`/${type}`}
            className="text-sm font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400 dark:hover:text-indigo-300"
          >
            View all
          </Link>
        </div>
      </div>

      <div className="divide-y divide-gray-200 dark:divide-gray-700">
        {loading ? (
          <div className="p-6 flex justify-center">
            <LoadingSpinner size="sm" />
          </div>
        ) : items.length === 0 ? (
          <div className="p-6 text-center">
            <div className="flex flex-col items-center">
              {type === 'projects' ? (
                <DocumentTextIcon className="h-12 w-12 text-gray-400 mb-2" />
              ) : (
                <PlayIcon className="h-12 w-12 text-gray-400 mb-2" />
              )}
              <p className="text-gray-500 dark:text-gray-400">
                No {type} yet
              </p>
            </div>
          </div>
        ) : (
          items.slice(0, 5).map((item) => (
            <div key={item.id} className="p-6 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
              <div className="flex items-center space-x-4">
                <div className="flex-shrink-0">
                  {type === 'projects' ? (
                    <DocumentTextIcon className="h-6 w-6 text-gray-400" />
                  ) : (
                    getStatusIcon(item.status || 'pending')
                  )}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                      {item.name}
                    </p>
                    {item.status && (
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(item.status)}`}>
                        {item.status}
                      </span>
                    )}
                  </div>
                  
                  <div className="flex items-center mt-1 text-sm text-gray-500 dark:text-gray-400">
                    <span>
                      {type === 'projects' ? 'Created' : 'Started'} {formatDate(item.created_at)}
                    </span>
                    {item.updated_at && item.updated_at !== item.created_at && (
                      <span className="ml-2">
                        • Updated {formatDate(item.updated_at)}
                      </span>
                    )}
                  </div>
                </div>
                
                <div className="flex-shrink-0">
                  <Link
                    to={`/${type}/${item.id}`}
                    className="text-indigo-600 hover:text-indigo-500 dark:text-indigo-400 dark:hover:text-indigo-300 text-sm font-medium"
                  >
                    View
                  </Link>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}