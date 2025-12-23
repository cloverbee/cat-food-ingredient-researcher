'use client';

import { use } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { useProduct, useDeleteProduct } from '@/lib/api-hooks';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, Edit, Trash2, ExternalLink } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

export default function ProductDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const productId = parseInt(resolvedParams.id);
  const { data: product, isLoading, error } = useProduct(productId);
  const deleteProduct = useDeleteProduct();
  const router = useRouter();
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this product?')) {
      return;
    }

    setIsDeleting(true);
    try {
      await deleteProduct.mutateAsync(productId);
      router.push('/');
    } catch (err) {
      alert('Failed to delete product');
      setIsDeleting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          <p className="mt-2 text-muted-foreground">Loading product...</p>
        </div>
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <p className="text-destructive">Product not found</p>
          <Link href="/">
            <Button className="mt-4">Go Home</Button>
          </Link>
        </div>
      </div>
    );
  }

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
                <h1 className="text-3xl font-bold">{product.name}</h1>
                <p className="text-muted-foreground mt-1">{product.brand}</p>
              </div>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="icon" title="Edit product">
                <Edit className="h-4 w-4" />
              </Button>
              <Button
                variant="destructive"
                size="icon"
                title="Delete product"
                onClick={handleDelete}
                disabled={isDeleting}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Product Image */}
          {product.image_url && (
            <Card>
              <CardContent className="p-0">
                <div className="relative w-full h-96 overflow-hidden rounded-lg">
                  <Image
                    src={product.image_url}
                    alt={product.name}
                    fill
                    className="object-contain"
                    sizes="(max-width: 768px) 100vw, 896px"
                    priority
                    unoptimized
                  />
                </div>
              </CardContent>
            </Card>
          )}

          {/* Shopping Link */}
          {product.shopping_url && (
            <Card>
              <CardContent className="p-6">
                <Button
                  asChild
                  className="w-full bg-primary hover:bg-primary/90 text-primary-foreground text-lg py-6"
                  size="lg"
                >
                  <a
                    href={product.shopping_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center justify-center gap-3"
                  >
                    <span>Buy on Amazon</span>
                    <ExternalLink className="w-5 h-5" />
                  </a>
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Basic Info Card */}
          <Card>
            <CardHeader>
              <CardTitle>Product Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Price</p>
                  <p className="text-2xl font-bold">
                    {product.price ? `$${product.price.toFixed(2)}` : 'N/A'}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Product ID</p>
                  <p className="text-lg">{product.id}</p>
                </div>
              </div>

              <div className="flex gap-2 flex-wrap">
                {product.food_type && <Badge>{product.food_type}</Badge>}
                {product.age_group && <Badge variant="secondary">{product.age_group}</Badge>}
              </div>

              {product.description && (
                <div>
                  <p className="text-sm text-muted-foreground mb-2">Description</p>
                  <p className="text-base">{product.description}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Ingredients Card */}
          <Card>
            <CardHeader>
              <CardTitle>Ingredients</CardTitle>
              <CardDescription>
                {product.ingredients.length > 0
                  ? `This product contains ${product.ingredients.length} ingredient(s)`
                  : 'No ingredients listed'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {product.full_ingredient_list && (
                <div className="mb-4">
                  <p className="text-sm text-muted-foreground mb-2">Full Ingredient List</p>
                  <p className="text-base">{product.full_ingredient_list}</p>
                </div>
              )}

              {product.ingredients.length > 0 && (
                <div className="space-y-4">
                  <p className="text-sm text-muted-foreground">Detailed Ingredients</p>
                  <div className="grid gap-4">
                    {product.ingredients.map((ingredient) => (
                      <Card key={ingredient.id}>
                        <CardHeader className="pb-3">
                          <CardTitle className="text-lg">{ingredient.name}</CardTitle>
                          {ingredient.description && (
                            <CardDescription>{ingredient.description}</CardDescription>
                          )}
                        </CardHeader>
                        <CardContent className="space-y-3">
                          {ingredient.nutritional_value && (
                            <div>
                              <p className="text-sm font-medium mb-2">Nutritional Value</p>
                              <div className="flex flex-wrap gap-2">
                                {Object.entries(ingredient.nutritional_value).map(([key, value]) => (
                                  <Badge key={key} variant="outline">
                                    {key}: {String(value)}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          )}

                          {ingredient.common_allergens && ingredient.common_allergens.length > 0 && (
                            <div>
                              <p className="text-sm font-medium mb-2">Common Allergens</p>
                              <div className="flex flex-wrap gap-2">
                                {ingredient.common_allergens.map((allergen) => (
                                  <Badge key={allergen} variant="destructive">
                                    {allergen}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}



