export default function TestPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          StoryQR Test Page
        </h1>
        <p className="text-gray-600 mb-4">
          This is a simple test page to verify the application is working.
        </p>
        <div className="space-y-2">
          <div className="flex justify-between">
            <span className="text-sm text-gray-500">Status:</span>
            <span className="text-sm font-medium text-green-600">Running</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-gray-500">Environment:</span>
            <span className="text-sm font-medium text-blue-600">Production</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-gray-500">Framework:</span>
            <span className="text-sm font-medium text-purple-600">Next.js 14</span>
          </div>
        </div>
        <div className="mt-6">
          <a 
            href="/" 
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors text-center block"
          >
            Go to Home
          </a>
        </div>
      </div>
    </div>
  );
}


