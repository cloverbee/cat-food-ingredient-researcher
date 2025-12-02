import axios, { AxiosInstance } from 'axios';
import type {
  ProductRead,
  ProductCreate,
  ProductUpdate,
  IngredientRead,
  IngredientCreate,
  IngredientUpdate,
  SearchQuery,
  SearchResponse,
  IngestRequest,
  IngestResponse,
} from './api-types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_V1 = '/api/v1';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // Products API
  async getProducts(): Promise<ProductRead[]> {
    const response = await this.client.get<ProductRead[]>(`${API_V1}/products`);
    return response.data;
  }

  async getProduct(id: number): Promise<ProductRead> {
    const response = await this.client.get<ProductRead>(`${API_V1}/products/${id}`);
    return response.data;
  }

  async createProduct(product: ProductCreate): Promise<ProductRead> {
    const response = await this.client.post<ProductRead>(`${API_V1}/products`, product);
    return response.data;
  }

  async updateProduct(id: number, product: ProductUpdate): Promise<ProductRead> {
    const response = await this.client.put<ProductRead>(`${API_V1}/products/${id}`, product);
    return response.data;
  }

  async deleteProduct(id: number): Promise<void> {
    await this.client.delete(`${API_V1}/products/${id}`);
  }

  // Ingredients API
  async getIngredients(): Promise<IngredientRead[]> {
    const response = await this.client.get<IngredientRead[]>(`${API_V1}/ingredients`);
    return response.data;
  }

  async getIngredient(id: number): Promise<IngredientRead> {
    const response = await this.client.get<IngredientRead>(`${API_V1}/ingredients/${id}`);
    return response.data;
  }

  async createIngredient(ingredient: IngredientCreate): Promise<IngredientRead> {
    const response = await this.client.post<IngredientRead>(`${API_V1}/ingredients`, ingredient);
    return response.data;
  }

  async updateIngredient(id: number, ingredient: IngredientUpdate): Promise<IngredientRead> {
    const response = await this.client.put<IngredientRead>(`${API_V1}/ingredients/${id}`, ingredient);
    return response.data;
  }

  async deleteIngredient(id: number): Promise<void> {
    await this.client.delete(`${API_V1}/ingredients/${id}`);
  }

  // Search API
  async search(query: string): Promise<SearchResponse> {
    const response = await this.client.post<SearchResponse>(`${API_V1}/search`, {
      query,
    } as SearchQuery);
    return response.data;
  }

  // Admin/Ingestion API
  async ingestCSV(fileContent: string, filename: string): Promise<IngestResponse> {
    const response = await this.client.post<IngestResponse>(`${API_V1}/admin/ingest`, {
      file_content: fileContent,
      filename,
    } as IngestRequest);
    return response.data;
  }
}

// Export singleton instance
export const apiClient = new APIClient();

