import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  ChartBarIcon, 
  CogIcon, 
  PlayIcon, 
  DocumentTextIcon,
  TrendingUpIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import StatsCard from '../components/Dashboard/StatsCard';
import RecentActivity from '../components/Dashboard/RecentActivity';
import QuickActions from '../components/Dashboard/QuickActions';
import UsageChart from '../components/Dashboard/UsageChart';
import { apiClient } from '../services/api';

export default function Dashboard() {
  const { data: analytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ['analytics', 'usage'],
    queryFn: () => apiClient.getUsageAnalytics(30),
  });

  const { data: projects, isLoading: projectsLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: () => apiClient.listProjects({ limit: 5 }),
  });

  const { data: orchestrations, isLoading: orchestrationsLoading } = useQuery({
    queryKey: ['orchestrations'],
    queryFn: () => apiClient.listOrchestrations({ limit: 5 }),
  });

  const stats = [
    {
      name: 'Total Projects',
      value: projects?.length || 0,
      change: '+12%',
      changeType: 'increase' as const,
      icon: DocumentTextIcon,
    },
    {
      name: 'Active Orchestrations',
      value: orchestrations?.filter(o => o.status === 'running').length || 0,
      change: '+5%',
      changeType: 'increase' as const,
      icon: PlayIcon,
    },
    {
      name: 'Success Rate',
      value: `${analytics?.runs_summary?.completed_runs || 0}%`,
      change: '+2.1%',
      changeType: 'increase' as const,
      icon: TrendingUpIcon,
    },
    {
      name: 'Avg. Execution Time',
      value: `${Math.round((analytics?.runs_summary?.avg_execution_time || 0) / 1000)}s`,
      change: '-0.5s',
      changeType: 'decrease' as const,
      icon: ClockIcon,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Dashboard
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Welcome back! Here's what's happening with your AI orchestrations.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <StatsCard
            key={stat.name}
            name={stat.name}
            value={stat.value}
            change={stat.change}
            changeType={stat.changeType}
            icon={stat.icon}
            loading={analyticsLoading || projectsLoading || orchestrationsLoading}
          />
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Usage Chart */}
        <div className="lg:col-span-2">
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                API Usage Over Time
              </h3>
              <ChartBarIcon className="h-5 w-5 text-gray-400" />
            </div>
            <UsageChart data={analytics?.api_usage || []} loading={analyticsLoading} />
          </div>
        </div>

        {/* Quick Actions */}
        <div>
          <QuickActions />
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentActivity
          title="Recent Projects"
          items={projects || []}
          loading={projectsLoading}
          type="projects"
        />
        <RecentActivity
          title="Recent Orchestrations"
          items={orchestrations || []}
          loading={orchestrationsLoading}
          type="orchestrations"
        />
      </div>
    </div>
  );
}