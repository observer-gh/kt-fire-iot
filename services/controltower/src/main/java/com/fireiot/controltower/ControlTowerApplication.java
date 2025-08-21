package com.fireiot.controltower;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class ControlTowerApplication {

    public static void main(String[] args) {
        try {
            SpringApplication app = new SpringApplication(ControlTowerApplication.class);

            // Set default profile if none specified
            if (System.getProperty("spring.profiles.active") == null
                    && System.getenv("SPRING_PROFILES_ACTIVE") == null) {
                app.setAdditionalProfiles("local");
            }

            app.run(args);
        } catch (Exception e) {
            System.err.println("Failed to start ControlTower application: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}
