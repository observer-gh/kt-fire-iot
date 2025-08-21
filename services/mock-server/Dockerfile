# ---------- Build stage ----------
FROM maven:3.9.9-eclipse-temurin-17 AS builder

WORKDIR /build

# Copy pom.xml first (for dependency caching)
COPY pom.xml ./
RUN mvn dependency:go-offline -B

# Copy source and build
COPY src ./src
RUN mvn clean package -DskipTests

# ---------- Runtime stage ----------
FROM eclipse-temurin:17-jdk-jammy

WORKDIR /app

# Install native libraries required for JavaCV
RUN apt-get update && apt-get install -y \
    libavcodec-extra \
    libavformat-dev \
    libavutil-dev \
    libswscale-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /build/target/*.jar app.jar

# Create user first
RUN addgroup --system appuser && adduser --system --ingroup appuser appuser

# Create and copy CCTV files with proper permissions
RUN mkdir -p ./cctv
COPY cctv/ ./cctv/

# Set proper ownership and permissions
RUN chown -R appuser:appuser /app
RUN chmod -R 755 /app

USER appuser

EXPOSE 8001

ENV JAVA_OPTS="-Xms512m -Xmx1024m -XX:+UseG1GC -XX:+UseContainerSupport"
ENV SPRING_PROFILES_ACTIVE=container

ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -Dspring.profiles.active=container -jar app.jar"]