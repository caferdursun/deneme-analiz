import { Resource } from '../types';

interface ResourceDeleteModalProps {
  resource: Resource;
  isOpen: boolean;
  onClose: () => void;
  onDeleteOnly: () => void;
  onDeleteAndBlacklist: () => void;
}

export default function ResourceDeleteModal({
  resource,
  isOpen,
  onClose,
  onDeleteOnly,
  onDeleteAndBlacklist,
}: ResourceDeleteModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black bg-opacity-50"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Kaynağı Sil
        </h3>

        <p className="text-sm text-gray-600 mb-4">
          <span className="font-medium">{resource.name}</span> kaynağı için ne yapmak istersiniz?
        </p>

        <div className="space-y-3">
          {/* Option 1: Delete and Blacklist */}
          <button
            onClick={onDeleteAndBlacklist}
            className="w-full px-4 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-left"
          >
            <div className="font-medium">Bu kaynağı bir daha önerme</div>
            <div className="text-sm text-red-100 mt-1">
              Kaynak silinir ve kara listeye eklenir
            </div>
          </button>

          {/* Option 2: Delete Only */}
          <button
            onClick={onDeleteOnly}
            className="w-full px-4 py-3 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors text-left"
          >
            <div className="font-medium">Sadece sil</div>
            <div className="text-sm text-orange-100 mt-1">
              Kaynak silinir, tekrar önerilebilir
            </div>
          </button>

          {/* Option 3: Cancel */}
          <button
            onClick={onClose}
            className="w-full px-4 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
          >
            Vazgeç
          </button>
        </div>
      </div>
    </div>
  );
}
