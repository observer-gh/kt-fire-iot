package com.fireiot.mockserver.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.ApplicationContext;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/diagnostic")
@CrossOrigin(origins = "*")
public class DiagnosticController {

  private static final Logger logger = LoggerFactory.getLogger(DiagnosticController.class);

  @Autowired
  private ApplicationContext applicationContext;

  @GetMapping("/health")
  public ResponseEntity<Map<String, Object>> health() {
    logger.info("🏥 Health check endpoint called");

    Map<String, Object> response = new HashMap<>();
    response.put("status", "OK");
    response.put("timestamp", System.currentTimeMillis());
    response.put("message", "Diagnostic controller is working");

    return ResponseEntity.ok(response);
  }

  @GetMapping("/beans")
  public ResponseEntity<Map<String, Object>> getBeans() {
    logger.info("🔍 Bean diagnostic endpoint called");

    Map<String, Object> response = new HashMap<>();

    try {
      // CCTV 관련 빈들 확인
      boolean cctvServiceExists = applicationContext.containsBean("CCTVStreamingService");
      boolean cctvControllerExists = applicationContext.containsBean("CCTVController");

      response.put("success", true);
      response.put("cctvServiceExists", cctvServiceExists);
      response.put("cctvControllerExists", cctvControllerExists);
      response.put("timestamp", System.currentTimeMillis());

      // 모든 빈 이름 (CCTV 관련만)
      String[] beanNames = applicationContext.getBeanDefinitionNames();
      long cctvBeanCount =
          Arrays.stream(beanNames).filter(name -> name.toLowerCase().contains("cctv")).count();

      response.put("cctvBeanCount", cctvBeanCount);
      response.put("totalBeanCount", beanNames.length);

      logger.info("✅ Bean diagnostic completed - CCTV Service: {}, CCTV Controller: {}",
          cctvServiceExists, cctvControllerExists);

    } catch (Exception e) {
      logger.error("❌ Bean diagnostic failed", e);
      response.put("success", false);
      response.put("error", e.getMessage());
    }

    return ResponseEntity.ok(response);
  }

  @GetMapping("/env")
  public ResponseEntity<Map<String, Object>> getEnvironment() {
    logger.info("🌍 Environment diagnostic endpoint called");

    Map<String, Object> response = new HashMap<>();
    response.put("success", true);
    response.put("userDir", System.getProperty("user.dir"));
    response.put("javaVersion", System.getProperty("java.version"));
    response.put("osName", System.getProperty("os.name"));
    response.put("timestamp", System.currentTimeMillis());

    return ResponseEntity.ok(response);
  }
}
