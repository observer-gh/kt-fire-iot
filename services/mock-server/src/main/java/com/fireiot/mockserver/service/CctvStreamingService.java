package com.fireiot.mockserver.service;

import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Base64;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;

import javax.imageio.ImageIO;

import org.bytedeco.javacv.FFmpegFrameGrabber;
import org.bytedeco.javacv.Frame;
import org.bytedeco.javacv.Java2DFrameConverter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import jakarta.annotation.PostConstruct;

@Service
public class CCTVStreamingService {

  private static final Logger logger = LoggerFactory.getLogger(CCTVStreamingService.class);

  @Value("${cctv.topic.name:/topic/cctv-stream}")
  private String TOPIC_NAME;

  @Value("${cctv.folder.path:./cctv}")
  private String CCTV_FOLDER;

  private static final int FRAME_RATE = 15; // 15 FPS로 제한
  private static final long FRAME_DELAY = 1000 / FRAME_RATE; // 밀리초

  @Autowired(required = false)
  private SimpMessagingTemplate messagingTemplate;

  private final List<String> videoFiles = new ArrayList<>();
  private final AtomicInteger currentVideoIndex = new AtomicInteger(0);
  private final AtomicBoolean isStreaming = new AtomicBoolean(false);
  private final AtomicInteger frameCounter = new AtomicInteger(0);
  private final AtomicInteger totalVideosPlayed = new AtomicInteger(0);

  public CCTVStreamingService() {
    logger.info("🏗️ CctvStreamingService constructor called");
    logger.info("🌍 Environment info - Working directory: {}", System.getProperty("user.dir"));
    logger.info("🌍 Environment info - Java version: {}", System.getProperty("java.version"));
    logger.info("🌍 Environment info - OS: {}", System.getProperty("os.name"));

    // JavaCV 라이브러리 로드 테스트
    try {
      logger.info("🔍 Testing JavaCV library availability...");
      Class.forName("org.bytedeco.javacv.FFmpegFrameGrabber");
      logger.info("✅ JavaCV FFmpegFrameGrabber class found");

      // FFmpeg 바이너리 테스트
      try {
        org.bytedeco.ffmpeg.global.avutil
            .av_log_set_level(org.bytedeco.ffmpeg.global.avutil.AV_LOG_ERROR);
        logger.info("✅ FFmpeg native library loaded successfully");
      } catch (Exception ffmpegEx) {
        logger.error("❌ FFmpeg native library load failed", ffmpegEx);
      }
    } catch (Exception e) {
      logger.error("❌ JavaCV library not available", e);
    }
  }

  @PostConstruct
  public void initializeVideoFiles() {
    logger.info("🚀 CctvStreamingService PostConstruct started");
    logger.info("📁 CCTV_FOLDER value: {}", CCTV_FOLDER);
    logger.info("📡 TOPIC_NAME value: {}", TOPIC_NAME);
    logger.info("🔌 SimpMessagingTemplate available: {}", messagingTemplate != null);

    try {
      // CCTV_FOLDER가 null인 경우 기본값 사용
      String folderPath = CCTV_FOLDER != null ? CCTV_FOLDER : "./cctv";
      Path cctvPath = Paths.get(folderPath);
      logger.info("📍 Resolved CCTV path: {}", cctvPath.toAbsolutePath());

      if (Files.exists(cctvPath)) {
        Files.list(cctvPath).filter(path -> path.toString().toLowerCase().endsWith(".mp4")).sorted() // 파일명
                                                                                                     // 순서대로
                                                                                                     // 정렬
            .forEach(path -> videoFiles.add(path.toString()));

        logger.info("Found {} video files: {}", videoFiles.size(), videoFiles);

        // 비디오 파일이 없으면 경고
        if (videoFiles.isEmpty()) {
          logger.warn("No MP4 files found in CCTV folder: {}", cctvPath.toAbsolutePath());
        }
      } else {
        logger.warn("⚠️ CCTV folder not found: {}", cctvPath.toAbsolutePath());
        logger.info("💡 Creating CCTV folder...");
        try {
          Files.createDirectories(cctvPath);
          logger.info("✅ CCTV folder created: {}", cctvPath.toAbsolutePath());
        } catch (Exception createEx) {
          logger.warn("⚠️ Failed to create CCTV folder, continuing without it: {}",
              createEx.getMessage());
        }
      }

      logger.info("✅ CctvStreamingService PostConstruct completed successfully");
    } catch (Exception e) {
      logger.error("❌ Error initializing video files, but continuing service creation", e);
      // 예외를 던지지 않음으로써 빈 생성을 계속 진행
    }
  }

