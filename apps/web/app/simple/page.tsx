export default function SimplePage() {
  return (
    <html>
      <head>
        <title>StoryQR - Simple Test</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body style={{ margin: 0, padding: 0, fontFamily: 'Arial, sans-serif' }}>
        <div style={{ 
          minHeight: '100vh', 
          backgroundColor: '#f9fafb', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center' 
        }}>
          <div style={{ 
            maxWidth: '400px', 
            width: '100%', 
            backgroundColor: 'white', 
            borderRadius: '8px', 
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)', 
            padding: '24px' 
          }}>
            <h1 style={{ 
              fontSize: '24px', 
              fontWeight: 'bold', 
              color: '#111827', 
              marginBottom: '16px' 
            }}>
              StoryQR Test Page
            </h1>
            <p style={{ 
              color: '#6b7280', 
              marginBottom: '16px' 
            }}>
              This is a simple test page to verify the application is working.
            </p>
            <div style={{ marginBottom: '24px' }}>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                marginBottom: '8px' 
              }}>
                <span style={{ fontSize: '14px', color: '#6b7280' }}>Status:</span>
                <span style={{ fontSize: '14px', fontWeight: '500', color: '#059669' }}>Running</span>
              </div>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                marginBottom: '8px' 
              }}>
                <span style={{ fontSize: '14px', color: '#6b7280' }}>Environment:</span>
                <span style={{ fontSize: '14px', fontWeight: '500', color: '#2563eb' }}>Production</span>
              </div>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between' 
              }}>
                <span style={{ fontSize: '14px', color: '#6b7280' }}>Framework:</span>
                <span style={{ fontSize: '14px', fontWeight: '500', color: '#7c3aed' }}>Next.js 14</span>
              </div>
            </div>
            <a 
              href="/test" 
              style={{ 
                width: '100%', 
                backgroundColor: '#2563eb', 
                color: 'white', 
                padding: '8px 16px', 
                borderRadius: '6px', 
                textDecoration: 'none', 
                display: 'block', 
                textAlign: 'center',
                transition: 'background-color 0.2s'
              }}
              onMouseOver={(e) => (e.target as HTMLElement).style.backgroundColor = '#1d4ed8'}
              onMouseOut={(e) => (e.target as HTMLElement).style.backgroundColor = '#2563eb'}
            >
              Go to Test Page
            </a>
          </div>
        </div>
      </body>
    </html>
  );
}


