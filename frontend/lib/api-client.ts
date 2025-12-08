import axios, { AxiosInstance, AxiosError } from "axios";
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
} from "./api-types";

// Validate API URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

if (!process.env.NEXT_PUBLIC_API_URL && typeof window === "undefined") {
  console.warn("NEXT_PUBLIC_API_URL is not set, using default:", API_BASE_URL);
}

// Validate URL format
try {
  new URL(API_BASE_URL);
} catch (error) {
  throw new Error(`Invalid API_BASE_URL format: ${API_BASE_URL}`);
}

const API_V1 = "/api/v1";

// Request timeout (30 seconds)
const REQUEST_TIMEOUT = 30000;

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: REQUEST_TIMEOUT,
      headers: {
        "Content-Type": "application/json",
      },
      // CSRF protection (if backend supports it)
      withCredentials: true,
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add request timestamp for debugging
        config.headers["X-Request-Time"] = new Date().toISOString();
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        // Log error for debugging (in development)
        if (process.env.NODE_ENV === "development") {
          console.error("API Error:", {
            url: error.config?.url,
            method: error.config?.method,
            status: error.response?.status,
            message: error.message,
          });
        }

        // Don't expose internal error details to user
        const userMessage = this.getUserFriendlyError(error);
        return Promise.reject(new Error(userMessage));
      }
    );
  }

  private getUserFriendlyError(error: AxiosError): string {
    if (error.code === "ECONNABORTED") {
      return "Request timed out. Please try again.";
    }

    if (!error.response) {
      return "Network error. Please check your connection.";
    }

    switch (error.response.status) {
      case 400:
        return "Invalid request. Please check your input.";
      case 401:
        return "Unauthorized. Please log in.";
      case 403:
        return "Access denied. You don't have permission.";
      case 404:
        return "Resource not found.";
      case 429:
        return "Too many requests. Please try again later.";
      case 500:
        return "Server error. Please try again later.";
      default:
        return "An error occurred. Please try again.";
    }
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
    const response = await this.client.put<IngredientRead>(
      `${API_V1}/ingredients/${id}`,
      ingredient
    );
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
    // Validate file size (5MB limit)
    const MAX_SIZE = 5 * 1024 * 1024;
    const sizeInBytes = new Blob([fileContent]).size;

    if (sizeInBytes > MAX_SIZE) {
      throw new Error("File size exceeds 5MB limit");
    }

    // Basic CSV validation
    if (!this.validateCSVFormat(fileContent)) {
      throw new Error("Invalid CSV format");
    }

    const response = await this.client.post<IngestResponse>(`${API_V1}/admin/ingest`, {
      file_content: fileContent,
      filename,
    } as IngestRequest);
    return response.data;
  }

  private validateCSVFormat(content: string): boolean {
    const lines = content.trim().split("\n");

    if (lines.length < 2) {
      return false; // Need at least header + 1 data row
    }

    // Check required headers
    const headers = lines[0].toLowerCase();
    const requiredHeaders = ["name", "brand", "price", "age_group", "food_type", "ingredients"];

    return requiredHeaders.every((header) => headers.includes(header));
  }
}

// Export singleton instance
export const apiClient = new APIClient();
