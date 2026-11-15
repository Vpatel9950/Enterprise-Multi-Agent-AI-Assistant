package com.enterprise.ai.entity;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import lombok.Builder;
import org.springframework.data.annotation.Id;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.mongodb.core.mapping.Document;
// Note: @CompoundIndex removed to avoid conflicts with existing MongoDB indexes
// (created by scripts/init_mongo.py). auto-index-creation=false in application.yml

import java.time.Instant;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Document(collection = "departments")
public class Department {
    @Id
    private String id;

    private String organizationId;

    private String name;

    private String code;

    private String description;

    private String managerId;

    @CreatedDate
    private Instant createdAt;

    @LastModifiedDate
    private Instant updatedAt;
}
