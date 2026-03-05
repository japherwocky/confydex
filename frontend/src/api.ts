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

// ============ Regulatory Review API ============

export interface UploadResponse {
  protocol_id: number
  filename: string
  file_size: number
}

export interface ReviewReport {
  executive_summary: {
    overall_rating: string
    top_3_findings: string[]
    recommendation: string
  }
  estimand_assessment: {
    population: string
    population_detail: string
    variable: string
    variable_detail: string
    intercurrent_events: string
    intercurrent_events_detail: string
    population_level_summary: string
    summary_detail: string
    compliance_score: string
  }
  endpoint_assessment: {
    primary_endpoint: string
    approval_pathway: string
    regulatory_precedent: string
    key_risk: string
  }
  competitive_comparison: Array<{
    program: string
    endpoint: string
    estimand_notes: string
    status: string
  }>
  consistency_flags: {
    section_3_vs_section_10: string
    section_3_vs_section_4: string
    section_3_vs_section_5: string
  }
  detailed_findings: Array<{
    finding: string
    risk: string
    recommendation: string
  }>
  recommended_actions: string[]
}

export interface ReviewResponse {
  review_id: number
  status: string
  overall_rating: string
  recommendation: string
  estimand_score: string
  report: ReviewReport
}

export interface ReviewListItem {
  id: number
  protocol_id: number
  filename: string
  overall_rating: string
  recommendation: string
  created_at: string
}

export async function uploadProtocol(file: File): Promise<UploadResponse> {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await axios.post(`${API_BASE}/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export async function generateReview(protocolId: number, llmProvider?: string): Promise<ReviewResponse> {
  const response = await axios.post(`${API_BASE}/review`, {
    protocol_id: protocolId,
    llm_provider: llmProvider,
  })
  return response.data
}

export async function listReviews(): Promise<{ reviews: ReviewListItem[] }> {
  const response = await axios.get(`${API_BASE}/reports`)
  return response.data
}

export async function getReview(reviewId: number): Promise<ReviewResponse & { filename: string }> {
  const response = await axios.get(`${API_BASE}/reports/${reviewId}`)
  return response.data
}
