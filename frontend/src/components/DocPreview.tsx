import { useState, useEffect } from 'react'
import type { SearchResult } from '../api'
import { getTrialDocuments, getDocumentText } from '../api'

interface DocPreviewProps {
  doc: SearchResult | null
}

export default function DocPreview({ doc }: DocPreviewProps) {
  const [text, setText] = useState<string>('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!doc) {
      setText('')
      return
    }

    setLoading(true)
    getDocumentText(doc.nct_id, doc.id)
      .then(setText)
      .catch((err) => {
        console.error('Failed to load text:', err)
        setText('Failed to load document text')
      })
      .finally(() => setLoading(false))
  }, [doc])

  if (!doc) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500 h-96 flex items-center justify-center">
        Select a document to preview
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow h-[600px] flex flex-col">
      {/* Header */}
      <div className="p-4 border-b">
        <div className="flex items-center gap-2 mb-2">
          <span className="font-mono text-sm text-blue-600">{doc.nct_id}</span>
          <span className="px-2 py-0.5 text-xs bg-gray-100 rounded">{doc.doc_type}</span>
        </div>
        <h3 className="font-medium text-gray-900">{doc.title}</h3>
        <p className="text-sm text-gray-500">Score: {(doc.score * 100).toFixed(1)}%</p>
      </div>

      {/* Text content */}
      <div className="flex-1 overflow-auto p-4">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
          </div>
        ) : text ? (
          <pre className="text-sm text-gray-700 whitespace-pre-wrap font-mono">
            {text.slice(0, 5000)}
            {text.length > 5000 && '\n\n... (truncated for preview)'}
          </pre>
        ) : (
          <p className="text-gray-500">No text available for this document</p>
        )}
      </div>
    </div>
  )
}
