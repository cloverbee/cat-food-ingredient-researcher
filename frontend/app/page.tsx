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
import { Header } from '@/components/layout/header';
import { ArrowDown } from 'lucide-react';

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

  const scrollToProducts = () => {
    const element = document.getElementById('products');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative py-20 md:py-32 px-4 overflow-hidden">
          <div className="container mx-auto text-center relative z-10 space-y-8">
            <div className="space-y-6 max-w-4xl mx-auto animate-in fade-in slide-in-from-bottom-8 duration-700">
              <h1 className="text-5xl md:text-7xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-br from-foreground to-foreground/60 drop-shadow-sm">
                Find the Perfect Food <br className="hidden md:block" /> for Your Cat
              </h1>
              <p className="text-xl md:text-2xl text-muted-foreground/80 max-w-2xl mx-auto font-light leading-relaxed">
                Research ingredients, compare products, and make informed decisions for your feline friend's health.
              </p>
            </div>
            
            <div className="max-w-2xl mx-auto pt-8 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-100">
               <SearchBar onSearch={handleSearch} isLoading={isSearching} />
            </div>

            {searchResult && (
              <div className="mt-8 p-6 glass rounded-2xl max-w-3xl mx-auto text-left animate-in fade-in slide-in-from-bottom-4 shadow-2xl">
                <h3 className="font-semibold mb-3 text-lg flex items-center gap-2 text-primary">
                  <span className="text-xl">🤖</span> AI Analysis Result
                </h3>
                <div className="prose prose-sm dark:prose-invert max-w-none text-muted-foreground">
                  <p className="whitespace-pre-wrap leading-relaxed">{searchResult}</p>
                </div>
              </div>
            )}
            
            {!searchResult && (
              <div className="pt-12 animate-bounce duration-1000">
                <Button variant="ghost" size="icon" onClick={scrollToProducts} className="rounded-full hover:bg-background/20">
                  <ArrowDown className="h-6 w-6 opacity-50" />
                </Button>
              </div>
            )}
          </div>
        </section>

        {/* Products Section */}
        <section className="container mx-auto px-4 pb-20" id="products">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-3xl font-bold tracking-tight">Explore Products</h2>
              <p className="text-muted-foreground mt-1">Browse our collection of cat food products</p>
            </div>
            <Link href="/products/new">
              <Button size="lg" className="shadow-lg shadow-primary/20">Add Product</Button>
            </Link>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            {/* Filters Sidebar */}
            <div className="lg:col-span-1">
              <FilterPanel filters={filters} onFiltersChange={setFilters} />
            </div>

            {/* Products Grid */}
            <div className="lg:col-span-3">
              {isLoading && (
                <div className="glass rounded-2xl p-12 text-center">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary mb-4"></div>
                  <p className="text-muted-foreground font-medium">Loading products...</p>
                </div>
              )}

              {error && (
                <div className="glass rounded-2xl p-12 text-center border-destructive/20 bg-destructive/5">
                  <p className="text-destructive font-medium">Error loading products. Make sure the backend is running.</p>
                </div>
              )}

              {filteredProducts && filteredProducts.length === 0 && (
                <div className="glass rounded-2xl p-12 text-center">
                  <p className="text-muted-foreground text-lg">No products found matching your criteria.</p>
                  <Button variant="link" onClick={() => setFilters({})} className="mt-2">
                    Clear all filters
                  </Button>
                </div>
              )}

              {filteredProducts && filteredProducts.length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
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
