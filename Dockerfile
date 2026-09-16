# ---- Frontend build ----
FROM node:22-alpine AS frontend-build
WORKDIR /web
COPY frontend/package.json frontend/tsconfig.json frontend/tsconfig.node.json frontend/vite.config.ts ./
COPY frontend/src ./src
COPY frontend/index.html ./index.html
COPY frontend/public ./public
RUN npm install && npm run build

# ---- API runtime ----
FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8080
WORKDIR /srv
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend ./backend
COPY data ./data
COPY start.sh ./start.sh
RUN chmod +x ./start.sh
COPY --from=frontend-build /web/dist ./frontend/dist
EXPOSE 8080
CMD ["./start.sh"]
