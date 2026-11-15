package com.enterprise.ai.entity;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import lombok.Builder;
import org.springframework.data.annotation.Id;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.Instant;
import java.util.Map;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Document(collection = "organizations")
public class Organization {
    @Id
    private String id;

    private String name;

    private String code;

    private String domain;

    private String status; // ACTIVE, SUSPENDED, PENDING

    private String subscriptionTier; // STARTER, PROFESSIONAL, ENTERPRISE

    private Map<String, Object> settings;

    @CreatedDate
    private Instant createdAt;

    @LastModifiedDate
    private Instant updatedAt;
}