  @Scheduled(fixedDelay = 1000) // 1초마다 체크
  public void startStreamingIfNotRunning() {
    if (!isStreaming.get() && !videoFiles.isEmpty()) {
      logger.info("Auto-starting CCTV streaming service - no videos currently streaming");
      startStreaming();
    }
  }

  public void startStreaming() {
    if (isStreaming.compareAndSet(false, true)) {
      logger.info("Starting CCTV streaming service with {} videos", videoFiles.size());
      new Thread(this::streamVideos, "CCTV-Streaming-Thread").start();
    } else {
      logger.info("CCTV streaming service is already running");
    }
  }

  public void stopStreaming() {
    if (isStreaming.compareAndSet(true, false)) {
      logger.info("Stopping CCTV streaming service");
    } else {
      logger.info("CCTV streaming service is already stopped");
    }
  }

  /**
   * 메인 스트리밍 루프 - 비디오들을 순차적으로 무한 반복 재생
   */
  private void streamVideos() {
    logger.info("Starting sequential video streaming loop");

    while (isStreaming.get()) {
      try {
        // 현재 비디오 인덱스 가져오기
        int currentIndex = currentVideoIndex.get();
        String currentVideo = videoFiles.get(currentIndex);

        logger.info("🎬 Starting to stream video {} of {}: {} (index: {})", currentIndex + 1,
            videoFiles.size(), currentVideo, currentIndex);

        // 현재 비디오 스트리밍
        boolean videoCompleted = streamVideo(currentVideo);

        if (videoCompleted) {
          // 비디오가 정상적으로 완료된 경우
          logger.info("✅ Completed streaming video: {} (index: {})", currentVideo, currentIndex);

          // 다음 비디오 인덱스 계산 (순환)
          int nextIndex = (currentIndex + 1) % videoFiles.size();
          currentVideoIndex.set(nextIndex);

          // 전체 재생된 비디오 수 증가
          totalVideosPlayed.incrementAndGet();

          logger.info("🔄 Moving to next video: {} (index: {}) - Total videos played: {}",
              videoFiles.get(nextIndex), nextIndex, totalVideosPlayed.get());

          // 다음 비디오로 넘어가기 전에 잠시 대기 (선택사항)
          Thread.sleep(100);
        } else {
          // 비디오 스트리밍이 중단된 경우 (stopStreaming 호출됨)
          logger.info("⏹️ Video streaming interrupted for: {} (index: {})", currentVideo,
              currentIndex);
          break;
        }

      } catch (Exception e) {
        logger.error("❌ Error in video streaming loop", e);

        // 에러 발생 시 다음 비디오로 이동
        int currentIndex = currentVideoIndex.get();
        int nextIndex = (currentIndex + 1) % videoFiles.size();
        currentVideoIndex.set(nextIndex);

        logger.info("🔄 Error recovery: Moving to next video (index: {})", nextIndex);

        // 에러 후 잠시 대기
        try {
          Thread.sleep(1000);
        } catch (InterruptedException ie) {
          Thread.currentThread().interrupt();
          break;
        }
      }
    }

    logger.info("🛑 CCTV streaming loop ended");
  }

