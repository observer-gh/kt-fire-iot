package com.fireiot.controltower.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.listener.KafkaMessageListenerContainer;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

@RestController
public class HealthController {

  @Autowired
  private KafkaTemplate<String, Object> kafkaTemplate;

  @Value("${spring.kafka.bootstrap-servers}")
  private String kafkaBootstrapServers;

  @Value("${spring.kafka.consumer.group-id}")
  private String consumerGroupId;

  @Value("${spring.profiles.active:local}")
  private String activeProfile;

  @Value("${spring.kafka.properties.security.protocol:PLAINTEXT}")
  private String securityProtocol;

  @Value("${spring.kafka.properties.sasl.mechanism:}")
  private String saslMechanism;

  @Value("${spring.kafka.properties.sasl.jaas.config:}")
  private String saslJaasConfig;

  @GetMapping("/healthz")
  public Map<String, Object> health() {
    Map<String, Object> status = new HashMap<>();
    Map<String, Object> details = new HashMap<>();

    try {
      // Test Kafka connectivity
      kafkaTemplate.getProducerFactory().createProducer().close();

      // Build detailed Kafka response
      details.put("kafka_connection", "CONNECTED");
      details.put("kafka_bootstrap_servers", kafkaBootstrapServers);
      details.put("consumer_group_id", consumerGroupId);
      details.put("active_profile", activeProfile);
      details.put("security_protocol", securityProtocol);
      details.put("sasl_mechanism", saslMechanism.isEmpty() ? "NONE" : saslMechanism);
      details.put("sasl_jaas_configured", !saslJaasConfig.isEmpty());
      details.put("sasl_jaas_endpoint", extractEndpointFromJaas(saslJaasConfig));
      details.put("connection_test", "SUCCESS");
      details.put("timestamp", Instant.now().toString());

      status.put("status", "UP");
      status.put("service", "controltower");
      status.put("version", "1.0.0");
      status.put("details", details);

    } catch (Exception e) {
      details.put("kafka_connection", "DISCONNECTED");
      details.put("kafka_bootstrap_servers", kafkaBootstrapServers);
      details.put("consumer_group_id", consumerGroupId);
      details.put("active_profile", activeProfile);
      details.put("security_protocol", securityProtocol);
      details.put("sasl_mechanism", saslMechanism.isEmpty() ? "NONE" : saslMechanism);
      details.put("sasl_jaas_configured", !saslJaasConfig.isEmpty());
      details.put("sasl_jaas_endpoint", extractEndpointFromJaas(saslJaasConfig));
      details.put("connection_test", "FAILED");
      details.put("error", e.getMessage());
      details.put("error_type", e.getClass().getSimpleName());
      details.put("timestamp", Instant.now().toString());

      status.put("status", "DOWN");
      status.put("service", "controltower");
      status.put("version", "1.0.0");
      status.put("details", details);
    }

    return status;
  }

  @GetMapping("/ready")
  public Map<String, Object> readiness() {
    Map<String, Object> status = new HashMap<>();
    Map<String, Object> details = new HashMap<>();

    try {
      // Test Kafka connectivity for readiness
      kafkaTemplate.getProducerFactory().createProducer().close();

      details.put("kafka_ready", true);
      details.put("consumers_configured", true);
      details.put("topics_subscribed",
          new String[] {"dataLake.sensorDataAnomalyDetected", "videoAnalysis.fireDetected"});
      details.put("consumer_group", consumerGroupId);
      details.put("bootstrap_servers", kafkaBootstrapServers);
      details.put("security_protocol", securityProtocol);
      details.put("sasl_mechanism", saslMechanism.isEmpty() ? "NONE" : saslMechanism);
      details.put("sasl_jaas_configured", !saslJaasConfig.isEmpty());
      details.put("timestamp", Instant.now().toString());

      status.put("status", "READY");
      status.put("service", "controltower");
      status.put("details", details);

    } catch (Exception e) {
      details.put("kafka_ready", false);
      details.put("error", e.getMessage());
      details.put("error_type", e.getClass().getSimpleName());
      details.put("bootstrap_servers", kafkaBootstrapServers);
      details.put("security_protocol", securityProtocol);
      details.put("sasl_mechanism", saslMechanism.isEmpty() ? "NONE" : saslMechanism);
      details.put("sasl_jaas_configured", !saslJaasConfig.isEmpty());
      details.put("timestamp", Instant.now().toString());

      status.put("status", "NOT_READY");
      status.put("service", "controltower");
      status.put("details", details);
    }

    return status;
  }

