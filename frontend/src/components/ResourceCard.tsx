import { Resource } from '../types';

interface ResourceCardProps {
  resource: Resource;
  compact?: boolean;
  onTogglePin?: (resourceId: string) => void;
  onPin?: (resource: Resource) => void; // For unpinned search results
}

export default function ResourceCard({ resource, compact = false, onTogglePin, onPin }: ResourceCardProps) {

  // If resource has no ID, it's from search results (not saved to DB yet)
  const isSearchResult = !resource.id;
  const isPinned = resource.is_pinned;

  const handlePinClick = () => {
    if (isSearchResult && onPin) {
      // Save to DB and pin
      onPin(resource);
    } else if (onTogglePin && resource.id) {
      // Toggle existing resource
      onTogglePin(resource.id);
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'youtube':
        return '🎥';
      case 'pdf':
        return '📄';
      case 'website':
        return '🌐';
      default:
        return '📚';
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'youtube':
        return 'YouTube';
      case 'pdf':
        return 'PDF';
      case 'website':
        return 'Web Sitesi';
      default:
        return 'Kaynak';
    }
  };

  const formatViewCount = (count?: number) => {
    if (!count) return '';
    if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`;
    if (count >= 1000) return `${(count / 1000).toFixed(1)}K`;
    return count.toString();
  };

  if (resource.type === 'youtube') {
    return (
        <div className={`flex items-start gap-3 p-3 border rounded-lg relative group ${
          resource.is_pinned
            ? 'bg-amber-50 border-amber-300'
            : 'bg-white border-gray-200'
        }`}>
          {/* Pin Button */}
          {(onTogglePin || onPin) && (
            <button
              onClick={handlePinClick}
              className={`absolute top-2 right-2 p-1.5 rounded-full transition-all ${
                isPinned
                  ? 'bg-amber-500 text-white opacity-100'
                  : isSearchResult
                  ? 'bg-blue-500 text-white opacity-100'
                  : 'bg-gray-200 text-gray-600 opacity-0 group-hover:opacity-100 hover:bg-gray-300'
              }`}
              title={isPinned ? 'Sabitlemeyi kaldır' : isSearchResult ? 'Kaydet ve sabitle' : 'Sabitle'}
            >
              {isSearchResult ? '💾' : '📌'}
            </button>
          )}

        <a
          href={resource.url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-start gap-3 flex-1"
        >
        {/* Thumbnail */}
        {resource.thumbnail_url && (
          <div className="flex-shrink-0">
            <img
              src={resource.thumbnail_url}
              alt={resource.name}
              className="w-32 h-20 object-cover rounded"
            />
          </div>
        )}

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start gap-2 mb-1">
            <span className="text-lg">{getTypeIcon(resource.type)}</span>
            <h4 className="text-sm font-semibold text-gray-900 line-clamp-2 flex-1">
              {resource.name}
            </h4>
          </div>

          {/* Channel & Stats */}
          {resource.extra_data && (
            <div className="flex items-center gap-3 text-xs text-gray-600 mb-1">
              {resource.extra_data.channel_name && (
                <span className="font-medium">{resource.extra_data.channel_name}</span>
              )}
              {resource.extra_data.view_count && (
                <span>👁️ {formatViewCount(resource.extra_data.view_count)}</span>
              )}
            </div>
          )}

          {/* Description */}
          {!compact && resource.description && (
            <p className="text-xs text-gray-600 line-clamp-2 mt-1">
              {resource.description}
            </p>
          )}

          {/* Type Badge */}
          <span className="inline-block px-2 py-0.5 text-xs font-medium bg-red-100 text-red-700 rounded mt-2">
            {getTypeLabel(resource.type)}
          </span>
        </div>
        </a>
        </div>
    );
  }

  // PDF or Website (not used currently)
  return (
      <div className={`flex items-start gap-3 p-3 border rounded-lg relative group ${
        resource.is_pinned
          ? 'bg-amber-50 border-amber-300'
          : 'bg-white border-gray-200'
      }`}>
        {/* Pin Button */}
        {(onTogglePin || onPin) && (
          <button
            onClick={handlePinClick}
            className={`absolute top-2 right-2 p-1.5 rounded-full transition-all z-10 ${
              isPinned
                ? 'bg-amber-500 text-white opacity-100'
                : isSearchResult
                ? 'bg-blue-500 text-white opacity-100'
                : 'bg-gray-200 text-gray-600 opacity-0 group-hover:opacity-100 hover:bg-gray-300'
            }`}
            title={isPinned ? 'Sabitlemeyi kaldır' : isSearchResult ? 'Kaydet ve sabitle' : 'Sabitle'}
          >
            {isSearchResult ? '💾' : '📌'}
          </button>
        )}

      <a
        href={resource.url}
        target="_blank"
        rel="noopener noreferrer"
        className="flex items-start gap-3 flex-1"
      >
      {/* Icon */}
      <div className="flex-shrink-0">
        <div className="w-12 h-12 flex items-center justify-center bg-gray-100 rounded text-2xl">
          {getTypeIcon(resource.type)}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <h4 className="text-sm font-semibold text-gray-900 mb-1">
          {resource.name}
        </h4>

        {!compact && resource.description && (
          <p className="text-xs text-gray-600 line-clamp-2 mb-2">
            {resource.description}
          </p>
        )}

        <span className={`inline-block px-2 py-0.5 text-xs font-medium rounded ${
          resource.type === 'pdf' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'
        }`}>
          {getTypeLabel(resource.type)}
        </span>
      </div>
      </a>
      </div>
  );
}
