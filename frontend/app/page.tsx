'use client';

import { useState } from 'react';
import { useProducts } from '@/lib/api-hooks';
import { apiClient } from '@/lib/api-client';
import { ProductCard } from '@/components/products/product-card';
import { SearchBar } from '@/components/search/search-bar';
import { FilterPanel } from '@/components/products/filter-panel';
import { ProductFilters } from '@/lib/api-types';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

export default function Home() {
  const { data: products, isLoading, error } = useProducts();
  const [filters, setFilters] = useState<ProductFilters>({});
  const [searchResult, setSearchResult] = useState<string | null>(null);
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = async (query: string) => {
    setIsSearching(true);
    try {
      const result = await apiClient.search(query);
      setSearchResult(result.result);
    } catch (err) {
      setSearchResult('Error performing search');
    } finally {
      setIsSearching(false);
    }
  };

  const filteredProducts = products?.filter((product) => {
    if (filters.food_type && product.food_type !== filters.food_type) return false;
    if (filters.age_group && !product.age_group?.toLowerCase().includes(filters.age_group.toLowerCase())) return false;
    if (filters.brand && !product.brand?.toLowerCase().includes(filters.brand.toLowerCase())) return false;
    if (filters.min_price && product.price && product.price < filters.min_price) return false;
    if (filters.max_price && product.price && product.price > filters.max_price) return false;
    return true;
  });

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">🐱 Cat Food Ingredient Researcher</h1>
              <p className="text-muted-foreground mt-1">
                Research and analyze cat food products and ingredients
              </p>
            </div>
            <div className="flex gap-3">
              <Link href="/products">
                <Button variant="outline">Products</Button>
              </Link>
              <Link href="/ingredients">
                <Button variant="outline">Ingredients</Button>
              </Link>
              <Link href="/admin">
                <Button>Admin</Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Search Section */}
        <section className="mb-8">
          <SearchBar onSearch={handleSearch} isLoading={isSearching} />
          {searchResult && (
            <div className="mt-4 p-4 bg-card border rounded-lg">
              <h3 className="font-semibold mb-2">Search Results:</h3>
              <p className="whitespace-pre-wrap">{searchResult}</p>
            </div>
          )}
        </section>

        {/* Products Section */}
        <section>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold">Products</h2>
            <Link href="/products/new">
              <Button>Add Product</Button>
            </Link>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Filters Sidebar */}
            <div className="lg:col-span-1">
              <FilterPanel filters={filters} onFiltersChange={setFilters} />
            </div>

            {/* Products Grid */}
            <div className="lg:col-span-3">
              {isLoading && (
                <div className="text-center py-12">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                  <p className="mt-2 text-muted-foreground">Loading products...</p>
                </div>
              )}

              {error && (
                <div className="text-center py-12">
                  <p className="text-destructive">Error loading products. Make sure the backend is running.</p>
                </div>
              )}

              {filteredProducts && filteredProducts.length === 0 && (
                <div className="text-center py-12">
                  <p className="text-muted-foreground">No products found matching your criteria.</p>
                </div>
              )}

              {filteredProducts && filteredProducts.length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                  {filteredProducts.map((product) => (
                    <ProductCard key={product.id} product={product} />
                  ))}
                </div>
              )}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
