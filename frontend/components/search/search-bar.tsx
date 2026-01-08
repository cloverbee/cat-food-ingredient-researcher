'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Search } from 'lucide-react';

interface SearchBarProps {
  onSearch: (query: string) => void;
  isLoading?: boolean;
  initialQuery?: string;
}

export function SearchBar({ onSearch, isLoading, initialQuery = '' }: SearchBarProps) {
  const [query, setQuery] = useState(initialQuery);
  const [isFocused, setIsFocused] = useState(false);

  // Update query when initialQuery changes (e.g., when restored from storage)
  useEffect(() => {
    if (initialQuery) {
      setQuery(initialQuery);
    }
  }, [initialQuery]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query);
    }
  };

  return (
    <form 
      onSubmit={handleSubmit} 
      className={`relative max-w-3xl mx-auto transition-all duration-500 ease-out ${isFocused ? 'scale-105' : 'scale-100'}`}
    >
      <div 
        className={`
          relative flex items-center 
          bg-background/60 backdrop-blur-xl 
          rounded-full shadow-2xl 
          border transition-all duration-300
          ${isFocused ? 'ring-4 ring-primary/20 border-primary' : 'border-white/20 hover:border-white/40'}
        `}
      >
        <Search className={`ml-6 h-6 w-6 transition-colors ${isFocused ? 'text-primary' : 'text-muted-foreground'}`} />
        <Input
          type="text"
          placeholder="Search for cat food... (e.g., 'Find wet food for kittens')"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          className="flex-1 border-none shadow-none focus-visible:ring-0 bg-transparent h-16 pl-4 text-lg rounded-full placeholder:text-muted-foreground/60"
          disabled={isLoading}
        />
        <Button 
          type="submit" 
          disabled={isLoading || !query.trim()}
          size="lg"
          className="rounded-full mr-2 h-12 px-8 text-base font-semibold shadow-lg hover:shadow-xl transition-all"
        >
          {isLoading ? (
            <div className="flex items-center gap-2">
              <div className="h-4 w-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
              <span>Searching...</span>
            </div>
          ) : 'Search'}
        </Button>
      </div>
    </form>
  );
}
