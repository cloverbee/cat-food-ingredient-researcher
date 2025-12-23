'use client';

import Link from 'next/link';
import Image from 'next/image';
import { ProductRead } from '@/lib/api-types';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface ProductCardProps {
  product: ProductRead;
}

export function ProductCard({ product }: ProductCardProps) {
  return (
    <div className="glass h-full rounded-2xl overflow-hidden transition-all duration-300 hover:scale-[1.02] hover:shadow-xl group relative flex flex-col">
      <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-white/0 pointer-events-none" />
      
      {/* Product Image */}
      {product.image_url && (
        <div className="relative w-full h-48 overflow-hidden bg-muted/20">
          <Image
            src={product.image_url}
            alt={product.name}
            fill
            className="object-cover transition-transform duration-300 group-hover:scale-110"
            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
            unoptimized
            onError={(e) => {
              // Fallback if image fails to load
              e.currentTarget.style.display = 'none';
            }}
          />
        </div>
      )}
      
      <div className="p-6 space-y-4 relative z-10 flex flex-col h-full">
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-1 flex-1">
            <Link href={`/products/${product.id}`}>
              <h3 className="font-bold text-xl leading-tight group-hover:text-primary transition-colors line-clamp-2 cursor-pointer">
                {product.name}
              </h3>
            </Link>
            <p className="text-sm font-medium text-muted-foreground">{product.brand}</p>
          </div>
          {product.price && (
            <Badge variant="secondary" className="shrink-0 text-sm px-3 py-1 bg-white/20 backdrop-blur-md border border-white/20 shadow-sm">
              ${product.price.toFixed(2)}
            </Badge>
          )}
        </div>

          <div className="flex gap-2 flex-wrap">
            {product.food_type && (
              <Badge variant="outline" className="bg-transparent border-primary/20 text-primary/80 hover:bg-primary/5">
                {product.food_type}
              </Badge>
            )}
            {product.age_group && (
              <Badge variant="outline" className="bg-transparent border-primary/20 text-primary/80 hover:bg-primary/5">
                {product.age_group}
              </Badge>
            )}
          </div>

        {product.description && (
          <p className="text-sm text-muted-foreground/80 line-clamp-3 leading-relaxed">
            {product.description}
          </p>
        )}

        <div className="pt-4 mt-auto border-t border-white/10 space-y-3">
          <div className="flex items-center justify-between text-xs text-muted-foreground font-medium">
            <span>{product.ingredients.length > 0 ? `${product.ingredients.length} ingredients listed` : 'No ingredients listed'}</span>
          </div>
          
          {/* Shopping Link Button */}
          {product.shopping_url && (
            <Button
              asChild
              className="w-full bg-primary hover:bg-primary/90 text-primary-foreground"
              onClick={(e) => {
                // Open in new tab
                window.open(product.shopping_url!, '_blank', 'noopener,noreferrer');
                e.preventDefault();
              }}
            >
              <a
                href={product.shopping_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-center gap-2"
              >
                <span>Buy on Amazon</span>
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                  />
                </svg>
              </a>
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
