// frontend/src/services/api.ts
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000'

export interface Brand {
  id: string
  name: string
  industry: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Mention {
  id: string
  brand_id: string
  content: string
  platform: string
  sentiment_score: number
  sentiment_label: string
  crisis_probability: number
  published_at: string
  likes_count: number
  shares_count: number
  comments_count: number
}

class ApiService {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    })

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`)
    }

    return response.json()
  }

  // Brands
  async getBrands(): Promise<Brand[]> {
    return this.request<Brand[]>('/api/brands/')
  }

  async createBrand(brand: Omit<Brand, 'id' | 'created_at' | 'updated_at' | 'is_active'>): Promise<Brand> {
    return this.request<Brand>('/api/brands/', {
      method: 'POST',
      body: JSON.stringify(brand),
    })
  }

  // Mentions
  async getMentions(params?: {
    brand_id?: string
    platform?: string
    days?: number
    limit?: number
  }): Promise<Mention[]> {
    const searchParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString())
        }
      })
    }
    
    return this.request<Mention[]>(`/api/mentions/?${searchParams}`)
  }

  // Analytics
  async getSentimentOverview(brandId: string, days: number = 7) {
    return this.request(`/api/analytics/sentiment-overview?brand_id=${brandId}&days=${days}`)
  }

  async getPlatformBreakdown(brandId: string, days: number = 30) {
    return this.request(`/api/analytics/platform-breakdown?brand_id=${brandId}&days=${days}`)
  }

  async getCrisisMetrics(brandId: string, threshold: number = 0.7) {
    return this.request(`/api/analytics/crisis-metrics?brand_id=${brandId}&threshold=${threshold}`)
  }

  // Demo data
  async getDemoData() {
    return this.request('/api/demo/sample-data')
  }
}

export const apiService = new ApiService()