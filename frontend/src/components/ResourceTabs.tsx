import { Resource } from '../types';
import ResourceCard from './ResourceCard';

interface ResourceTabsProps {
  youtubeResources: Resource[];
  pdfResources: Resource[];
  websiteResources: Resource[];
  onDeleteResource?: (resourceId: string, blacklist: boolean) => void;
  onTogglePin?: (resourceId: string) => void;
}

export default function ResourceTabs({
  youtubeResources,
  pdfResources,
  websiteResources,
  onDeleteResource,
  onTogglePin,
}: ResourceTabsProps) {
  // Only show YouTube resources now
  const activeResources = youtubeResources;

  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-200 bg-blue-50 px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="text-lg">🎥</span>
          <span className="text-sm font-semibold text-blue-700">YouTube Videoları</span>
          {activeResources.length > 0 && (
            <span className="px-2 py-0.5 text-xs rounded-full bg-blue-200 text-blue-800">
              {activeResources.length}
            </span>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {activeResources.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p className="text-sm">Video bulunamadı.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {activeResources.map((resource) => (
              <ResourceCard
                key={resource.id}
                resource={resource}
                onDelete={onDeleteResource}
                onTogglePin={onTogglePin}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
