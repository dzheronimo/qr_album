const fs = require('fs');
const path = require('path');

function addDynamicExport(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  
  // Skip if already has dynamic export
  if (content.includes('export const dynamic = \'force-dynamic\';')) {
    return;
  }
  
  // Add dynamic export after 'use client' or at the beginning
  let newContent;
  if (content.includes("'use client';")) {
    newContent = content.replace(
      "'use client';",
      "'use client';\n\nexport const dynamic = 'force-dynamic';"
    );
  } else {
    newContent = "export const dynamic = 'force-dynamic';\n\n" + content;
  }
  
  fs.writeFileSync(filePath, newContent);
  console.log(`Fixed: ${filePath}`);
}

function processDirectory(dir) {
  const files = fs.readdirSync(dir);
  
  for (const file of files) {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat.isDirectory()) {
      processDirectory(filePath);
    } else if (file === 'page.tsx') {
      addDynamicExport(filePath);
    }
  }
}

// Process all page.tsx files
processDirectory('./app');
console.log('Done!');
