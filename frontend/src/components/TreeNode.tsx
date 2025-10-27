import { useState } from 'react';

export interface TreeNodeData {
  id?: number;
  name: string;
  type: 'subject' | 'category' | 'subcategory' | 'outcome';
  children?: TreeNodeData[];
  stats: {
    total_outcomes?: number;
    total_appearances?: number;
    total_questions: number;
    total_acquired: number;
    average_success_rate: number;
    recommendation_count: number;
  };
}

interface TreeNodeProps {
  node: TreeNodeData;
  level: number;
  onOutcomeClick?: (outcomeId: number) => void;
}

export const TreeNode: React.FC<TreeNodeProps> = ({ node, level, onOutcomeClick }) => {
  const [isExpanded, setIsExpanded] = useState(level === 0); // Subjects expanded by default

  const hasChildren = node.children && node.children.length > 0;
  const successRate = node.stats.average_success_rate;

  // Color coding by success rate
  const getColorClass = (rate: number): string => {
    if (rate >= 75) return 'bg-green-50 border-green-300 text-green-800';
    if (rate >= 50) return 'bg-yellow-50 border-yellow-300 text-yellow-800';
    return 'bg-red-50 border-red-300 text-red-800';
  };

  const getSuccessRateColor = (rate: number): string => {
    if (rate >= 75) return 'text-green-700';
    if (rate >= 50) return 'text-yellow-700';
    return 'text-red-700';
  };

  const getIconForType = (type: string): string => {
    switch (type) {
      case 'subject': return '📚';
      case 'category': return '📂';
      case 'subcategory': return '📄';
      case 'outcome': return '🎯';
      default: return '•';
    }
  };

  const handleClick = () => {
    if (hasChildren) {
      setIsExpanded(!isExpanded);
    } else if (node.type === 'outcome' && node.id && onOutcomeClick) {
      onOutcomeClick(node.id);
    }
  };

  const indentClass = `ml-${level * 4}`;

  return (
    <div className="tree-node">
      <div
        className={`
          flex items-center justify-between p-3 mb-2 rounded-lg border-2 transition-all
          ${getColorClass(successRate)}
          ${hasChildren || node.type === 'outcome' ? 'cursor-pointer hover:shadow-md' : ''}
          ${level === 0 ? 'ml-0' : level === 1 ? 'ml-4' : level === 2 ? 'ml-8' : 'ml-12'}
        `}
        onClick={handleClick}
      >
        <div className="flex items-center gap-3 flex-1 min-w-0">
          {/* Expand/collapse icon */}
          {hasChildren && (
            <span className="text-gray-600 text-sm flex-shrink-0">
              {isExpanded ? '▼' : '▶'}
            </span>
          )}

          {/* Type icon */}
          <span className="text-lg flex-shrink-0">{getIconForType(node.type)}</span>

          {/* Node name */}
          <div className="flex-1 min-w-0">
            <div className={`font-semibold truncate ${
              node.type === 'subject' ? 'text-base sm:text-lg' :
              node.type === 'category' ? 'text-sm sm:text-base' :
              'text-xs sm:text-sm'
            }`}>
              {node.name}
            </div>
            <div className="text-xs text-gray-600 mt-0.5">
              {node.stats.total_questions} soru
              {node.stats.total_outcomes && ` • ${node.stats.total_outcomes} kazanım`}
              {node.stats.total_appearances && ` • ${node.stats.total_appearances} sınav`}
            </div>
          </div>
        </div>

        {/* Stats badges */}
        <div className="flex items-center gap-2 flex-shrink-0">
          {/* Success rate */}
          <div className={`text-center min-w-[60px] ${getSuccessRateColor(successRate)}`}>
            <div className="text-lg sm:text-xl font-bold">
              {successRate.toFixed(0)}%
            </div>
            <div className="text-xs hidden sm:block">Başarı</div>
          </div>

          {/* Recommendation count badge */}
          {node.stats.recommendation_count > 0 && (
            <div className="bg-orange-100 text-orange-700 px-2 py-1 rounded-full border border-orange-300">
              <div className="flex items-center gap-1">
                <span className="text-xs sm:text-sm">💡</span>
                <span className="text-xs sm:text-sm font-bold">{node.stats.recommendation_count}</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Children */}
      {hasChildren && isExpanded && (
        <div className="children">
          {node.children!.map((child, index) => (
            <TreeNode
              key={`${child.name}-${index}`}
              node={child}
              level={level + 1}
              onOutcomeClick={onOutcomeClick}
            />
          ))}
        </div>
      )}
    </div>
  );
};
