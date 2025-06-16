// frontend/app/page.tsx
'use client';

import { DashboardLayout } from '../src/components/layout/DashboardLayout';
import { useEffect, useState } from 'react';
import { apiService, Brand, Mention, AnalyticsOverview, CrisisAlert } from '../src/services/api';
import { TrendingUp, TrendingDown, AlertTriangle, Users, MessageSquare, BarChart3, Zap } from 'lucide-react';

export default function Dashboard() {
  const [brands, setBrands] = useState<Brand[]>([]);
  const [mentions, setMentions] = useState<Mention[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsOverview | null>(null);
  const [crisisAlerts, setCrisisAlerts] = useState<CrisisAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedBrand, setSelectedBrand] = useState<string>('');
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setRefreshing(true);
      const [sampleData, analyticsData, crisisData] = await Promise.all([
        apiService.getSampleData(),
        apiService.getAnalyticsOverview(),
        apiService.getCrisisAlerts(0.5)
      ]);

      setBrands(sampleData.brands);
      setMentions(sampleData.mentions);
      setAnalytics(analyticsData);
      setCrisisAlerts(crisisData.crisis_alerts);

      if (sampleData.brands.length > 0) {
        setSelectedBrand(sampleData.brands[0].id);
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const refreshData = () => {
    loadDashboardData();
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-64"></div>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="h-96 bg-gray-200 rounded"></div>
            <div className="h-96 bg-gray-200 rounded"></div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Header Section */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-gray-900">Brand Intelligence Dashboard</h1>
            <p className="mt-2 text-lg text-gray-600">
              Real-time brand monitoring with AI-powered crisis detection
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={refreshData}
              disabled={refreshing}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {refreshing ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              ) : null}
              {refreshing ? 'Refreshing...' : 'Refresh Data'}
            </button>
          </div>
        </div>

        {/* Brand Selector */}
        <div className="bg-white shadow-sm rounded-lg p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <label htmlFor="brand-select" className="block text-sm font-medium text-gray-700 mb-2">
                Active Brand Monitoring
              </label>
              <select
                id="brand-select"
                className="block w-full max-w-xs pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                value={selectedBrand}
                onChange={(e) => setSelectedBrand(e.target.value)}
              >
                <option value="">All Brands</option>
                {brands.map((brand) => (
                  <option key={brand.id} value={brand.id}>
                    {brand.name} ({brand.industry})
                  </option>
                ))}
              </select>
            </div>
            <div className="text-sm text-gray-500">
              <div className="flex items-center">
                <div className="h-2 w-2 bg-green-400 rounded-full animate-pulse mr-2"></div>
                Live monitoring active
              </div>
            </div>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard
            title="Total Mentions"
            value={analytics?.total_mentions.toString() || '0'}
            change="+12%"
            trend="up"
            icon={<MessageSquare className="h-6 w-6" />}
            description="Last 24 hours"
          />
          <MetricCard
            title="Avg Sentiment"
            value={analytics?.average_sentiment.toFixed(2) || '0.50'}
            change={analytics && analytics.average_sentiment > 0.5 ? "+5%" : "-3%"}
            trend={analytics && analytics.average_sentiment > 0.5 ? "up" : "down"}
            icon={<BarChart3 className="h-6 w-6" />}
            description="0.00 - 1.00 scale"
          />
          <MetricCard
            title="Crisis Alerts"
            value={analytics?.high_crisis_alerts.toString() || '0'}
            change={analytics && analytics.high_crisis_alerts > 0 ? "+100%" : "-50%"}
            trend={analytics && analytics.high_crisis_alerts > 0 ? "up" : "down"}
            icon={<AlertTriangle className="h-6 w-6" />}
            description="High risk mentions"
            urgent={analytics ? analytics.high_crisis_alerts > 0 : false}
          />
          <MetricCard
            title="Engagement"
            value="2.4K"
            change="+18%"
            trend="up"
            icon={<Zap className="h-6 w-6" />}
            description="Total interactions"
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Recent Mentions - Takes 2/3 of the space */}
          <div className="lg:col-span-2">
            <div className="bg-white shadow-sm rounded-lg border border-gray-200">
              <div className="px-6 py-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-medium text-gray-900">Recent Mentions</h3>
                  <span className="text-sm text-gray-500">Real-time updates</span>
                </div>
              </div>
              <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
                {mentions.slice(0, 8).map((mention) => (
                  <MentionCard key={mention.id} mention={mention} />
                ))}
              </div>
            </div>
          </div>

          {/* Sidebar - Takes 1/3 of the space */}
          <div className="space-y-6">
            {/* Crisis Alerts */}
            {crisisAlerts.length > 0 && (
              <div className="bg-red-50 border border-red-200 rounded-lg">
                <div className="px-4 py-3 border-b border-red-200">
                  <div className="flex items-center">
                    <AlertTriangle className="h-5 w-5 text-red-500 mr-2" />
                    <h3 className="text-sm font-semibold text-red-800">Crisis Alerts</h3>
                  </div>
                </div>
                <div className="p-4 space-y-3 max-h-64 overflow-y-auto">
                  {crisisAlerts.slice(0, 3).map((alert) => (
                    <div key={alert.id} className="bg-white p-3 rounded border border-red-200">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <p className="text-xs text-red-600 font-medium">{alert.platform}</p>
                          <p className="text-sm text-gray-900 mt-1 line-clamp-2">{alert.content}</p>
                          <div className="flex items-center mt-2 space-x-2">
                            <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                              alert.urgency_level === 'HIGH' ? 'bg-red-100 text-red-800' : 'bg-orange-100 text-orange-800'
                            }`}>
                              {alert.urgency_level} RISK
                            </span>
                            <span className="text-xs text-gray-500">
                              {Math.round(alert.crisis_probability * 100)}% crisis probability
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Sentiment Distribution */}
            <div className="bg-white shadow-sm rounded-lg border border-gray-200">
              <div className="px-4 py-3 border-b border-gray-200">
                <h3 className="text-sm font-semibold text-gray-900">Sentiment Distribution</h3>
              </div>
              <div className="p-4">
                {analytics && (
                  <div className="space-y-3">
                    <SentimentBar 
                      label="Positive" 
                      percentage={analytics.sentiment_distribution.positive_percentage}
                      color="bg-green-500"
                      count={analytics.sentiment_breakdown.positive}
                    />
                    <SentimentBar 
                      label="Neutral" 
                      percentage={analytics.sentiment_distribution.neutral_percentage}
                      color="bg-gray-400"
                      count={analytics.sentiment_breakdown.neutral}
                    />
                    <SentimentBar 
                      label="Negative" 
                      percentage={analytics.sentiment_distribution.negative_percentage}
                      color="bg-red-500"
                      count={analytics.sentiment_breakdown.negative}
                    />
                  </div>
                )}
              </div>
            </div>

            {/* Monitored Brands */}
            <div className="bg-white shadow-sm rounded-lg border border-gray-200">
              <div className="px-4 py-3 border-b border-gray-200">
                <h3 className="text-sm font-semibold text-gray-900">Monitored Brands</h3>
              </div>
              <div className="p-4 space-y-3">
                {brands.map((brand) => (
                  <div key={brand.id} className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{brand.name}</p>
                      <p className="text-xs text-gray-500">{brand.industry}</p>
                    </div>
                    <div className="flex items-center">
                      <div className="h-2 w-2 bg-green-400 rounded-full mr-2"></div>
                      <span className="text-xs text-gray-500">Active</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}

// Enhanced Metric Card Component
function MetricCard({ 
  title, 
  value, 
  change, 
  trend, 
  icon, 
  description, 
  urgent = false 
}: {
  title: string;
  value: string;
  change: string;
  trend: 'up' | 'down';
  icon?: React.ReactNode;
  description?: string;
  urgent?: boolean;
}) {
  return (
    <div className={`bg-white overflow-hidden shadow-sm rounded-lg border ${
      urgent ? 'border-red-200 ring-2 ring-red-100' : 'border-gray-200'
    }`}>
      <div className="p-5">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            {icon && (
              <div className={`p-2 rounded-md ${
                urgent ? 'bg-red-100 text-red-600' : 'bg-indigo-100 text-indigo-600'
              }`}>
                {icon}
              </div>
            )}
          </div>
          <div className="ml-4 flex-1">
            <div className="flex items-baseline">
              <div className="text-2xl font-bold text-gray-900">{value}</div>
              <div className={`ml-2 inline-flex items-baseline px-2.5 py-0.5 rounded-full text-sm font-medium ${
                trend === 'up' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {trend === 'up' ? (
                  <TrendingUp className="h-3 w-3 mr-1" />
                ) : (
                  <TrendingDown className="h-3 w-3 mr-1" />
                )}
                {change}
              </div>
            </div>
            <p className="text-sm font-medium text-gray-500 truncate">{title}</p>
            {description && (
              <p className="text-xs text-gray-400 mt-1">{description}</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// Mention Card Component
function MentionCard({ mention }: { mention: Mention }) {
  const getSentimentColor = (score: number) => {
    if (score > 0.6) return 'bg-green-100 text-green-800';
    if (score > 0.3) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    return `${Math.floor(diffInHours / 24)}d ago`;
  };

  return (
    <div className="px-6 py-4 hover:bg-gray-50 transition-colors">
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <p className="text-sm text-gray-900 line-clamp-2 mb-2">{mention.content}</p>
          <div className="flex items-center space-x-4 text-xs text-gray-500">
            <span className="font-medium">{mention.platform}</span>
            <span>{formatTimeAgo(mention.published_at)}</span>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
              getSentimentColor(mention.sentiment_score)
            }`}>
              {mention.sentiment_label} ({Math.round(mention.sentiment_score * 100)}%)
            </span>
            {mention.crisis_probability > 0.5 && (
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                ⚠️ Crisis Risk
              </span>
            )}
          </div>
          <div className="flex items-center space-x-4 mt-2 text-xs text-gray-400">
            <span>❤️ {mention.likes_count}</span>
            <span>🔄 {mention.shares_count}</span>
            <span>💬 {mention.comments_count}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// Sentiment Bar Component
function SentimentBar({ 
  label, 
  percentage, 
  color, 
  count 
}: { 
  label: string; 
  percentage: number; 
  color: string; 
  count: number; 
}) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center flex-1">
        <span className="text-sm font-medium text-gray-700 w-16">{label}</span>
        <div className="flex-1 mx-3">
          <div className="bg-gray-200 rounded-full h-2">
            <div 
              className={`${color} h-2 rounded-full transition-all duration-300`}
              style={{ width: `${percentage}%` }}
            ></div>
          </div>
        </div>
        <span className="text-sm text-gray-600 w-12 text-right">{percentage.toFixed(1)}%</span>
      </div>
      <span className="text-xs text-gray-500 ml-2">({count})</span>
    </div>
  );
}