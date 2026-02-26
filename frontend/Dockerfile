FROM node:20-slim

WORKDIR /app

# Accept build-time API URL
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

# Install dependencies
COPY package.json ./
RUN npm install

# Copy source
COPY . .

# Expose port
EXPOSE 3000

# Run dev server
CMD ["npm", "run", "dev"]
