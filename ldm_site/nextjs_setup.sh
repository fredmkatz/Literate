# Create Next.js project
npx create-next-app@latest ldm-editor --typescript --tailwind --eslint --app --src-dir

cd ldm-editor

# Install RDF and HTTP client dependencies
npm install n3 @types/n3 axios

# Install additional UI components (optional but nice)
npm install @headlessui/react @heroicons/react lucide-react

# Install date/time handling for temporal queries
npm install date-fns

# Start development server
npm run dev