import { useState, FormEvent } from 'react'

interface SearchBarProps {
  onSearch: (query: string) => void
  loading: boolean
  method: 'hybrid' | 'keyword' | 'semantic'
  onMethodChange: (method: 'hybrid' | 'keyword' | 'semantic') => void
}

export default function SearchBar({ onSearch, loading, method, onMethodChange }: SearchBarProps) {
  const [query, setQuery] = useState('')

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    onSearch(query)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search clinical trial documents..."
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
        />
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>
      
      <div className="flex gap-4 text-sm">
        <label items-center gap- className="flex2">
          <input
            type="radio"
            name="method"
            value="hybrid"
            checked={method === 'hybrid'}
            onChange={() => onMethodChange('hybrid')}
          />
          <span>Hybrid</span>
        </label>
        <label className="flex items-center gap-2">
          <input
            type="radio"
            name="method"
            value="keyword"
            checked={method === 'keyword'}
            onChange={() => onMethodChange('keyword')}
          />
          <span>Keyword</span>
        </label>
        <label className="flex items-center gap-2">
          <input
            type="radio"
            name="method"
            value="semantic"
            checked={method === 'semantic'}
            onChange={() => onMethodChange('semantic')}
          />
          <span>Semantic</span>
        </label>
      </div>
    </form>
  )
}
