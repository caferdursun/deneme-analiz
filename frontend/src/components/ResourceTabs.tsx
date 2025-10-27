import { useState } from 'react';
import { Resource } from '../types';
import ResourceCard from './ResourceCard';

interface ResourceTabsProps {
  youtubeResources: Resource[];
  pdfResources: Resource[];
  websiteResources: Resource[];
  onDeleteResource?: (resourceId: string, blacklist: boolean) => void;
}

type TabType = 'youtube' | 'pdf' | 'website';

export default function ResourceTabs({
  youtubeResources,
  pdfResources,
  websiteResources,
  onDeleteResource,
}: ResourceTabsProps) {
  const [activeTab, setActiveTab] = useState<TabType>('youtube');

  const tabs = [
    { id: 'youtube' as TabType, label: '🎥 YouTube', count: youtubeResources.length },
    { id: 'pdf' as TabType, label: '📄 PDF', count: pdfResources.length },
    { id: 'website' as TabType, label: '🌐 Web Sitesi', count: websiteResources.length },
  ];

  const getActiveResources = (): Resource[] => {
    switch (activeTab) {
      case 'youtube':
        return youtubeResources;
      case 'pdf':
        return pdfResources;
      case 'website':
        return websiteResources;
      default:
        return [];
    }
  };

  const activeResources = getActiveResources();

  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
      {/* Tab Headers */}
      <div className="flex border-b border-gray-200">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? 'bg-blue-50 text-blue-700 border-b-2 border-blue-600'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            }`}
          >
            {tab.label}
            {tab.count > 0 && (
              <span
                className={`ml-2 px-2 py-0.5 text-xs rounded-full ${
                  activeTab === tab.id
                    ? 'bg-blue-200 text-blue-800'
                    : 'bg-gray-200 text-gray-700'
                }`}
              >
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="p-4">
        {activeResources.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p className="text-sm">Bu kategoride kaynak bulunamadı.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {activeResources.map((resource) => (
              <ResourceCard key={resource.id} resource={resource} onDelete={onDeleteResource} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
