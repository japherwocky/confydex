import axios from 'axios'

const API_BASE = '/api'

export interface SearchResult {
  id: number
  nct_id: string
  title: string
  doc_type: string
  snippet: string
  score: number
  rank: number
}

export interface SearchResponse {
  results: SearchResult[]
  total: number
  query: string
  method: string
}

export interface TrialDocuments {
  nct_id: string
  title: string
  status: string
  sponsor: string
  conditions: string
  documents: {
    id: number
    doc_type: string
    file_path: string
    page_count: number
    text_length: number
    has_embedding: boolean
  }[]
}

export interface Stats {
  trials_indexed: number
  documents_indexed: number
  documents_with_embeddings: number
  storage_mb: number
}

export async function search(
  query: string,
  limit: number = 20,
  method: string = 'hybrid'
): Promise<SearchResponse> {
  const response = await axios.get(`${API_BASE}/search`, {
    params: { q: query, limit, method },
  })
  return response.data
}

export async function getTrialDocuments(nctId: string): Promise<TrialDocuments> {
  const response = await axios.get(`${API_BASE}/docs/${nctId}`)
  return response.data
}

export async function getDocumentText(nctId: string, docId: number): Promise<string> {
  const response = await axios.get(`${API_BASE}/docs/${nctId}/text/${docId}`)
  return response.data
}

export async function getStats(): Promise<Stats> {
  const response = await axios.get(`${API_BASE}/stats`)
  return response.data
}

export async function healthCheck(): Promise<{ status: string }> {
  const response = await axios.get(`${API_BASE}/health`)
  return response.data
}
