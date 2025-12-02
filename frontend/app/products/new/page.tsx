'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useCreateProduct, useIngredients } from '@/lib/api-hooks';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

export default function NewProductPage() {
  const router = useRouter();
  const createProduct = useCreateProduct();
  const { data: ingredients } = useIngredients();

  const [formData, setFormData] = useState({
    name: '',
    brand: '',
    price: '',
    age_group: '',
    food_type: '',
    description: '',
    full_ingredient_list: '',
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      await createProduct.mutateAsync({
        name: formData.name,
        brand: formData.brand,
        price: formData.price ? parseFloat(formData.price) : undefined,
        age_group: formData.age_group || undefined,
        food_type: formData.food_type || undefined,
        description: formData.description || undefined,
        full_ingredient_list: formData.full_ingredient_list || undefined,
      });

      // Success - redirect to home
      router.push('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create product');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center gap-4">
            <Link href="/">
              <Button variant="ghost" size="icon">
                <ArrowLeft className="h-5 w-5" />
              </Button>
            </Link>
            <div>
              <h1 className="text-3xl font-bold">Add New Product</h1>
              <p className="text-muted-foreground mt-1">
                Create a new cat food product
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <Card>
            <CardHeader>
              <CardTitle>Product Information</CardTitle>
              <CardDescription>
                Fill in the details for the new cat food product
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Product Name */}
                <div className="space-y-2">
                  <Label htmlFor="name">
                    Product Name <span className="text-destructive">*</span>
                  </Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => handleChange('name', e.target.value)}
                    placeholder="e.g., Premium Chicken & Rice Formula"
                    required
                  />
                </div>

                {/* Brand */}
                <div className="space-y-2">
                  <Label htmlFor="brand">
                    Brand <span className="text-destructive">*</span>
                  </Label>
                  <Input
                    id="brand"
                    value={formData.brand}
                    onChange={(e) => handleChange('brand', e.target.value)}
                    placeholder="e.g., Whisker Delight"
                    required
                  />
                </div>

                {/* Price */}
                <div className="space-y-2">
                  <Label htmlFor="price">Price ($)</Label>
                  <Input
                    id="price"
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.price}
                    onChange={(e) => handleChange('price', e.target.value)}
                    placeholder="e.g., 29.99"
                  />
                </div>

                {/* Food Type */}
                <div className="space-y-2">
                  <Label htmlFor="food-type">Food Type</Label>
                  <Select
                    value={formData.food_type}
                    onValueChange={(value) => handleChange('food_type', value)}
                  >
                    <SelectTrigger id="food-type">
                      <SelectValue placeholder="Select food type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Wet">Wet</SelectItem>
                      <SelectItem value="Dry">Dry</SelectItem>
                      <SelectItem value="Snack">Snack</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Age Group */}
                <div className="space-y-2">
                  <Label htmlFor="age-group">Age Group</Label>
                  <Select
                    value={formData.age_group}
                    onValueChange={(value) => handleChange('age_group', value)}
                  >
                    <SelectTrigger id="age-group">
                      <SelectValue placeholder="Select age group" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Kitten">Kitten</SelectItem>
                      <SelectItem value="Kitten (1-6m)">Kitten (1-6m)</SelectItem>
                      <SelectItem value="Kitten (1-12m)">Kitten (1-12m)</SelectItem>
                      <SelectItem value="Adult">Adult</SelectItem>
                      <SelectItem value="Adult (1-7y)">Adult (1-7y)</SelectItem>
                      <SelectItem value="Senior">Senior</SelectItem>
                      <SelectItem value="Senior (7+y)">Senior (7+y)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Description */}
                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <textarea
                    id="description"
                    className="flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    value={formData.description}
                    onChange={(e) => handleChange('description', e.target.value)}
                    placeholder="Enter product description..."
                  />
                </div>

                {/* Ingredients */}
                <div className="space-y-2">
                  <Label htmlFor="ingredients">Ingredients</Label>
                  <textarea
                    id="ingredients"
                    className="flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    value={formData.full_ingredient_list}
                    onChange={(e) => handleChange('full_ingredient_list', e.target.value)}
                    placeholder="Enter comma-separated ingredients, e.g., Chicken, Brown Rice, Carrots, Taurine"
                  />
                  <p className="text-sm text-muted-foreground">
                    Enter ingredients separated by commas
                  </p>
                </div>

                {/* Error Message */}
                {error && (
                  <div className="p-3 bg-destructive/10 border border-destructive rounded-md">
                    <p className="text-sm text-destructive">{error}</p>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex gap-3 justify-end">
                  <Link href="/">
                    <Button type="button" variant="outline" disabled={isSubmitting}>
                      Cancel
                    </Button>
                  </Link>
                  <Button type="submit" disabled={isSubmitting}>
                    {isSubmitting ? 'Creating...' : 'Create Product'}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}