  @GetMapping("/kafka-debug")
  public Map<String, Object> kafkaDebug() {
    Map<String, Object> debug = new HashMap<>();
    Map<String, Object> connection = new HashMap<>();
    Map<String, Object> consumers = new HashMap<>();

    try {
      // Test producer connection
      kafkaTemplate.getProducerFactory().createProducer().close();
      connection.put("producer", "CONNECTED");
    } catch (Exception e) {
      connection.put("producer", "DISCONNECTED");
      connection.put("producer_error", e.getMessage());
    }

    // Kafka configuration details
    debug.put("service", "controltower");
    debug.put("profile", activeProfile);
    debug.put("bootstrap_servers", kafkaBootstrapServers);
    debug.put("consumer_group_id", consumerGroupId);
    debug.put("security_protocol", securityProtocol);
    debug.put("sasl_mechanism", saslMechanism.isEmpty() ? "NONE" : saslMechanism);
    debug.put("sasl_jaas_configured", !saslJaasConfig.isEmpty());
    debug.put("sasl_jaas_endpoint", extractEndpointFromJaas(saslJaasConfig));
    debug.put("connection", connection);

    // Consumer topics
    consumers.put("sensor_anomaly_topic", "dataLake.sensorDataAnomalyDetected");
    consumers.put("video_fire_topic", "videoAnalysis.fireDetected");
    consumers.put("group_id", consumerGroupId);
    debug.put("consumers", consumers);

    debug.put("timestamp", Instant.now().toString());

    return debug;
  }

  @GetMapping("/info")
  public Map<String, Object> info() {
    Map<String, Object> info = new HashMap<>();

    info.put("service", "controltower");
    info.put("version", "1.0.0");
    info.put("description", "Central hub for read-only access to IoT fire monitoring data");
    info.put("active_profile", activeProfile);
    info.put("kafka_bootstrap_servers", kafkaBootstrapServers);
    info.put("consumer_group_id", consumerGroupId);
    info.put("security_protocol", securityProtocol);
    info.put("sasl_mechanism", saslMechanism.isEmpty() ? "NONE" : saslMechanism);
    info.put("sasl_jaas_configured", !saslJaasConfig.isEmpty());
    info.put("sasl_jaas_endpoint", extractEndpointFromJaas(saslJaasConfig));
    info.put("java_version", System.getProperty("java.version"));
    info.put("spring_version", org.springframework.core.SpringVersion.getVersion());
    info.put("startup_time", Instant.now().toString());

    return info;
  }

  /**
   * Extract endpoint from SASL JAAS config for debugging (without exposing credentials)
   */
  private String extractEndpointFromJaas(String jaasConfig) {
    if (jaasConfig == null || jaasConfig.isEmpty()) {
      return "NOT_CONFIGURED";
    }

    try {
      // Extract endpoint from: org.apache.kafka.common.security.plain.PlainLoginModule required
      // username="$ConnectionString"
      // password="Endpoint=sb://fire-iot-eventhub-dev.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=xxx;EntityPath=dataLake.sensorDataAnomalyDetected";
      if (jaasConfig.contains("Endpoint=sb://")) {
        int start = jaasConfig.indexOf("Endpoint=sb://") + 13;
        int end = jaasConfig.indexOf("/;", start);
        if (end > start) {
          return "sb://" + jaasConfig.substring(start, end);
        }
      }
      return "CONFIGURED_BUT_ENDPOINT_NOT_FOUND";
    } catch (Exception e) {
      return "ERROR_EXTRACTING_ENDPOINT";
    }
  }
}
