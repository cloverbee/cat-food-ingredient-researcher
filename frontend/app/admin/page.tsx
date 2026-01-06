'use client';

import { useState } from 'react';
import { useIngestCSV } from '@/lib/api-hooks';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import Link from 'next/link';
import { ArrowLeft, Upload, FileText, CheckCircle, XCircle } from 'lucide-react';

export default function AdminPage() {
  const ingestCSV = useIngestCSV();
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message: string; count?: number } | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile && selectedFile.type === 'text/csv') {
      setFile(selectedFile);
      setResult(null);
    } else {
      alert('Please select a valid CSV file');
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setResult(null);

    try {
      // Read file content
      const fileContent = await file.text();

      // Upload to backend
      const response = await ingestCSV.mutateAsync({
        fileContent,
        filename: file.name,
      });

      setResult({
        success: true,
        message: response.message,
        count: response.products_created,
      });

      // Clear file input
      setFile(null);
    } catch (error: any) {
      setResult({
        success: false,
        message: error.response?.data?.detail || 'Failed to upload CSV file',
      });
    } finally {
      setIsUploading(false);
    }
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
              <h1 className="text-3xl font-bold">Admin Panel</h1>
              <p className="text-muted-foreground mt-1">
                Manage products and bulk operations
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-3xl mx-auto space-y-6">
          {/* CSV Upload Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Upload className="h-5 w-5" />
                Bulk Import Products
              </CardTitle>
              <CardDescription>
                Upload a CSV file to import multiple products at once
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* File Input */}
              <div className="space-y-2">
                <label
                  htmlFor="csv-file"
                  className="block text-sm font-medium cursor-pointer"
                >
                  Select CSV File
                </label>
                <div className="flex items-center gap-3">
                  <input
                    id="csv-file"
                    type="file"
                    accept=".csv"
                    onChange={handleFileChange}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    disabled={isUploading}
                  />
                </div>
                {file && (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <FileText className="h-4 w-4" />
                    <span>{file.name}</span>
                  </div>
                )}
              </div>

              {/* Upload Button */}
              <Button
                onClick={handleUpload}
                disabled={!file || isUploading}
                className="w-full"
              >
                {isUploading ? 'Uploading...' : 'Upload CSV'}
              </Button>

              {/* CSV Format Info */}
              <div className="p-4 bg-muted rounded-lg">
                <p className="text-sm font-medium mb-2">CSV Format Requirements:</p>
                <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
                  <li>Headers: name, brand, price, age_group, food_type, description, ingredients</li>
                  <li>Ingredients should be comma-separated</li>
                  <li>Example: "Chicken, Brown Rice, Carrots"</li>
                </ul>
              </div>

              {/* Result Message */}
              {result && (
                <div
                  className={`p-4 rounded-lg border ${
                    result.success
                      ? 'bg-green-50 border-green-200 text-green-800'
                      : 'bg-red-50 border-red-200 text-red-800'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    {result.success ? (
                      <CheckCircle className="h-5 w-5 shrink-0 mt-0.5" />
                    ) : (
                      <XCircle className="h-5 w-5 shrink-0 mt-0.5" />
                    )}
                    <div>
                      <p className="font-medium">{result.success ? 'Success!' : 'Error'}</p>
                      <p className="text-sm mt-1">{result.message}</p>
                      {result.count && (
                        <p className="text-sm mt-1">
                          {result.count} product(s) imported successfully
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Quick Actions Card */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>Common administrative tasks</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <Link href="/products/new">
                <Button variant="outline" className="w-full justify-start">
                  Add New Product
                </Button>
              </Link>
              <Link href="/products">
                <Button variant="outline" className="w-full justify-start">
                  View All Products
                </Button>
              </Link>
              <Link href="/ingredients">
                <Button variant="outline" className="w-full justify-start">
                  View All Ingredients
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Sample CSV Download */}
          <Card>
            <CardHeader>
              <CardTitle>Sample CSV</CardTitle>
              <CardDescription>Download a sample CSV file to use as a template</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                Create a CSV file with the following structure:
              </p>
              <div className="bg-muted p-4 rounded-lg overflow-x-auto">
                <pre className="text-xs">
{`name,brand,price,age_group,food_type,description,ingredients
"Premium Chicken",Brand A,29.99,Adult,Dry,"High quality food","Chicken, Rice, Carrots"
"Salmon Delight",Brand B,24.99,Kitten,Wet,"Salmon in gravy","Salmon, Fish Oil"`}
                </pre>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}






