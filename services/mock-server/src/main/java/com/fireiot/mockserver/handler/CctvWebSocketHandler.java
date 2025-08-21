package com.fireiot.mockserver.handler;

import com.fireiot.mockserver.service.CctvStreamingService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.SendTo;
import org.springframework.stereotype.Controller;

import java.util.HashMap;
import java.util.Map;

@Controller
public class CctvWebSocketHandler {

  private final CctvStreamingService cctvStreamingService;

  @Autowired
  public CctvWebSocketHandler(CctvStreamingService cctvStreamingService) {
    this.cctvStreamingService = cctvStreamingService;
  }

  @MessageMapping("/cctv/control")
  @SendTo("/topic/cctv-control")
  public Map<String, Object> handleCctvControl(Map<String, String> message) {
    Map<String, Object> response = new HashMap<>();

    String action = message.get("action");
    String videoFileName = message.get("videoFileName");

    try {
      switch (action) {
        case "start":
          cctvStreamingService.startStreaming(videoFileName);
          response.put("status", "success");
          response.put("message", "Streaming started for: " + videoFileName);
          break;

        case "stop":
          cctvStreamingService.stopStreaming();
          response.put("status", "success");
          response.put("message", "Streaming stopped");
          break;

        case "status":
          response.put("status", "success");
          response.put("streaming", cctvStreamingService.isStreaming());
          break;

        default:
          response.put("status", "error");
          response.put("message", "Unknown action: " + action);
      }
    } catch (Exception e) {
      response.put("status", "error");
      response.put("message", "Error: " + e.getMessage());
    }

    return response;
  }
}
