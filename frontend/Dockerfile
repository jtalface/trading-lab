FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

EXPOSE 3847

CMD ["npm", "run", "dev", "--", "-p", "3847"]

