import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './api-client';
import type {
  ProductCreate,
  ProductUpdate,
  IngredientCreate,
  IngredientUpdate,
} from './api-types';

// Products hooks
export function useProducts() {
  return useQuery({
    queryKey: ['products'],
    queryFn: () => apiClient.getProducts(),
  });
}

export function useProduct(id: number) {
  return useQuery({
    queryKey: ['products', id],
    queryFn: () => apiClient.getProduct(id),
    enabled: !!id,
  });
}

export function useCreateProduct() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (product: ProductCreate) => apiClient.createProduct(product),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
    },
  });
}

export function useUpdateProduct() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, product }: { id: number; product: ProductUpdate }) =>
      apiClient.updateProduct(id, product),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
    },
  });
}

export function useDeleteProduct() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => apiClient.deleteProduct(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
    },
  });
}

// Ingredients hooks
export function useIngredients() {
  return useQuery({
    queryKey: ['ingredients'],
    queryFn: () => apiClient.getIngredients(),
  });
}

export function useIngredient(id: number) {
  return useQuery({
    queryKey: ['ingredients', id],
    queryFn: () => apiClient.getIngredient(id),
    enabled: !!id,
  });
}

export function useCreateIngredient() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (ingredient: IngredientCreate) => apiClient.createIngredient(ingredient),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ingredients'] });
    },
  });
}

export function useUpdateIngredient() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ingredient }: { id: number; ingredient: IngredientUpdate }) =>
      apiClient.updateIngredient(id, ingredient),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ingredients'] });
    },
  });
}

export function useDeleteIngredient() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => apiClient.deleteIngredient(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ingredients'] });
    },
  });
}

// Search hook
export function useSearch(query: string, enabled = false) {
  return useQuery({
    queryKey: ['search', query],
    queryFn: () => apiClient.search(query),
    enabled: enabled && query.length > 0,
  });
}

// Ingest hook
export function useIngestCSV() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ fileContent, filename }: { fileContent: string; filename: string }) =>
      apiClient.ingestCSV(fileContent, filename),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      queryClient.invalidateQueries({ queryKey: ['ingredients'] });
    },
  });
}


