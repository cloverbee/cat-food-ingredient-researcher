'use client';

import Link from 'next/link';
import { ProductRead } from '@/lib/api-types';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface ProductCardProps {
  product: ProductRead;
}

export function ProductCard({ product }: ProductCardProps) {
  return (
    <Link href={`/products/${product.id}`}>
      <Card className="h-full hover:shadow-lg transition-shadow cursor-pointer">
        <CardHeader>
          <div className="flex items-start justify-between gap-2">
            <CardTitle className="text-lg line-clamp-2">{product.name}</CardTitle>
            {product.price && (
              <Badge variant="secondary" className="shrink-0">
                ${product.price.toFixed(2)}
              </Badge>
            )}
          </div>
          <CardDescription>{product.brand}</CardDescription>
        </CardHeader>

        <CardContent className="space-y-3">
          <div className="flex gap-2 flex-wrap">
            {product.food_type && (
              <Badge variant="outline">{product.food_type}</Badge>
            )}
            {product.age_group && (
              <Badge variant="outline">{product.age_group}</Badge>
            )}
          </div>

          {product.description && (
            <p className="text-sm text-muted-foreground line-clamp-3">
              {product.description}
            </p>
          )}
        </CardContent>

        <CardFooter className="text-xs text-muted-foreground">
          {product.ingredients.length > 0 ? (
            <span>{product.ingredients.length} ingredients</span>
          ) : (
            <span>No ingredients listed</span>
          )}
        </CardFooter>
      </Card>
    </Link>
  );
}

