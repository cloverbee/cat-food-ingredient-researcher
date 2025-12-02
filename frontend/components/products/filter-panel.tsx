'use client';

import { ProductFilters } from '@/lib/api-types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

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
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Filters</CardTitle>
          {hasActiveFilters && (
            <Button variant="ghost" size="sm" onClick={clearFilters}>
              Clear
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Food Type Filter */}
        <div className="space-y-2">
          <Label htmlFor="food-type">Food Type</Label>
          <Select
            value={filters.food_type || 'all'}
            onValueChange={(value) => updateFilter('food_type', value === 'all' ? null : value as any)}
          >
            <SelectTrigger id="food-type">
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
          <Label htmlFor="age-group">Age Group</Label>
          <Select
            value={filters.age_group || 'all'}
            onValueChange={(value) => updateFilter('age_group', value === 'all' ? null : value as any)}
          >
            <SelectTrigger id="age-group">
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
          <Label htmlFor="brand">Brand</Label>
          <Input
            id="brand"
            type="text"
            placeholder="Filter by brand..."
            value={filters.brand || ''}
            onChange={(e) => updateFilter('brand', e.target.value || null)}
          />
        </div>

        {/* Price Range Filters */}
        <div className="space-y-2">
          <Label htmlFor="min-price">Min Price ($)</Label>
          <Input
            id="min-price"
            type="number"
            placeholder="Min"
            min="0"
            step="0.01"
            value={filters.min_price || ''}
            onChange={(e) => updateFilter('min_price', e.target.value ? parseFloat(e.target.value) : null)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="max-price">Max Price ($)</Label>
          <Input
            id="max-price"
            type="number"
            placeholder="Max"
            min="0"
            step="0.01"
            value={filters.max_price || ''}
            onChange={(e) => updateFilter('max_price', e.target.value ? parseFloat(e.target.value) : null)}
          />
        </div>
      </CardContent>
    </Card>
  );
}

