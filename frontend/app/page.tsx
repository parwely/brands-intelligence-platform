// frontend/app/page.tsx
'use client';

import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { useEffect, useState } from 'react';
import { apiService, Brand, Mention } from '@/services/api';

export default function Dashboard() {
  const [brands, setBrands] = useState<Brand[]>([]);
  const [mentions, setMentions] = useState<Mention[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedBrand, setSelectedBrand] = useState<string>('');

  useEffect(() => {
    const loadData = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/demo/sample-data');
        const data = await response.json();
        setBrands(data.brands);
        setMentions(data.mentions);
        if (data.brands.length > 0) {
          setSelectedBrand(data.brands[0].id);
        }
      } catch (error) {
        console.error('Failed to load data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  if (loading) {
    return (
      <DashboardLayout>
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-64 mb-4"></div>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Brand Intelligence Dashboard</h1>
          <p className="mt-2 text-sm text-gray-700">
            Monitor your brand's online presence and sentiment in real-time.
          </p>
        </div>

        {/* Brand Selector */}
        <div className="bg-white shadow rounded-lg p-6">
          <label htmlFor="brand-select" className="block text-sm font-medium text-gray-700">
            Select Brand
          </label>
          <select
            id="brand-select"
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            value={selectedBrand}
            onChange={(e) => setSelectedBrand(e.target.value)}
          >
            {brands.map((brand) => (
              <option key={brand.id} value={brand.id}>
                {brand.name}
              </option>
            ))}
          </select>
        </div>

        {/* Metrics Cards */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard
            title="Total Mentions"
            value={mentions.length.toString()}
            change="+12%"
            trend="up"
          />
          <MetricCard
            title="Avg Sentiment"
            value={mentions.length > 0 
              ? (mentions.reduce((sum, m) => sum + m.sentiment_score, 0) / mentions.length).toFixed(2)
              : '0.00'
            }
            change="+5%"
            trend="up"
          />
          <MetricCard
            title="Crisis Alerts"
            value="0"
            change="-50%"
            trend="down"
          />
          <MetricCard
            title="Engagement"
            value="1.2K"
            change="+18%"
            trend="up"
          />
        </div>

        {/* Recent Mentions */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Recent Mentions</h3>
          </div>
          <div className="divide-y divide-gray-200">
            {mentions.slice(0, 5).map((mention) => (
              <div key={mention.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="text-sm text-gray-900">{mention.content}</p>
                    <div className="mt-1 flex items-center space-x-4 text-xs text-gray-500">
                      <span>Platform: {mention.platform}</span>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        mention.sentiment_score > 0.6 ? 'bg-green-100 text-green-800' :
                        mention.sentiment_score > 0.3 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        Sentiment: {(mention.sentiment_score * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}

function MetricCard({ title, value, change, trend }: {
  title: string;
  value: string;
  change: string;
  trend: 'up' | 'down';
}) {
  return (
    <div className="bg-white overflow-hidden shadow rounded-lg">
      <div className="p-5">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <div className="text-2xl font-bold text-gray-900">{value}</div>
          </div>
        </div>
        <div className="mt-1 flex items-baseline justify-between">
          <p className="text-sm font-medium text-gray-500 truncate">{title}</p>
          <div className={`inline-flex items-baseline px-2.5 py-0.5 rounded-full text-sm font-medium ${
            trend === 'up' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            {change}
          </div>
        </div>
      </div>
    </div>
  );
}