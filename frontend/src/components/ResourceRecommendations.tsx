import React, { useState } from 'react';
import axios from 'axios';

interface Resource {
  id: string;
  name: string;
  type: string;
  url: string;
  description: string;
  subject_name: string;
  topic: string;
  thumbnail_url?: string;
  quality_score: number;
  extra_data?: {
    channel_name?: string;
    channel_name_db?: string;
    view_count?: number;
    like_count?: number;
    comment_count?: number;
    like_ratio?: number;
    duration_seconds?: number;
    channel_trust_score?: number;
  };
}

interface ResourcesByType {
  youtube: Resource[];
  pdf: Resource[];
  website: Resource[];
}

interface ResourceRecommendationsProps {
  studyItemId: string;
  subject: string;
  topic: string;
}

const ResourceRecommendations: React.FC<ResourceRecommendationsProps> = ({
  studyItemId,
  subject,
  topic,
}) => {
  const [resources, setResources] = useState<ResourcesByType | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const curateResources = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post<ResourcesByType>(
        `http://localhost:8000/api/resources/study-plan-items/${studyItemId}/curate`
      );
      setResources(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Kaynaklar yüklenirken bir hata oluştu');
      console.error('Error curating resources:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatViews = (views: number) => {
    if (views >= 1000000) return `${(views / 1000000).toFixed(1)}M`;
    if (views >= 1000) return `${(views / 1000).toFixed(1)}K`;
    return views.toString();
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    return `${mins} dk`;
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            📺 Video Önerileri
          </h3>
          <p className="text-sm text-gray-600">
            {subject} - {topic}
          </p>
        </div>
        <button
          onClick={curateResources}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? (
            <span className="flex items-center">
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Aranıyor...
            </span>
          ) : (
            'Kaynak Öner'
          )}
        </button>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {resources && (
        <div className="space-y-6">
          {/* YouTube Videos */}
          {resources.youtube && resources.youtube.length > 0 && (
            <div>
              <h4 className="text-md font-medium text-gray-700 mb-3 flex items-center">
                <svg className="w-5 h-5 mr-2 text-red-600" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                </svg>
                YouTube Videoları ({resources.youtube.length})
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {resources.youtube.map((resource) => (
                  <div
                    key={resource.id}
                    className="border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition-shadow"
                  >
                    {/* Thumbnail */}
                    {resource.thumbnail_url && (
                      <div className="relative w-full aspect-video bg-gray-900">
                        <img
                          src={resource.thumbnail_url}
                          alt={resource.name}
                          className="w-full h-full object-cover"
                        />
                        <div className="absolute bottom-2 right-2 bg-black bg-opacity-80 text-white text-xs px-2 py-1 rounded">
                          {resource.extra_data?.duration_seconds && formatDuration(resource.extra_data.duration_seconds)}
                        </div>
                      </div>
                    )}

                    {/* Content */}
                    <div className="p-4">
                      <h5 className="font-medium text-sm text-gray-900 mb-2 line-clamp-2">
                        {resource.name}
                      </h5>

                      <p className="text-xs text-gray-600 mb-3">
                        {resource.extra_data?.channel_name_db || resource.extra_data?.channel_name || 'Kanal bilinmiyor'}
                      </p>

                      {/* Stats */}
                      <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
                        <div className="flex items-center space-x-3">
                          <span title="Görüntülenme">
                            👁️ {resource.extra_data?.view_count && formatViews(resource.extra_data.view_count)}
                          </span>
                          <span title="Beğeni Oranı">
                            👍 {resource.extra_data?.like_ratio?.toFixed(1)}%
                          </span>
                          <span title="Yorumlar">
                            💬 {resource.extra_data?.comment_count}
                          </span>
                        </div>
                      </div>

                      {/* Quality Score */}
                      <div className="mb-3">
                        <div className="flex justify-between items-center text-xs mb-1">
                          <span className="text-gray-600">Kalite Skoru</span>
                          <span className="font-semibold">{resource.quality_score.toFixed(0)}/100</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${
                              resource.quality_score >= 80
                                ? 'bg-green-500'
                                : resource.quality_score >= 60
                                ? 'bg-yellow-500'
                                : 'bg-blue-500'
                            }`}
                            style={{ width: `${resource.quality_score}%` }}
                          ></div>
                        </div>
                      </div>

                      {/* Actions */}
                      <a
                        href={resource.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block w-full text-center px-4 py-2 bg-red-600 text-white text-sm rounded-md hover:bg-red-700 transition-colors"
                      >
                        YouTube'da İzle
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* No Results */}
          {resources.youtube.length === 0 && (
            <div className="text-center py-8">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-yellow-100 rounded-full mb-4">
                <svg className="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <p className="text-gray-700 font-medium mb-2">Bu konu için video bulunamadı</p>
              <p className="text-sm text-gray-500 mb-4">
                YouTube API kotası dolmuş olabilir veya bu konuya özel video henüz eklenmemiş olabilir.
              </p>
              <div className="text-xs text-gray-400">
                <p>Çözüm önerileri:</p>
                <ul className="mt-2 space-y-1">
                  <li>• Birkaç saat sonra tekrar deneyin</li>
                  <li>• Daha genel bir konu başlığı kullanın</li>
                  <li>• YouTube'da manuel arama yapabilirsiniz</li>
                </ul>
              </div>
            </div>
          )}
        </div>
      )}

      {!resources && !loading && (
        <div className="text-center py-8 text-gray-400">
          <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p>Kaynak önerileri için "Kaynak Öner" butonuna tıklayın</p>
          <p className="text-sm mt-2">AI destekli algoritma ile en kaliteli videoları bulacağız</p>
        </div>
      )}
    </div>
  );
};

export default ResourceRecommendations;
