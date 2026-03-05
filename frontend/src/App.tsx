import { useState, useEffect } from 'react'
import { listReviews, getReview, type UploadResponse, type ReviewResponse } from './api'
import FileUpload from './components/FileUpload'
import ReviewReport from './components/ReviewReport'

type View = 'upload' | 'review' | 'history'

function App() {
  const [view, setView] = useState<View>('upload')
  const [currentProtocolId, setCurrentProtocolId] = useState<number | null>(null)
  const [currentReview, setCurrentReview] = useState<ReviewResponse | null>(null)
  const [reviews, setReviews] = useState<{ reviews: Array<{ id: number; filename: string; overall_rating: string; recommendation: string; created_at: string }> }>({ reviews: [] })
  const [analyzing, setAnalyzing] = useState(false)

  useEffect(() => {
    loadReviews()
  }, [])

  const loadReviews = async () => {
    try {
      const data = await listReviews()
      setReviews(data)
    } catch (error) {
      console.error('Failed to load reviews:', error)
    }
  }

  const handleUploadComplete = async (response: UploadResponse) => {
    setCurrentProtocolId(response.protocol_id)
    
    // Trigger review generation
    setAnalyzing(true)
    try {
      const review = await generateReview(response.protocol_id)
      setCurrentReview(review)
      setView('review')
      loadReviews()
    } catch (error) {
      console.error('Review failed:', error)
    } finally {
      setAnalyzing(false)
    }
  }

  const generateReview = async (protocolId: number) => {
    const response = await fetch('/api/review', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ protocol_id: protocolId }),
    })
    if (!response.ok) throw new Error('Review failed')
    return response.json()
  }

  const handleSelectReview = async (reviewId: number) => {
    try {
      const review = await getReview(reviewId)
      setCurrentReview(review)
      setView('review')
    } catch (error) {
      console.error('Failed to load review:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Confydex</h1>
              <p className="text-sm text-gray-500">Protocol Section 3 Regulatory Review</p>
            </div>
            <nav className="flex gap-4">
              <button
                onClick={() => setView('upload')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  view === 'upload' 
                    ? 'bg-blue-600 text-white' 
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                Upload
              </button>
              <button
                onClick={() => setView('history')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  view === 'history' 
                    ? 'bg-blue-600 text-white' 
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                History ({reviews.reviews.length})
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-5xl mx-auto px-4 py-6">
        {analyzing && (
          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center gap-3">
              <svg className="animate-spin h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <span className="text-blue-700">Analyzing protocol with LLM...</span>
            </div>
          </div>
        )}

        {view === 'upload' && (
          <FileUpload onUploadComplete={handleUploadComplete} />
        )}

        {view === 'review' && currentReview && (
          <ReviewReport 
            report={currentReview.report} 
            filename={(currentReview as any).filename || 'Protocol'} 
          />
        )}

        {view === 'history' && (
          <div className="bg-white rounded-lg shadow-sm border">
            <div className="p-6 border-b">
              <h2 className="text-lg font-semibold text-gray-900">Review History</h2>
            </div>
            
            {reviews.reviews.length === 0 ? (
              <div className="p-6 text-center text-gray-500">
                No reviews yet. Upload a protocol to get started.
              </div>
            ) : (
              <div className="divide-y">
                {reviews.reviews.map((review) => (
                  <button
                    key={review.id}
                    onClick={() => handleSelectReview(review.id)}
                    className="w-full p-4 hover:bg-gray-50 text-left transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900">{review.filename}</p>
                        <p className="text-sm text-gray-500">
                          {new Date(review.created_at).toLocaleString()}
                        </p>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          review.overall_rating === 'High' ? 'bg-red-100 text-red-800' :
                          review.overall_rating === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {review.overall_rating} Risk
                        </span>
                        <span className="text-gray-400">→</span>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  )
}

export default App
