# Starting from your working directory (where ldm_site exists)

# 1. Create the Python scripts folder
mkdir -p ldm_site/python_scripts
cd ldm_site/python_scripts

# 2. Create Python files (copy content from artifacts)
# Create these files and paste the content:
# - pydantic_rdf_converter.py
# - graphdb_setup.py  
# - requirements.txt

# 3. Create the Next.js web interface
cd ..  # Back to ldm_site/
npx create-next-app@latest web_interface --typescript --tailwind --eslint --app --src-dir

# 4. Install additional dependencies
cd web_interface
npm install n3 @types/n3 axios date-fns

# 5. Create the lib directory and files
mkdir -p src/lib

# 6. Create/replace files with content from artifacts:
# - src/lib/sparql-client.ts
# - src/app/layout.tsx
# - src/app/page.tsx
# - src/app/globals.css
# - src/app/class/[id]/page.tsx  (create the folders first)
# - src/app/temporal/page.tsx

# 7. Create the class detail page directory structure
mkdir -p src/app/class/[id]
mkdir -p src/app/temporal

# 8. Start the development server
npm run dev