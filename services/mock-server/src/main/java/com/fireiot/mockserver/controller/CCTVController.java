package com.fireiot.mockserver.controller;

import com.fireiot.mockserver.service.CctvStreamingService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import jakarta.annotation.PostConstruct;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/cctv")
@CrossOrigin(origins = "*")
public class CCTVController {

  private static final Logger logger = LoggerFactory.getLogger(CCTVController.class);

  @Autowired
  private CctvStreamingService cctvStreamingService;
  @Value("${cctv.folder.path}")
  private String CCTV_FOLDER;

  @PostConstruct
  public void init() {
    logger.info("🎮 CCTVController initialized successfully");
    logger.info("📂 CCTV_FOLDER: {}", CCTV_FOLDER);
    logger.info("🔗 CctvStreamingService injected: {}",
        cctvStreamingService != null ? "SUCCESS" : "FAILED");
  }

  @PostMapping("/start")
  public ResponseEntity<Map<String, Object>> startStreaming() {
    try {
      cctvStreamingService.startStreaming();

      Map<String, Object> response = new HashMap<>();
      response.put("success", true);
      response.put("message", "CCTV streaming started");
      response.put("timestamp", System.currentTimeMillis());

      return ResponseEntity.ok(response);
    } catch (Exception e) {
      Map<String, Object> response = new HashMap<>();
      response.put("success", false);
      response.put("message", "Failed to start streaming: " + e.getMessage());
      response.put("timestamp", System.currentTimeMillis());

      return ResponseEntity.internalServerError().body(response);
    }
  }

  @PostMapping("/stop")
  public ResponseEntity<Map<String, Object>> stopStreaming() {
    try {
      cctvStreamingService.stopStreaming();

      Map<String, Object> response = new HashMap<>();
      response.put("success", true);
      response.put("message", "CCTV streaming stopped");
      response.put("timestamp", System.currentTimeMillis());

      return ResponseEntity.ok(response);
    } catch (Exception e) {
      Map<String, Object> response = new HashMap<>();
      response.put("success", false);
      response.put("message", "Failed to stop streaming: " + e.getMessage());
      response.put("timestamp", System.currentTimeMillis());

      return ResponseEntity.internalServerError().body(response);
    }
  }

  @GetMapping("/status")
  public ResponseEntity<Map<String, Object>> getStreamingStatus() {
    try {
      Map<String, Object> response = new HashMap<>();
      response.put("success", true);
      response.put("isStreaming", cctvStreamingService.isStreaming());
      response.put("currentVideoIndex", cctvStreamingService.getCurrentVideoIndex());
      response.put("videoFiles", cctvStreamingService.getVideoFiles());
      response.put("timestamp", System.currentTimeMillis());

      return ResponseEntity.ok(response);
    } catch (Exception e) {
      Map<String, Object> response = new HashMap<>();
      response.put("success", false);
      response.put("message", "Failed to get status: " + e.getMessage());
      response.put("timestamp", System.currentTimeMillis());

      return ResponseEntity.internalServerError().body(response);
    }
  }

  @GetMapping("/videos")
  public ResponseEntity<Map<String, Object>> getVideoList() {
    try {
      Map<String, Object> response = new HashMap<>();
      response.put("success", true);
      response.put("videos", cctvStreamingService.getVideoFiles());
      response.put("count", cctvStreamingService.getVideoFiles().size());
      response.put("timestamp", System.currentTimeMillis());

      return ResponseEntity.ok(response);
    } catch (Exception e) {
      Map<String, Object> response = new HashMap<>();
      response.put("success", false);
      response.put("message", "Failed to get video list: " + e.getMessage());
      response.put("timestamp", System.currentTimeMillis());

      return ResponseEntity.internalServerError().body(response);
    }
  }
}

