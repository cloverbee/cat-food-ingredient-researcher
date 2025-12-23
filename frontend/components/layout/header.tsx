'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/10 bg-background/60 backdrop-blur-xl supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
            <span className="text-2xl">🐱</span>
            <span className="font-bold text-lg hidden sm:inline-block">Cat Food Researcher</span>
          </Link>
        </div>
        <nav className="flex items-center gap-2 md:gap-4">
          <Link href="/products">
            <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground">Products</Button>
          </Link>
          <Link href="/ingredients">
            <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground">Ingredients</Button>
          </Link>
          {process.env.NODE_ENV !== 'production' && (
            <Link href="/admin">
              <Button variant="default" size="sm" className="shadow-lg shadow-primary/20">Admin</Button>
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}


