'use client';

import { ProductFilters } from '@/lib/api-types';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { X } from 'lucide-react';

interface FilterPanelProps {
  filters: ProductFilters;
  onFiltersChange: (filters: ProductFilters) => void;
}

export function FilterPanel({ filters, onFiltersChange }: FilterPanelProps) {
  const updateFilter = <K extends keyof ProductFilters>(key: K, value: ProductFilters[K]) => {
    onFiltersChange({ ...filters, [key]: value });
  };

  const clearFilters = () => {
    onFiltersChange({});
  };

  const hasActiveFilters = Object.values(filters).some((value) => value !== null && value !== undefined);

  return (
    <div className="glass rounded-2xl p-6 sticky top-24">
      <div className="flex items-center justify-between mb-6">
        <h3 className="font-semibold text-lg flex items-center gap-2">
          Filters
        </h3>
        {hasActiveFilters && (
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={clearFilters} 
            className="h-8 px-2 text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
          >
            <X className="h-4 w-4 mr-1" />
            Clear
          </Button>
        )}
      </div>
      
      <div className="space-y-6">
        {/* Food Type Filter */}
        <div className="space-y-2">
          <Label htmlFor="food-type" className="text-xs uppercase tracking-wider text-muted-foreground font-semibold">Food Type</Label>
          <Select
            value={filters.food_type || 'all'}
            onValueChange={(value) => updateFilter('food_type', value === 'all' ? null : value as any)}
          >
            <SelectTrigger id="food-type" className="bg-white/5 border-white/10 focus:ring-primary/20 backdrop-blur-sm">
              <SelectValue placeholder="All types" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="Wet">Wet</SelectItem>
              <SelectItem value="Dry">Dry</SelectItem>
              <SelectItem value="Snack">Snack</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Age Group Filter */}
        <div className="space-y-2">
          <Label htmlFor="age-group" className="text-xs uppercase tracking-wider text-muted-foreground font-semibold">Age Group</Label>
          <Select
            value={filters.age_group || 'all'}
            onValueChange={(value) => updateFilter('age_group', value === 'all' ? null : value as any)}
          >
            <SelectTrigger id="age-group" className="bg-white/5 border-white/10 focus:ring-primary/20 backdrop-blur-sm">
              <SelectValue placeholder="All ages" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Ages</SelectItem>
              <SelectItem value="Kitten">Kitten</SelectItem>
              <SelectItem value="Adult">Adult</SelectItem>
              <SelectItem value="Senior">Senior</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Brand Filter */}
        <div className="space-y-2">
          <Label htmlFor="brand" className="text-xs uppercase tracking-wider text-muted-foreground font-semibold">Brand</Label>
          <Input
            id="brand"
            type="text"
            placeholder="Search brands..."
            value={filters.brand || ''}
            onChange={(e) => updateFilter('brand', e.target.value || null)}
            className="bg-white/5 border-white/10 focus-visible:ring-primary/20 backdrop-blur-sm"
          />
        </div>

        {/* Price Range Filters */}
        <div className="space-y-2">
          <Label className="text-xs uppercase tracking-wider text-muted-foreground font-semibold">Price Range</Label>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <Input
                type="number"
                placeholder="Min $"
                min="0"
                step="0.01"
                value={filters.min_price || ''}
                onChange={(e) => updateFilter('min_price', e.target.value ? parseFloat(e.target.value) : null)}
                className="bg-white/5 border-white/10 focus-visible:ring-primary/20 backdrop-blur-sm"
              />
            </div>
            <div>
              <Input
                type="number"
                placeholder="Max $"
                min="0"
                step="0.01"
                value={filters.max_price || ''}
                onChange={(e) => updateFilter('max_price', e.target.value ? parseFloat(e.target.value) : null)}
                className="bg-white/5 border-white/10 focus-visible:ring-primary/20 backdrop-blur-sm"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
