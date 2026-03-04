import type { SearchResult } from '../api'

interface ResultsListProps {
  results: SearchResult[]
  loading: boolean
  query: string
  onSelect: (doc: SearchResult) => void
  selectedId?: number
}

export default function ResultsList({ results, loading, query, onSelect, selectedId }: ResultsListProps) {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-2 text-gray-500">Searching...</p>
      </div>
    )
  }

  if (!query) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
        Enter a search query to find clinical trial documents
      </div>
    )
  }

  if (results.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
        No results found for "{query}"
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow divide-y">
      {results.map((result) => (
        <div
          key={result.id}
          onClick={() => onSelect(result)}
          className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${
            selectedId === result.id ? 'bg-blue-50 border-l-4 border-blue-600' : ''
          }`}
        >
          <div className="flex justify-between items-start gap-4">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="font-mono text-sm text-blue-600">{result.nct_id}</span>
                <span className="text-xs text-gray-400">#{result.rank}</span>
                <span className="px-2 py-0.5 text-xs bg-gray-100 rounded">{result.doc_type}</span>
              </div>
              <h3 className="mt-1 font-medium text-gray-900 truncate">{result.title}</h3>
              <p 
                className="mt-1 text-sm text-gray-600 line-clamp-2"
                dangerouslySetInnerHTML={{ __html: result.snippet }}
              />
            </div>
            <div className="text-right shrink-0">
              <div className="text-sm font-medium text-gray-900">
                {(result.score * 100).toFixed(0)}%
              </div>
              <div className="text-xs text-gray-500">relevance</div>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
