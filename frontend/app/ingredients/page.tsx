'use client';

import { useState } from 'react';
import { useIngredients } from '@/lib/api-hooks';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import Link from 'next/link';
import { ArrowLeft, Plus, Search } from 'lucide-react';

export default function IngredientsPage() {
  const { data: ingredients, isLoading, error } = useIngredients();
  const [searchQuery, setSearchQuery] = useState('');

  // Filter ingredients by search query
  const filteredIngredients = ingredients?.filter((ingredient) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      ingredient.name.toLowerCase().includes(query) ||
      ingredient.description?.toLowerCase().includes(query)
    );
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
                <h1 className="text-3xl font-bold">Ingredients</h1>
                <p className="text-muted-foreground mt-1">
                  Browse all cat food ingredients
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Search Bar */}
        <div className="mb-6 max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
            <Input
              type="text"
              placeholder="Search ingredients..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        {/* Stats */}
        <div className="mb-6">
          <p className="text-sm text-muted-foreground">
            {isLoading
              ? 'Loading...'
              : `Showing ${filteredIngredients?.length || 0} of ${ingredients?.length || 0} ingredients`}
          </p>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            <p className="mt-2 text-muted-foreground">Loading ingredients...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="text-center py-12">
            <p className="text-destructive">Error loading ingredients. Make sure the backend is running.</p>
            <Button onClick={() => window.location.reload()} className="mt-4">
              Retry
            </Button>
          </div>
        )}

        {/* Empty State */}
        {!isLoading && filteredIngredients && filteredIngredients.length === 0 && (
          <div className="text-center py-12">
            <p className="text-muted-foreground">
              {ingredients && ingredients.length > 0
                ? 'No ingredients found matching your search.'
                : 'No ingredients available yet.'}
            </p>
          </div>
        )}

        {/* Ingredients Grid */}
        {filteredIngredients && filteredIngredients.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredIngredients.map((ingredient) => (
              <Card key={ingredient.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <CardTitle className="text-lg">{ingredient.name}</CardTitle>
                  {ingredient.description && (
                    <CardDescription className="line-clamp-2">
                      {ingredient.description}
                    </CardDescription>
                  )}
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Nutritional Value */}
                  {ingredient.nutritional_value && (
                    <div>
                      <p className="text-sm font-medium mb-2">Nutritional Value</p>
                      <div className="flex flex-wrap gap-2">
                        {Object.entries(ingredient.nutritional_value).slice(0, 4).map(([key, value]) => (
                          <Badge key={key} variant="outline" className="text-xs">
                            {key}: {String(value)}
                          </Badge>
                        ))}
                        {Object.keys(ingredient.nutritional_value).length > 4 && (
                          <Badge variant="outline" className="text-xs">
                            +{Object.keys(ingredient.nutritional_value).length - 4} more
                          </Badge>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Allergens */}
                  {ingredient.common_allergens && ingredient.common_allergens.length > 0 && (
                    <div>
                      <p className="text-sm font-medium mb-2">Common Allergens</p>
                      <div className="flex flex-wrap gap-2">
                        {ingredient.common_allergens.map((allergen) => (
                          <Badge key={allergen} variant="destructive" className="text-xs">
                            {allergen}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* No allergens message */}
                  {(!ingredient.common_allergens || ingredient.common_allergens.length === 0) && (
                    <div>
                      <Badge variant="secondary" className="text-xs">
                        No known allergens
                      </Badge>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

