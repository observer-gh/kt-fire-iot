package com.fireiot.controltower.config;

import com.fireiot.controltower.events.SensorAnomalyDetected;
import com.fireiot.controltower.events.VideoFireDetected;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.common.serialization.StringSerializer;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.config.ConcurrentKafkaListenerContainerFactory;
import org.springframework.kafka.core.*;
import org.springframework.kafka.support.serializer.JsonDeserializer;
import org.springframework.kafka.support.serializer.JsonSerializer;

import java.util.HashMap;
import java.util.Map;

@Configuration
public class KafkaConfig {

  @Value("${spring.kafka.bootstrap-servers}")
  private String bootstrapServers;

  @Bean
  public ConsumerFactory<String, SensorAnomalyDetected> sensorAnomalyConsumerFactory() {
    Map<String, Object> props = new HashMap<>();
    props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
    props.put(ConsumerConfig.GROUP_ID_CONFIG, "controltower-group");
    props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
    props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
    props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, JsonDeserializer.class);
    props.put(JsonDeserializer.TRUSTED_PACKAGES, "*");

    return new DefaultKafkaConsumerFactory<>(props, new StringDeserializer(),
        new JsonDeserializer<>(SensorAnomalyDetected.class));
  }

  @Bean
  public ConsumerFactory<String, VideoFireDetected> videoFireDetectedConsumerFactory() {
    Map<String, Object> props = new HashMap<>();
    props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
    props.put(ConsumerConfig.GROUP_ID_CONFIG, "controltower-group");
    props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
    props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
    props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, JsonDeserializer.class);
    props.put(JsonDeserializer.TRUSTED_PACKAGES, "*");

    return new DefaultKafkaConsumerFactory<>(props, new StringDeserializer(),
        new JsonDeserializer<>(VideoFireDetected.class));
  }

  @Bean
  public ConcurrentKafkaListenerContainerFactory<String, SensorAnomalyDetected> sensorAnomalyKafkaListenerContainerFactory() {
    ConcurrentKafkaListenerContainerFactory<String, SensorAnomalyDetected> factory =
        new ConcurrentKafkaListenerContainerFactory<>();
    factory.setConsumerFactory(sensorAnomalyConsumerFactory());
    return factory;
  }

  @Bean
  public ConcurrentKafkaListenerContainerFactory<String, VideoFireDetected> videoFireDetectedKafkaListenerContainerFactory() {
    ConcurrentKafkaListenerContainerFactory<String, VideoFireDetected> factory =
        new ConcurrentKafkaListenerContainerFactory<>();
    factory.setConsumerFactory(videoFireDetectedConsumerFactory());
    return factory;
  }

  @Bean
  public ProducerFactory<String, Object> producerFactory() {
    Map<String, Object> props = new HashMap<>();
    props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
    props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
    props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, JsonSerializer.class);

    return new DefaultKafkaProducerFactory<>(props);
  }

  @Bean
  public KafkaTemplate<String, Object> kafkaTemplate() {
    return new KafkaTemplate<>(producerFactory());
  }
}
