# ---------- Build stage ----------
    FROM maven:3.9.9-eclipse-temurin-21 AS builder

    WORKDIR /build
    
    # Copy pom.xml first (for dependency caching)
    COPY pom.xml ./
    RUN mvn dependency:go-offline -B
    
    # Copy source and build
    COPY src ./src
    RUN mvn clean package -DskipTests
    
    # ---------- Runtime stage ----------
    FROM eclipse-temurin:21-jdk-jammy
    
    WORKDIR /app
    
    COPY --from=builder /build/target/*.jar app.jar
    
    RUN addgroup --system appuser && adduser --system --ingroup appuser appuser
    USER appuser
    
    EXPOSE 8001
    
    ENV JAVA_OPTS="-Xms512m -Xmx1024m -XX:+UseG1GC -XX:+UseContainerSupport"
    
    ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
    