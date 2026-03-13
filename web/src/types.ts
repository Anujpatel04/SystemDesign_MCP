export interface ArchitectureComponent {
  name: string;
  description: string;
  responsibilities: string[];
}

export interface InfrastructureItem {
  category: string;
  name: string;
  description: string;
  use_case: string;
}

export interface APIEndpoint {
  method: string;
  path: string;
  description: string;
  request_fields: Record<string, unknown>[];
  response_structure: unknown;
}

export interface DesignResponse {
  system_overview: string;
  functional_requirements: string[];
  non_functional_requirements: string[];
  architecture_components: ArchitectureComponent[];
  infrastructure_stack: InfrastructureItem[];
  api_design: APIEndpoint[];
  architecture_diagram_mermaid: string;
  workflow_diagram_mermaid: string;
  scaling_strategy: string[];
  load_estimate?: {
    qps_estimate?: number;
    storage_gb_estimate?: number;
    bandwidth_mbps_estimate?: number;
    qps_note?: string;
    storage_note?: string;
    bandwidth_note?: string;
  };
}
