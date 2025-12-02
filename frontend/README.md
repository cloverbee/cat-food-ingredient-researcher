# Cat Food Ingredient Researcher - Frontend

A modern Next.js frontend for researching and analyzing cat food products and ingredients.

## 🚀 Tech Stack

- **Next.js 16** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS 4** - Modern utility-first CSS
- **shadcn/ui** - Beautiful, accessible UI components
- **TanStack Query** - Powerful data fetching and caching
- **openapi-typescript** - Type-safe API client generation
- **Axios** - HTTP client
- **Lucide React** - Icon library

## 📋 Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

## 🛠️ Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Create a `.env.local` file in the frontend directory:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Generate API Types (Optional)

If the backend is running, you can generate TypeScript types from the OpenAPI schema:

```bash
npm run generate-types
```

This will:
- Fetch the OpenAPI schema from `http://localhost:8000/openapi.json`
- Generate TypeScript types in `lib/api-types.ts`
- Display available API endpoints

**Note:** The types are already pre-generated, so this step is optional unless the API changes.

## 🏃 Running the Application

### Development Mode

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Production Build

```bash
npm run build
npm start
```

## 📁 Project Structure

```
frontend/
├── app/                      # Next.js App Router pages
│   ├── layout.tsx           # Root layout with QueryProvider
│   ├── page.tsx             # Home page with search and products
│   └── globals.css          # Global styles with Tailwind
├── components/
│   ├── providers/           # React providers
│   │   └── query-provider.tsx
│   ├── products/            # Product-related components
│   │   ├── product-card.tsx
│   │   └── filter-panel.tsx
│   ├── search/              # Search components
│   │   └── search-bar.tsx
│   └── ui/                  # shadcn/ui components
│       ├── button.tsx
│       ├── card.tsx
│       ├── input.tsx
│       ├── label.tsx
│       ├── select.tsx
│       ├── badge.tsx
│       └── table.tsx
├── lib/
│   ├── api-types.ts         # TypeScript types for API
│   ├── api-client.ts        # Axios-based API client
│   ├── api-hooks.ts         # React Query hooks
│   └── utils.ts             # Utility functions
├── scripts/
│   └── generate-api-types.sh # Script to generate types from OpenAPI
└── package.json
```

## 🎨 Features

### 🔍 Search
- Natural language search powered by AI
- Example: "Find wet food for kittens"
- Real-time search results

### 📊 Product Browsing
- Grid view of all products
- Filter by:
  - Food Type (Wet, Dry, Snack)
  - Age Group (Kitten, Adult, Senior)
  - Brand
  - Price Range
- Product cards showing:
  - Name and brand
  - Price
  - Food type and age group
  - Description
  - Ingredient count

### 🧪 Ingredients
- View all ingredients
- Nutritional information
- Allergen warnings
- Products using each ingredient

### ⚙️ Admin
- Bulk import products via CSV
- Product management
- Ingredient management

## 🔌 API Integration

The frontend communicates with the FastAPI backend via:

### API Client (`lib/api-client.ts`)
Type-safe Axios-based client with methods for all API endpoints:
- Products CRUD
- Ingredients CRUD
- Search
- CSV Ingestion

### React Query Hooks (`lib/api-hooks.ts`)
Custom hooks for data fetching with automatic caching and refetching:
```typescript
useProducts()        // Fetch all products
useProduct(id)       // Fetch single product
useCreateProduct()   // Create product mutation
useUpdateProduct()   // Update product mutation
useDeleteProduct()   // Delete product mutation
useSearch(query)     // AI-powered search
// ... and more
```

## 🎯 Usage Examples

### Using the Search

```typescript
import { apiClient } from '@/lib/api-client';

const result = await apiClient.search("Find wet food for kittens");
console.log(result.result);
```

### Fetching Products with React Query

```typescript
import { useProducts } from '@/lib/api-hooks';

function ProductList() {
  const { data: products, isLoading, error } = useProducts();
  
  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading products</div>;
  
  return (
    <div>
      {products?.map(product => (
        <div key={product.id}>{product.name}</div>
      ))}
    </div>
  );
}
```

### Creating a Product

```typescript
import { useCreateProduct } from '@/lib/api-hooks';

function CreateProductForm() {
  const createProduct = useCreateProduct();
  
  const handleSubmit = async (data) => {
    await createProduct.mutateAsync({
      name: "New Product",
      brand: "Brand Name",
      price: 29.99,
      food_type: "Wet",
      age_group: "Kitten"
    });
  };
  
  return <form onSubmit={handleSubmit}>...</form>;
}
```

## 🎨 Styling

This project uses **Tailwind CSS 4** with **shadcn/ui** components.

### Adding New Components

```bash
npx shadcn@latest add [component-name]
```

Example:
```bash
npx shadcn@latest add dialog
npx shadcn@latest add dropdown-menu
```

## 🔄 Updating API Types

When the backend API changes:

1. Make sure the backend is running
2. Run the type generation script:
```bash
npm run generate-types
```

3. Or manually check the API with jq:
```bash
curl http://localhost:8000/openapi.json | jq '.paths | keys'
```

## 🐛 Troubleshooting

### Backend Connection Issues

If you see "Error loading products":
1. Verify the backend is running: `http://localhost:8000`
2. Check the API URL in your environment configuration
3. Open browser DevTools to see network errors

### Type Generation Fails

If `npm run generate-types` fails:
1. Ensure the backend is running
2. Check that `http://localhost:8000/openapi.json` is accessible
3. The types in `lib/api-types.ts` are pre-generated and should work without regeneration

## 📝 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint
- `npm run generate-types` - Generate TypeScript types from OpenAPI schema

## 🚀 Next Steps

To extend the frontend:

1. **Add more pages**: Create new pages in the `app/` directory
2. **Add more components**: Use shadcn/ui or create custom components
3. **Enhance search**: Add filters, autocomplete, or search history
4. **Add authentication**: Integrate user authentication and protected routes
5. **Add charts**: Visualize ingredient data and product statistics

## 📚 Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [shadcn/ui](https://ui.shadcn.com/)
- [TanStack Query](https://tanstack.com/query/latest)
- [openapi-typescript](https://openapi-ts.dev/)
