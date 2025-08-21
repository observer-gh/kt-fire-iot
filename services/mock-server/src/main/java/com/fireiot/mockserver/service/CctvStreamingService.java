package com.fireiot.mockserver.service;

import org.bytedeco.javacv.FFmpegFrameGrabber;
import org.bytedeco.javacv.Frame;
import org.bytedeco.javacv.Java2DFrameConverter;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.util.Base64;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

@Service
public class CctvStreamingService {

  private final SimpMessagingTemplate messagingTemplate;
  private final ScheduledExecutorService executorService;
  private boolean isStreaming = false;

  @Value("${cctv.folder.path}")
  private String cctvFolderPath;

  public CctvStreamingService(SimpMessagingTemplate messagingTemplate) {
    this.messagingTemplate = messagingTemplate;
    this.executorService = Executors.newScheduledThreadPool(2);
  }

  public void startStreaming(String videoFileName) {
    if (isStreaming) {
      return;
    }

    isStreaming = true;
    // 설정된 CCTV 폴더 경로 사용
    String videoPath = new File(cctvFolderPath, videoFileName).getPath();

    System.out.println("스트리밍 시작 - 비디오 경로: " + videoPath);

    executorService.submit(() -> {
      try (FFmpegFrameGrabber grabber = new FFmpegFrameGrabber(videoPath)) {
        grabber.start();

        Java2DFrameConverter converter = new Java2DFrameConverter();
        Frame frame;
        int frameCount = 0;

        while (isStreaming && (frame = grabber.grab()) != null) {
          if (frame.image != null) {
            BufferedImage bufferedImage = converter.convert(frame);
            if (bufferedImage != null) {
              String base64Image = convertToBase64(bufferedImage);

              CctvFrame cctvFrame = new CctvFrame();
              cctvFrame.setFrameNumber(frameCount++);
              cctvFrame.setImageData(base64Image);
              cctvFrame.setTimestamp(System.currentTimeMillis());
              cctvFrame.setVideoFileName(videoFileName);

              // WebSocket으로 프레임 전송
              messagingTemplate.convertAndSend("/topic/cctv-stream", cctvFrame);

              // 30 FPS로 스트리밍 (약 33ms 간격)
              Thread.sleep(33);
            }
          }
        }

        grabber.stop();
      } catch (Exception e) {
        e.printStackTrace();
      }
    });
  }

  public void stopStreaming() {
    isStreaming = false;
  }

  public boolean isStreaming() {
    return isStreaming;
  }

  private String convertToBase64(BufferedImage image) throws IOException {
    ByteArrayOutputStream baos = new ByteArrayOutputStream();
    ImageIO.write(image, "jpg", baos);
    byte[] imageBytes = baos.toByteArray();
    return Base64.getEncoder().encodeToString(imageBytes);
  }

  public static class CctvFrame {
    private int frameNumber;
    private String imageData;
    private long timestamp;
    private String videoFileName;

    // Getters and Setters
    public int getFrameNumber() {
      return frameNumber;
    }

    public void setFrameNumber(int frameNumber) {
      this.frameNumber = frameNumber;
    }

    public String getImageData() {
      return imageData;
    }

    public void setImageData(String imageData) {
      this.imageData = imageData;
    }

    public long getTimestamp() {
      return timestamp;
    }

    public void setTimestamp(long timestamp) {
      this.timestamp = timestamp;
    }

    public String getVideoFileName() {
      return videoFileName;
    }

    public void setVideoFileName(String videoFileName) {
      this.videoFileName = videoFileName;
    }
  }
}
