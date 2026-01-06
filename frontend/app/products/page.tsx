'use client';

import { useState } from 'react';
import { useProducts } from '@/lib/api-hooks';
import { ProductCard } from '@/components/products/product-card';
import { FilterPanel } from '@/components/products/filter-panel';
import { ProductFilters } from '@/lib/api-types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import Link from 'next/link';
import { ArrowLeft, Plus, Search } from 'lucide-react';

export default function ProductsPage() {
  const { data: products, isLoading, error } = useProducts();
  const [filters, setFilters] = useState<ProductFilters>({});
  const [searchQuery, setSearchQuery] = useState('');

  // Filter and search products
  const filteredProducts = products?.filter((product) => {
    // Apply filters
    if (filters.food_type && product.food_type !== filters.food_type) return false;
    if (filters.age_group && !product.age_group?.toLowerCase().includes(filters.age_group.toLowerCase())) return false;
    if (filters.brand && !product.brand?.toLowerCase().includes(filters.brand.toLowerCase())) return false;
    if (filters.min_price && product.price && product.price < filters.min_price) return false;
    if (filters.max_price && product.price && product.price > filters.max_price) return false;

    // Apply search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        product.name.toLowerCase().includes(query) ||
        product.brand.toLowerCase().includes(query) ||
        product.description?.toLowerCase().includes(query) ||
        product.full_ingredient_list?.toLowerCase().includes(query)
      );
    }

    return true;
  });

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/">
                <Button variant="ghost" size="icon">
                  <ArrowLeft className="h-5 w-5" />
                </Button>
              </Link>
              <div>
                <h1 className="text-3xl font-bold">All Products</h1>
                <p className="text-muted-foreground mt-1">
                  Browse and manage cat food products
                </p>
              </div>
            </div>
            <Link href="/products/new">
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Add Product
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Filters Sidebar */}
          <div className="lg:col-span-1">
            <div className="space-y-4">
              <FilterPanel filters={filters} onFiltersChange={setFilters} />

              {/* Search Box */}
              <div className="mt-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                  <Input
                    type="text"
                    placeholder="Search products..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  Search by name, brand, description, or ingredients
                </p>
              </div>
            </div>
          </div>

          {/* Products Grid */}
          <div className="lg:col-span-3">
            {/* Stats */}
            <div className="mb-6">
              <p className="text-sm text-muted-foreground">
                {isLoading
                  ? 'Loading...'
                  : `Showing ${filteredProducts?.length || 0} of ${products?.length || 0} products`}
              </p>
            </div>

            {/* Loading State */}
            {isLoading && (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                <p className="mt-2 text-muted-foreground">Loading products...</p>
              </div>
            )}

            {/* Error State */}
            {error && (
              <div className="text-center py-12">
                <p className="text-destructive">Error loading products. Make sure the backend is running.</p>
                <Button onClick={() => window.location.reload()} className="mt-4">
                  Retry
                </Button>
              </div>
            )}

            {/* Empty State */}
            {!isLoading && filteredProducts && filteredProducts.length === 0 && (
              <div className="text-center py-12">
                <p className="text-muted-foreground mb-4">
                  {products && products.length > 0
                    ? 'No products found matching your criteria.'
                    : 'No products available yet.'}
                </p>
                <Link href="/products/new">
                  <Button>
                    <Plus className="h-4 w-4 mr-2" />
                    Add Your First Product
                  </Button>
                </Link>
              </div>
            )}

            {/* Products Grid */}
            {filteredProducts && filteredProducts.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                {filteredProducts.map((product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}






