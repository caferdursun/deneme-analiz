import { useState } from 'react';
import { Resource } from '../types';
import ResourceDeleteModal from './ResourceDeleteModal';

interface ResourceCardProps {
  resource: Resource;
  compact?: boolean;
  onDelete?: (resourceId: string, blacklist: boolean) => void;
}

export default function ResourceCard({ resource, compact = false, onDelete }: ResourceCardProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);

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
      <>
        <ResourceDeleteModal
          resource={resource}
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onDeleteOnly={() => {
            onDelete?.(resource.id, false);
            setIsModalOpen(false);
          }}
          onDeleteAndBlacklist={() => {
            onDelete?.(resource.id, true);
            setIsModalOpen(false);
          }}
        />

        <div className="flex items-start gap-3 p-3 bg-white border border-gray-200 rounded-lg relative group">
          {/* Delete Button */}
          {onDelete && (
            <button
              onClick={() => setIsModalOpen(true)}
              className="absolute top-2 right-2 p-1.5 bg-red-600 text-white rounded-full opacity-0 group-hover:opacity-100 hover:bg-red-700 transition-opacity"
              title="Kaynağı sil"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
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
      </>
    );
  }

  // PDF or Website
  return (
    <>
      <ResourceDeleteModal
        resource={resource}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onDeleteOnly={() => {
          onDelete?.(resource.id, false);
          setIsModalOpen(false);
        }}
        onDeleteAndBlacklist={() => {
          onDelete?.(resource.id, true);
          setIsModalOpen(false);
        }}
      />

      <div className="flex items-start gap-3 p-3 bg-white border border-gray-200 rounded-lg relative group">
        {/* Delete Button */}
        {onDelete && (
          <button
            onClick={() => setIsModalOpen(true)}
            className="absolute top-2 right-2 p-1.5 bg-red-600 text-white rounded-full opacity-0 group-hover:opacity-100 hover:bg-red-700 transition-opacity z-10"
            title="Kaynağı sil"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
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
    </>
  );
}
