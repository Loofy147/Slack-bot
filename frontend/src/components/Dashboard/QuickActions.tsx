import React from 'react';
import { Link } from 'react-router-dom';
import { 
  PlusIcon, 
  PlayIcon, 
  DocumentTextIcon, 
  CogIcon,
  ChartBarIcon,
  TemplateIcon
} from '@heroicons/react/24/outline';

const actions = [
  {
    name: 'New Project',
    description: 'Create a new project',
    href: '/projects/new',
    icon: PlusIcon,
    color: 'bg-indigo-500 hover:bg-indigo-600',
  },
  {
    name: 'Start Orchestration',
    description: 'Begin AI orchestration',
    href: '/orchestrations/new',
    icon: PlayIcon,
    color: 'bg-green-500 hover:bg-green-600',
  },
  {
    name: 'Browse Templates',
    description: 'Explore templates',
    href: '/templates',
    icon: TemplateIcon,
    color: 'bg-purple-500 hover:bg-purple-600',
  },
  {
    name: 'View Analytics',
    description: 'Check performance',
    href: '/analytics',
    icon: ChartBarIcon,
    color: 'bg-blue-500 hover:bg-blue-600',
  },
  {
    name: 'Documentation',
    description: 'Read the docs',
    href: '/docs',
    icon: DocumentTextIcon,
    color: 'bg-gray-500 hover:bg-gray-600',
  },
  {
    name: 'Settings',
    description: 'Configure platform',
    href: '/settings',
    icon: CogIcon,
    color: 'bg-orange-500 hover:bg-orange-600',
  },
];

export default function QuickActions() {
  return (
    <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white">
          Quick Actions
        </h3>
      </div>
      
      <div className="p-6">
        <div className="grid grid-cols-1 gap-4">
          {actions.map((action) => (
            <Link
              key={action.name}
              to={action.href}
              className="group relative rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
            >
              <div className="flex items-center space-x-3">
                <div className={`flex-shrink-0 w-10 h-10 ${action.color} rounded-lg flex items-center justify-center transition-colors group-hover:scale-110 transform duration-200`}>
                  <action.icon className="w-5 h-5 text-white" aria-hidden="true" />
                </div>
                
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                    {action.name}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {action.description}
                  </p>
                </div>
                
                <div className="flex-shrink-0">
                  <svg
                    className="w-5 h-5 text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300 transition-colors"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5l7 7-7 7"
                    />
                  </svg>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}