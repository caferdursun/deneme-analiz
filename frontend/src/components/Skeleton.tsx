/**
 * Skeleton loader components for better loading states
 */

interface SkeletonProps {
  className?: string;
}

export const Skeleton = ({ className = '' }: SkeletonProps) => {
  return (
    <div
      className={`animate-pulse bg-gray-200 rounded ${className}`}
      aria-hidden="true"
    />
  );
};

export const SkeletonText = ({ className = '' }: SkeletonProps) => {
  return <Skeleton className={`h-4 ${className}`} />;
};

export const SkeletonTitle = ({ className = '' }: SkeletonProps) => {
  return <Skeleton className={`h-8 ${className}`} />;
};

export const SkeletonCard = ({ className = '' }: SkeletonProps) => {
  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      <SkeletonTitle className="w-2/3 mb-4" />
      <SkeletonText className="w-full mb-2" />
      <SkeletonText className="w-5/6 mb-2" />
      <SkeletonText className="w-4/6" />
    </div>
  );
};

export const SkeletonChart = ({ className = '' }: SkeletonProps) => {
  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      <SkeletonTitle className="w-1/3 mb-4" />
      <Skeleton className="w-full h-64" />
    </div>
  );
};

export const SkeletonTable = ({ rows = 5, className = '' }: SkeletonProps & { rows?: number }) => {
  return (
    <div className={`bg-white rounded-lg shadow-md overflow-hidden ${className}`}>
      <div className="p-4 border-b border-gray-200">
        <SkeletonText className="w-1/4" />
      </div>
      {Array.from({ length: rows }).map((_, index) => (
        <div key={index} className="p-4 border-b border-gray-100 flex gap-4">
          <SkeletonText className="w-1/4" />
          <SkeletonText className="w-1/3" />
          <SkeletonText className="w-1/6" />
          <Skeleton className="w-16 h-8 rounded-full" />
        </div>
      ))}
    </div>
  );
};

export const SkeletonList = ({ items = 3, className = '' }: SkeletonProps & { items?: number }) => {
  return (
    <div className={className}>
      {Array.from({ length: items }).map((_, index) => (
        <div key={index} className="bg-white rounded-lg shadow-md p-6 mb-4">
          <div className="flex items-start gap-4">
            <Skeleton className="w-12 h-12 rounded-full flex-shrink-0" />
            <div className="flex-1">
              <SkeletonText className="w-1/2 mb-2" />
              <SkeletonText className="w-full mb-2" />
              <SkeletonText className="w-3/4" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

// Dashboard specific skeletons
export const DashboardSkeleton = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="mb-6">
          <SkeletonTitle className="w-1/4 mb-2" />
          <SkeletonText className="w-1/3" />
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white rounded-lg shadow-md p-6">
              <SkeletonText className="w-1/2 mb-2" />
              <SkeletonTitle className="w-3/4 mb-2" />
              <Skeleton className="w-full h-2 rounded-full" />
            </div>
          ))}
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <SkeletonChart />
          <SkeletonChart />
        </div>

        {/* Widgets */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <SkeletonCard />
          <SkeletonCard />
        </div>
      </div>
    </div>
  );
};

// Exam List skeleton
export const ExamListSkeleton = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <div className="mb-6">
          <SkeletonTitle className="w-1/4 mb-4" />
          <div className="flex gap-4">
            <Skeleton className="w-32 h-10 rounded-lg" />
            <Skeleton className="w-32 h-10 rounded-lg" />
          </div>
        </div>

        <SkeletonTable rows={8} />
      </div>
    </div>
  );
};

// Recommendations skeleton
export const RecommendationsSkeleton = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <div className="mb-6 flex justify-between items-center">
          <SkeletonTitle className="w-1/4" />
          <Skeleton className="w-32 h-10 rounded-lg" />
        </div>

        <div className="mb-6">
          <Skeleton className="w-full h-12 rounded-lg" />
        </div>

        <SkeletonList items={5} />
      </div>
    </div>
  );
};

// Study Plan skeleton
export const StudyPlanSkeleton = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <SkeletonText className="w-16 mb-4" />

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <SkeletonTitle className="w-1/2 mb-4" />
          <SkeletonText className="w-2/3 mb-4" />
          <Skeleton className="w-full h-3 rounded-full" />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md p-6">
              <SkeletonText className="w-1/4 mb-4" />
              <div className="grid grid-cols-7 gap-2">
                {Array.from({ length: 14 }).map((_, i) => (
                  <Skeleton key={i} className="w-full h-20 rounded-lg" />
                ))}
              </div>
            </div>
          </div>

          <div className="lg:col-span-1">
            <SkeletonCard />
          </div>
        </div>
      </div>
    </div>
  );
};
