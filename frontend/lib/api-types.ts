// API Types for Cat Food Ingredient Researcher

export interface IngredientBase {
  name: string;
  description?: string | null;
  nutritional_value?: Record<string, any> | null;
  common_allergens?: string[] | null;
}

export interface IngredientCreate extends IngredientBase {}

export interface IngredientUpdate {
  name?: string | null;
  description?: string | null;
  nutritional_value?: Record<string, any> | null;
  common_allergens?: string[] | null;
}

export interface IngredientRead extends IngredientBase {
  id: number;
}

export interface ProductBase {
  name: string;
  brand: string;
  price?: number | null;
  age_group?: string | null;
  food_type?: string | null;
  description?: string | null;
  full_ingredient_list?: string | null;
}

export interface ProductCreate extends ProductBase {
  ingredient_ids?: number[];
}

export interface ProductUpdate {
  name?: string | null;
  brand?: string | null;
  price?: number | null;
  age_group?: string | null;
  food_type?: string | null;
  description?: string | null;
  full_ingredient_list?: string | null;
}

export interface ProductRead extends ProductBase {
  id: number;
  ingredients: IngredientRead[];
}

export interface SearchQuery {
  query: string;
}

export interface SearchResponse {
  result: string;
}

export interface IngestRequest {
  file_content: string;
  filename: string;
}

export interface IngestResponse {
  message: string;
  products_created: number;
}

// API Response types
export interface APIResponse<T> {
  data?: T;
  error?: string;
}

// Filter types for frontend
export interface ProductFilters {
  food_type?: 'Wet' | 'Dry' | 'Snack' | null;
  age_group?: 'Kitten' | 'Adult' | 'Senior' | null;
  brand?: string | null;
  min_price?: number | null;
  max_price?: number | null;
}

