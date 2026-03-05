import type { ReviewReport } from '../api'

interface ReviewReportDisplayProps {
  report: ReviewReport
  filename: string
}

function getRatingColor(rating: string): string {
  switch (rating.toLowerCase()) {
    case 'high':
      return 'bg-red-100 text-red-800'
    case 'medium':
      return 'bg-yellow-100 text-yellow-800'
    case 'low':
      return 'bg-green-100 text-green-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

function getStatusColor(status: string): string {
  switch (status.toLowerCase()) {
    case 'defined':
      return 'text-green-600'
    case 'partially defined':
      return 'text-yellow-600'
    case 'missing':
      return 'text-red-600'
    default:
      return 'text-gray-600'
  }
}

function getRiskColor(risk: string): string {
  switch (risk.toLowerCase()) {
    case 'h':
      return 'bg-red-100 text-red-800'
    case 'm':
      return 'bg-yellow-100 text-yellow-800'
    case 'l':
      return 'bg-green-100 text-green-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

export default function ReviewReportDisplay({ report, filename }: ReviewReportDisplayProps) {
  const { executive_summary, estimand_assessment, endpoint_assessment, 
          competitive_comparison, consistency_flags, detailed_findings, 
          recommended_actions } = report

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Regulatory Review Report</h2>
            <p className="text-sm text-gray-500 mt-1">{filename}</p>
          </div>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getRatingColor(executive_summary.overall_rating)}`}>
            {executive_summary.overall_rating} Risk
          </span>
        </div>
        
        <div className="mt-4">
          <p className="text-lg font-medium text-gray-900">{executive_summary.recommendation}</p>
        </div>
      </div>

      {/* Executive Summary */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Executive Summary</h3>
        <ul className="space-y-2">
          {executive_summary.top_3_findings.map((finding, idx) => (
            <li key={idx} className="flex items-start gap-2">
              <span className="flex-shrink-0 w-5 h-5 flex items-center justify-center bg-blue-100 text-blue-600 rounded-full text-xs font-bold">
                {idx + 1}
              </span>
              <span className="text-gray-700">{finding}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Estimand Assessment */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Estimand Completeness (ICH E9(R1))</h3>
          <span className="text-lg font-bold text-blue-600">{estimand_assessment.compliance_score}</span>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium text-gray-700">Population</span>
              <span className={`text-sm font-medium ${getStatusColor(estimand_assessment.population)}`}>
                {estimand_assessment.population}
              </span>
            </div>
            <p className="text-sm text-gray-600">{estimand_assessment.population_detail}</p>
          </div>

          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium text-gray-700">Variable (Endpoint)</span>
              <span className={`text-sm font-medium ${getStatusColor(estimand_assessment.variable)}`}>
                {estimand_assessment.variable}
              </span>
            </div>
            <p className="text-sm text-gray-600">{estimand_assessment.variable_detail}</p>
          </div>

          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium text-gray-700">Intercurrent Events</span>
              <span className={`text-sm font-medium ${getStatusColor(estimand_assessment.intercurrent_events)}`}>
                {estimand_assessment.intercurrent_events}
              </span>
            </div>
            <p className="text-sm text-gray-600">{estimand_assessment.intercurrent_events_detail}</p>
          </div>

          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium text-gray-700">Population-Level Summary</span>
              <span className={`text-sm font-medium ${getStatusColor(estimand_assessment.population_level_summary)}`}>
                {estimand_assessment.population_level_summary}
              </span>
            </div>
            <p className="text-sm text-gray-600">{estimand_assessment.summary_detail}</p>
          </div>
        </div>
      </div>

      {/* Endpoint Assessment */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Endpoint Approvability</h3>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div className="p-3 bg-gray-50 rounded-lg text-center">
            <p className="text-xs text-gray-500 uppercase">Endpoint</p>
            <p className="font-semibold text-gray-900">{endpoint_assessment.primary_endpoint}</p>
          </div>
          <div className="p-3 bg-gray-50 rounded-lg text-center">
            <p className="text-xs text-gray-500 uppercase">Pathway</p>
            <p className="font-semibold text-gray-900">{endpoint_assessment.approval_pathway}</p>
          </div>
          <div className="p-3 bg-gray-50 rounded-lg text-center">
            <p className="text-xs text-gray-500 uppercase">Precedent</p>
            <p className="font-semibold text-gray-900">{endpoint_assessment.regulatory_precedent}</p>
          </div>
          <div className="p-3 bg-gray-50 rounded-lg text-center">
            <p className="text-xs text-gray-500 uppercase">Key Risk</p>
            <p className="font-semibold text-red-600 text-sm">{endpoint_assessment.key_risk}</p>
          </div>
        </div>
      </div>

      {/* Competitive Comparison */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Competitive Benchmark</h3>
        
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2 px-3 font-medium text-gray-600">Program</th>
                <th className="text-left py-2 px-3 font-medium text-gray-600">Endpoint</th>
                <th className="text-left py-2 px-3 font-medium text-gray-600">Estimand Notes</th>
                <th className="text-left py-2 px-3 font-medium text-gray-600">Status</th>
              </tr>
            </thead>
            <tbody>
              {competitive_comparison.map((comp, idx) => (
                <tr key={idx} className="border-b last:border-0">
                  <td className="py-2 px-3 font-medium">{comp.program}</td>
                  <td className="py-2 px-3">{comp.endpoint}</td>
                  <td className="py-2 px-3 text-gray-600">{comp.estimand_notes}</td>
                  <td className="py-2 px-3">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                      comp.status === 'approved' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {comp.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Consistency Flags */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Internal Consistency</h3>
        
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <p className="text-xs text-gray-500 mb-1">Section 3 vs 10</p>
            <p className={`font-medium ${
              consistency_flags.section_3_vs_section_10 === 'Aligned' ? 'text-green-600' : 'text-yellow-600'
            }`}>
              {consistency_flags.section_3_vs_section_10}
            </p>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <p className="text-xs text-gray-500 mb-1">Section 3 vs 4</p>
            <p className={`font-medium ${
              consistency_flags.section_3_vs_section_4 === 'Aligned' ? 'text-green-600' : 'text-yellow-600'
            }`}>
              {consistency_flags.section_3_vs_section_4}
            </p>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <p className="text-xs text-gray-500 mb-1">Section 3 vs 5</p>
            <p className={`font-medium ${
              consistency_flags.section_3_vs_section_5 === 'Aligned' ? 'text-green-600' : 'text-yellow-600'
            }`}>
              {consistency_flags.section_3_vs_section_5}
            </p>
          </div>
        </div>
      </div>

      {/* Detailed Findings */}
      {detailed_findings.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Detailed Findings</h3>
          
          <div className="space-y-3">
            {detailed_findings.map((finding, idx) => (
              <div key={idx} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${getRiskColor(finding.risk)}`}>
                  {finding.risk}
                </span>
                <div className="flex-1">
                  <p className="text-gray-700">{finding.finding}</p>
                  <p className="text-sm text-gray-500 mt-1">{finding.recommendation}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommended Actions */}
      {recommended_actions.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recommended Actions</h3>
          
          <ol className="space-y-2">
            {recommended_actions.map((action, idx) => (
              <li key={idx} className="flex items-start gap-3">
                <span className="flex-shrink-0 w-6 h-6 flex items-center justify-center bg-blue-600 text-white rounded-full text-xs font-bold">
                  {idx + 1}
                </span>
                <span className="text-gray-700">{action}</span>
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  )
}