  /**
   * 개별 비디오 스트리밍
   * 
   * @param videoPath 스트리밍할 비디오 파일 경로
   * @return 비디오가 완료되었는지 여부 (true: 완료, false: 중단됨)
   */
  private boolean streamVideo(String videoPath) {
    try (FFmpegFrameGrabber grabber = new FFmpegFrameGrabber(videoPath)) {
      grabber.start();

      Java2DFrameConverter converter = new Java2DFrameConverter();
      Frame frame;

      long startTime = System.currentTimeMillis();
      long lastFrameTime = startTime;
      int frameCount = 0;

      logger.info("🎥 Streaming video: {} (duration: {}ms)", videoPath,
          grabber.getLengthInTime() / 1000);

      while (isStreaming.get() && (frame = grabber.grab()) != null) {
        long currentTime = System.currentTimeMillis();

        // 프레임 레이트 제한
        if (currentTime - lastFrameTime >= FRAME_DELAY) {
          if (frame.image != null) {
            BufferedImage bufferedImage = converter.convert(frame);
            if (bufferedImage != null) {
              sendFrame(bufferedImage, videoPath, frameCount);
              lastFrameTime = currentTime;
              frameCount++;
            }
          }
        }

        // 짧은 대기로 CPU 사용량 조절
        Thread.sleep(1);
      }

      converter.close();

      // 스트리밍이 중단되지 않고 비디오가 완료된 경우
      boolean completed = isStreaming.get();
      if (completed) {
        logger.info("🎬 Video completed: {} - Total frames: {}", videoPath, frameCount);
      }

      return completed;

    } catch (Exception e) {
      logger.error("❌ Error streaming video: {}", videoPath, e);
      return false;
    }
  }

  private void sendFrame(BufferedImage image, String videoPath, int localFrameCount) {
    try {
      // 이미지를 Base64로 인코딩
      ByteArrayOutputStream baos = new ByteArrayOutputStream();
      ImageIO.write(image, "JPEG", baos);
      String base64Image = Base64.getEncoder().encodeToString(baos.toByteArray());

      // 프레임 정보 생성
      CCTVFrame frameData = new CCTVFrame();
      frameData.setType("video_frame");
      frameData.setVideoPath(videoPath);
      frameData.setFrameNumber(frameCounter.incrementAndGet());
      frameData.setTimestamp(System.currentTimeMillis());
      frameData.setData(base64Image);
      frameData.setIsLastFrame(false);
      frameData.setVideoIndex(currentVideoIndex.get());
      frameData.setTotalVideos(videoFiles.size());

      // 모든 클라이언트에게 브로드캐스트 (messagingTemplate이 있는 경우에만)
      if (messagingTemplate != null) {
        messagingTemplate.convertAndSend(TOPIC_NAME, frameData);
      } else {
        logger.warn("⚠️ SimpMessagingTemplate is null, cannot send frame data");
      }

    } catch (Exception e) {
      logger.error("Error sending frame", e);
    }
  }

  public boolean isStreaming() {
    return isStreaming.get();
  }

  public int getCurrentVideoIndex() {
    return currentVideoIndex.get();
  }

  public List<String> getVideoFiles() {
    return new ArrayList<>(videoFiles);
  }

  public int getTotalVideosPlayed() {
    return totalVideosPlayed.get();
  }

  public String getCurrentVideoName() {
    if (!videoFiles.isEmpty() && currentVideoIndex.get() < videoFiles.size()) {
      return videoFiles.get(currentVideoIndex.get());
    }
    return "No video";
  }

  // 내부 클래스
  public static class CCTVFrame {
    private String type;
    private String videoPath;
    private int frameNumber;
    private long timestamp;
    private String data;
    private boolean isLastFrame;
    private int videoIndex;
    private int totalVideos;

    // Getters and Setters
    public String getType() {
      return type;
    }

    public void setType(String type) {
      this.type = type;
    }

    public String getVideoPath() {
      return videoPath;
    }

    public void setVideoPath(String videoPath) {
      this.videoPath = videoPath;
    }

    public int getFrameNumber() {
      return frameNumber;
    }

    public void setFrameNumber(int frameNumber) {
      this.frameNumber = frameNumber;
    }

    public long getTimestamp() {
      return timestamp;
    }

    public void setTimestamp(long timestamp) {
      this.timestamp = timestamp;
    }

    public String getData() {
      return data;
    }

    public void setData(String data) {
      this.data = data;
    }

    public boolean isLastFrame() {
      return isLastFrame;
    }

    public void setIsLastFrame(boolean isLastFrame) {
      this.isLastFrame = isLastFrame;
    }

    public int getVideoIndex() {
      return videoIndex;
    }

    public void setVideoIndex(int videoIndex) {
      this.videoIndex = videoIndex;
    }

    public int getTotalVideos() {
      return totalVideos;
    }

    public void setTotalVideos(int totalVideos) {
      this.totalVideos = totalVideos;
    }
  }
}
