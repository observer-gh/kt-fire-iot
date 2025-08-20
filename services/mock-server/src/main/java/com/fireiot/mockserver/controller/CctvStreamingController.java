package com.fireiot.mockserver.controller;

import com.fireiot.mockserver.service.CctvStreamingService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.File;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/cctv")
@CrossOrigin(origins = "*")
public class CctvStreamingController {

  private final CctvStreamingService cctvStreamingService;

  @Value("${cctv.folder.path}")
  private String cctvFolderPath;

  @Autowired
  public CctvStreamingController(CctvStreamingService cctvStreamingService) {
    this.cctvStreamingService = cctvStreamingService;
  }

  @GetMapping("/videos")
  public ResponseEntity<List<String>> getAvailableVideos() {
    // 설정된 CCTV 폴더 경로 사용
    File cctvFolder = new File(cctvFolderPath);

    if (cctvFolder.exists() && cctvFolder.isDirectory()) {
      File[] videoFiles = cctvFolder.listFiles((dir, name) -> name.toLowerCase().endsWith(".mp4")
          || name.toLowerCase().endsWith(".avi") || name.toLowerCase().endsWith(".mov"));

      if (videoFiles != null) {
        List<String> videoNames =
            Arrays.stream(videoFiles).map(File::getName).collect(Collectors.toList());
        System.out.println("발견된 비디오 파일: " + videoNames);
        return ResponseEntity.ok(videoNames);
      }
    }
    return ResponseEntity.ok(List.of());
  }

  @PostMapping("/stream/start")
  public ResponseEntity<String> startStreaming(@RequestParam String videoFileName) {
    try {
      cctvStreamingService.startStreaming(videoFileName);
      return ResponseEntity.ok("Streaming started for: " + videoFileName);
    } catch (Exception e) {
      return ResponseEntity.badRequest().body("Failed to start streaming: " + e.getMessage());
    }
  }

  @PostMapping("/stream/stop")
  public ResponseEntity<String> stopStreaming() {
    try {
      cctvStreamingService.stopStreaming();
      return ResponseEntity.ok("Streaming stopped");
    } catch (Exception e) {
      return ResponseEntity.badRequest().body("Failed to stop streaming: " + e.getMessage());
    }
  }

  @GetMapping("/stream/status")
  public ResponseEntity<StreamStatus> getStreamStatus() {
    StreamStatus status = new StreamStatus();
    status.setStreaming(cctvStreamingService.isStreaming());
    return ResponseEntity.ok(status);
  }

  public static class StreamStatus {
    private boolean streaming;

    public boolean isStreaming() {
      return streaming;
    }

    public void setStreaming(boolean streaming) {
      this.streaming = streaming;
    }
  }
}
