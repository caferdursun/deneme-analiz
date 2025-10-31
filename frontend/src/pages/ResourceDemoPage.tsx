import React from 'react';
import ResourceRecommendations from '../components/ResourceRecommendations';

/**
 * Demo page for testing the new Resource Recommendations feature
 *
 * This page demonstrates the channel-based video curation algorithm:
 * - Uses real YouTube channels from our database
 * - AI-powered keyword generation with Claude
 * - Multi-factor quality scoring
 * - Enhanced filtering (duration, views, engagement, age)
 */
const ResourceDemoPage: React.FC = () => {
  // Demo study item IDs - these would normally come from the study plan
  // For now, we'll use a placeholder since we need a real study_plan_item from DB
  const demoStudyItemId = "demo-item-id";

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          📚 Kaynak Önerileri - Demo
        </h1>
        <p className="text-gray-600">
          Yeni kanal bazlı video önerme algoritmasını test edin
        </p>
      </div>

      {/* Algorithm Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
        <h2 className="text-lg font-semibold text-blue-900 mb-3">
          🤖 Yeni Algoritma Özellikleri
        </h2>
        <div className="grid md:grid-cols-2 gap-4 text-sm text-blue-800">
          <div>
            <h3 className="font-medium mb-2">✅ Kanal Bazlı Arama</h3>
            <ul className="list-disc list-inside space-y-1 text-blue-700">
              <li>24 güvenilir Türk eğitim kanalı</li>
              <li>Trust score sistemi (70-100)</li>
              <li>Otomatik kanal keşfi</li>
            </ul>
          </div>

          <div>
            <h3 className="font-medium mb-2">🎯 AI Keyword Üretimi</h3>
            <ul className="list-disc list-inside space-y-1 text-blue-700">
              <li>Claude ile akıllı keyword'ler</li>
              <li>Konu bazlı çeşitli arama terimleri</li>
              <li>TYT/AYT odaklı</li>
            </ul>
          </div>

          <div>
            <h3 className="font-medium mb-2">🔍 Gelişmiş Filtreler</h3>
            <ul className="list-disc list-inside space-y-1 text-blue-700">
              <li>Süre: 5-30 dakika</li>
              <li>İzlenme: &gt;5K</li>
              <li>Yaş: 2 hafta - 3 yıl</li>
              <li>Beğeni oranı: &gt;0.3%</li>
              <li>Yorum sayısı: &gt;5</li>
            </ul>
          </div>

          <div>
            <h3 className="font-medium mb-2">⭐ Kalite Skorlama</h3>
            <ul className="list-disc list-inside space-y-1 text-blue-700">
              <li>Başlık/açıklama uyumu</li>
              <li>Engagement metrikleri</li>
              <li>Kanal güvenilirliği</li>
              <li>Görüntülenme dengesi</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Demo Notice */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <p className="text-sm text-yellow-700">
              <strong>Not:</strong> Bu demo sayfayı kullanmak için gerçek bir Study Plan Item ID'si gereklidir.
              Veritabanında oluşturulmuş bir çalışma planı öğesi kullanın veya test scriptlerini çalıştırın.
            </p>
          </div>
        </div>
      </div>

      {/* Resource Recommendations Component */}
      <div className="grid grid-cols-1 gap-8">
        {/* Example 1: Fizik */}
        <ResourceRecommendations
          studyItemId={demoStudyItemId}
          subject="Fizik"
          topic="Optik ve Işık"
        />

        {/* Example 2: Matematik */}
        <div className="opacity-50 pointer-events-none">
          <ResourceRecommendations
            studyItemId={demoStudyItemId}
            subject="Matematik"
            topic="Türev"
          />
        </div>

        {/* Example 3: Kimya */}
        <div className="opacity-50 pointer-events-none">
          <ResourceRecommendations
            studyItemId={demoStudyItemId}
            subject="Kimya"
            topic="Asitler ve Bazlar"
          />
        </div>
      </div>

      {/* Technical Details */}
      <div className="mt-12 bg-gray-50 border border-gray-200 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">
          🛠️ Teknik Detaylar
        </h2>
        <div className="text-sm text-gray-700 space-y-2">
          <p><strong>API Endpoint:</strong> POST /api/resources/study-plan-items/:id/curate</p>
          <p><strong>Backend Services:</strong></p>
          <ul className="list-disc list-inside ml-4 space-y-1">
            <li>YouTubeService - Video arama ve filtreleme</li>
            <li>ClaudeCuratorService - AI keyword generation</li>
            <li>ChannelService - Kanal yönetimi</li>
            <li>ResourceService - Kaynak küratörlüğü</li>
          </ul>
          <p><strong>Database:</strong> 24 kanal (Matematik, Fizik, Kimya, Biyoloji, Türkçe)</p>
          <p><strong>YouTube API Quota:</strong> ~200-300 units per request</p>
        </div>
      </div>
    </div>
  );
};

export default ResourceDemoPage;
