import { useState, useEffect } from 'react'
import { search, getStats, type SearchResult, type Stats } from './api'
import SearchBar from './components/SearchBar'
import ResultsList from './components/ResultsList'
import DocPreview from './components/DocPreview'

function App() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState<Stats | null>(null)
  const [selectedDoc, setSelectedDoc] = useState<SearchResult | null>(null)
  const [searchMethod, setSearchMethod] = useState<'hybrid' | 'keyword' | 'semantic'>('hybrid')

  useEffect(() => {
    getStats().then(setStats).catch(console.error)
  }, [])

  const handleSearch = async (searchQuery: string) => {
    setQuery(searchQuery)
    if (!searchQuery.trim()) {
      setResults([])
      return
    }
    
    setLoading(true)
    try {
      const response = await search(searchQuery, 20, searchMethod)
      setResults(response.results)
    } catch (error) {
      console.error('Search failed:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">Confydex</h1>
          <p className="text-sm text-gray-500">Clinical Trial Document Search</p>
        </div>
      </header>

      {/* Stats bar */}
      {stats && (
        <div className="bg-white border-b">
          <div className="max-w-7xl mx-auto px-4 py-2 flex gap-6 text-sm text-gray-600">
            <span>Trials: <strong>{stats.trials_indexed}</strong></span>
            <span>Documents: <strong>{stats.documents_indexed}</strong></span>
            <span>With embeddings: <strong>{stats.documents_with_embeddings}</strong></span>
            <span>Storage: <strong>{stats.storage_mb} MB</strong></span>
          </div>
        </div>
      )}

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Search and results */}
          <div className="lg:col-span-2 space-y-4">
            <SearchBar 
              onSearch={handleSearch} 
              loading={loading}
              method={searchMethod}
              onMethodChange={setSearchMethod}
            />
            <ResultsList 
              results={results} 
              loading={loading}
              query={query}
              onSelect={setSelectedDoc}
              selectedId={selectedDoc?.id}
            />
          </div>

          {/* Preview panel */}
          <div className="lg:col-span-1">
            <DocPreview 
              doc={selectedDoc}
            />
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
