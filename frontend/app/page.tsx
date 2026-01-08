'use client';

import { useState, useMemo } from 'react';
import { useProducts } from '@/lib/api-hooks';
import { apiClient } from '@/lib/api-client';
import { ProductCard } from '@/components/products/product-card';
import { SearchBar } from '@/components/search/search-bar';
import { FilterPanel } from '@/components/products/filter-panel';
import { ProductFilters, ProductRead } from '@/lib/api-types';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { Header } from '@/components/layout/header';
import { ArrowDown, Sparkles, X, ChevronRight } from 'lucide-react';

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

  // Parse search results to extract product names and match with products
  const matchedProducts = useMemo(() => {
    if (!searchResult || !products) return [];

    // Extract product names from search result
    // Format: "- Product Name by Brand ($price) - food_type food for age_group"
    const productLines = searchResult
      .split('\n')
      .filter(line => line.trim().startsWith('-') && line.includes(' by '));

    const matched: ProductRead[] = [];

    productLines.forEach((line) => {
      // Extract product name (text between "- " and " by ")
      const match = line.match(/^-\s*(.+?)\s+by\s+/);
      if (match) {
        const productName = match[1].trim();
        // Find matching product (fuzzy match)
        const product = products.find(p => 
          p.name.toLowerCase().includes(productName.toLowerCase()) ||
          productName.toLowerCase().includes(p.name.toLowerCase())
        );
        if (product && !matched.find(p => p.id === product.id)) {
          matched.push(product);
        }
      }
    });

    return matched;
  }, [searchResult, products]);

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
              <div className="mt-8 max-w-5xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="bg-background/95 backdrop-blur-xl rounded-2xl border border-border/50 shadow-2xl overflow-hidden">
                  {/* Header */}
                  <div className="flex items-center justify-between px-6 py-4 border-b border-border/50 bg-gradient-to-r from-primary/5 via-primary/3 to-transparent">
                    <div className="flex items-center gap-3">
                      <div className="p-2.5 rounded-xl bg-primary/10 border border-primary/20 shadow-sm">
                        <Sparkles className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-lg text-foreground">AI Search Results</h3>
                        <p className="text-xs text-muted-foreground font-medium">
                          {matchedProducts.length > 0 
                            ? `Found ${matchedProducts.length} product(s)`
                            : 'Powered by intelligent analysis'}
                        </p>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setSearchResult(null)}
                      className="h-9 w-9 rounded-lg hover:bg-background/80 transition-colors"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                  
                  {/* Content */}
                  <div className="p-6 md:p-8 bg-gradient-to-b from-background to-background/95">
                    {/* Product List Section */}
                    {matchedProducts.length > 0 && (
                      <div className="space-y-3 mb-6">
                        {matchedProducts.map((product) => (
                          <Link
                            key={product.id}
                            href={`/products/${product.id}`}
                            className="block"
                          >
                            <div className="group relative flex items-center gap-4 p-4 rounded-lg border border-border/50 bg-card hover:bg-muted/50 hover:border-primary/50 transition-all cursor-pointer">
                              {product.image_url && (
                                <div className="relative w-16 h-16 rounded-lg overflow-hidden bg-muted/20 shrink-0">
                                  {product.image_url.includes('catfooddb.com') ? (
                                    <img
                                      src={`/api/image-proxy?url=${encodeURIComponent(product.image_url)}`}
                                      alt={product.name}
                                      className="absolute inset-0 w-full h-full object-cover"
                                      onError={(e) => {
                                        e.currentTarget.style.display = 'none';
                                      }}
                                    />
                                  ) : (
                                    <img
                                      src={product.image_url}
                                      alt={product.name}
                                      className="absolute inset-0 w-full h-full object-cover"
                                      onError={(e) => {
                                        e.currentTarget.style.display = 'none';
                                      }}
                                    />
                                  )}
                                </div>
                              )}
                              <div className="flex-1 min-w-0">
                                <h4 className="font-semibold text-foreground group-hover:text-primary transition-colors truncate">
                                  {product.name}
                                </h4>
                                <p className="text-sm text-muted-foreground truncate">
                                  {product.brand}
                                  {product.price && ` • $${product.price.toFixed(2)}`}
                                  {product.food_type && ` • ${product.food_type}`}
                                  {product.age_group && ` • ${product.age_group}`}
                                </p>
                              </div>
                              <ChevronRight className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors shrink-0" />
                            </div>
                          </Link>
                        ))}
                      </div>
                    )}

                    {/* Original AI Response Section */}
                    <div className="space-y-6">
                      {/* Parse and format the result */}
                      {(() => {
                        const lines = searchResult.split('\n').filter(line => line.trim());
                        const sections: Array<{ type: 'table' | 'list' | 'text' | 'heading'; content: string[] }> = [];
                        let currentSection: { type: 'table' | 'list' | 'text' | 'heading'; content: string[] } | null = null;
                        
                        lines.forEach((line, index) => {
                          const trimmed = line.trim();
                          
                          // Detect headings
                          if (trimmed.match(/^#{1,3}\s/) || (trimmed.length < 100 && trimmed.endsWith(':'))) {
                            if (currentSection) sections.push(currentSection);
                            currentSection = { type: 'heading', content: [trimmed.replace(/^#+\s/, '')] };
                            sections.push(currentSection);
                            currentSection = null;
                          }
                          // Detect table rows (contains | separator)
                          else if (trimmed.includes('|') && trimmed.split('|').length >= 3) {
                            if (!currentSection || currentSection.type !== 'table') {
                              if (currentSection) sections.push(currentSection);
                              currentSection = { type: 'table', content: [] };
                            }
                            currentSection.content.push(trimmed);
                          }
                          // Detect list items
                          else if (trimmed.match(/^[-*•]\s/) || trimmed.match(/^\d+[.)]\s/)) {
                            if (!currentSection || currentSection.type !== 'list') {
                              if (currentSection) sections.push(currentSection);
                              currentSection = { type: 'list', content: [] };
                            }
                            currentSection.content.push(trimmed);
                          }
                          // Regular text
                          else {
                            if (!currentSection || currentSection.type !== 'text') {
                              if (currentSection) sections.push(currentSection);
                              currentSection = { type: 'text', content: [] };
                            }
                            currentSection.content.push(trimmed);
                          }
                        });
                        if (currentSection) sections.push(currentSection);
                        
                        return sections.map((section, idx) => {
                          if (section.type === 'heading') {
                            return (
                              <h4 key={idx} className="text-xl font-bold text-foreground mt-8 mb-4 first:mt-0 pb-2 border-b border-border/30">
                                {section.content[0]}
                              </h4>
                            );
                          }
                          
                          if (section.type === 'table') {
                            const rows = section.content
                              .map(row => {
                                if (row.includes('|')) {
                                  const cells = row.split('|').map(cell => cell.trim()).filter(cell => cell);
                                  // Filter out separator rows (e.g., |---|---|)
                                  if (cells.every(cell => /^[-:]+$/.test(cell))) return null;
                                  return cells;
                                }
                                return null;
                              })
                              .filter((row): row is string[] => row !== null && row.length > 0);
                            
                            if (rows.length === 0) {
                              // Fallback to text if table parsing fails
                              return (
                                <div key={idx} className="space-y-2">
                                  {section.content.map((para, paraIdx) => (
                                    <p key={paraIdx} className="text-sm md:text-base text-foreground/85 leading-relaxed font-mono">
                                      {para}
                                    </p>
                                  ))}
                                </div>
                              );
                            }
                            
                            const isHeaderRow = (row: string[]) => {
                              // Check if row looks like a header (short cells, mostly uppercase or title case)
                              return row.every(cell => cell.length < 40) && 
                                     row.some(cell => /^[A-Z]/.test(cell) || cell.split(' ').every(word => /^[A-Z]/.test(word)));
                            };
                            
                            const hasHeader = rows.length > 1 && isHeaderRow(rows[0]);
                            
                            return (
                              <div key={idx} className="overflow-x-auto -mx-2">
                                <div className="inline-block min-w-full align-middle">
                                  <div className="overflow-hidden border border-border/50 rounded-xl shadow-sm bg-card">
                                    <table className="min-w-full divide-y divide-border/50">
                                      {hasHeader && (
                                        <thead className="bg-muted/40">
                                          <tr>
                                            {rows[0].map((cell, cellIdx) => (
                                              <th
                                                key={cellIdx}
                                                className="px-6 py-3.5 text-left text-xs font-semibold text-foreground uppercase tracking-wider"
                                              >
                                                {cell}
                                              </th>
                                            ))}
                                          </tr>
                                        </thead>
                                      )}
                                      <tbody className="bg-background divide-y divide-border/30">
                                        {rows.slice(hasHeader ? 1 : 0).map((row, rowIdx) => (
                                          <tr key={rowIdx} className="hover:bg-muted/20 transition-colors">
                                            {row.map((cell, cellIdx) => (
                                              <td
                                                key={cellIdx}
                                                className="px-6 py-4 text-sm text-foreground/90"
                                              >
                                                {cell}
                                              </td>
                                            ))}
                                          </tr>
                                        ))}
                                      </tbody>
                                    </table>
                                  </div>
                                </div>
                              </div>
                            );
                          }
                          
                          if (section.type === 'list') {
                            return (
                              <ul key={idx} className="space-y-2 list-none">
                                {section.content.map((item, itemIdx) => {
                                  // Skip items that are already shown in the product list above
                                  if (item.includes(' by ') && matchedProducts.length > 0) {
                                    return null;
                                  }
                                  return (
                                    <li key={itemIdx} className="flex items-start gap-3 text-foreground/90">
                                      <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-primary shrink-0" />
                                      <span className="text-sm md:text-base leading-relaxed">
                                        {item.replace(/^[-*•]\s/, '').replace(/^\d+[.)]\s/, '')}
                                      </span>
                                    </li>
                                  );
                                })}
                              </ul>
                            );
                          }
                          
                          // Text section
                          return (
                            <div key={idx} className="space-y-3">
                              {section.content.map((para, paraIdx) => (
                                <p
                                  key={paraIdx}
                                  className="text-sm md:text-base text-foreground/85 leading-relaxed"
                                >
                                  {para}
                                </p>
                              ))}
                            </div>
                          );
                        });
                      })()}
                    </div>
                  </div>
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
