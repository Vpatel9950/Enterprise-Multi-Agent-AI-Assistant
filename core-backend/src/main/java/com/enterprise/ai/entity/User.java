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

// Note: @Indexed and @CompoundIndex removed to avoid index conflicts with Python-seeded MongoDB
// auto-index-creation=false in application.yml prevents Spring from attempting to recreate them

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Document(collection = "users")
public class User {
    @Id
    private String id;

    private String organizationId;

    private String departmentId;

    private String email;

    private String passwordHash;

    private String fullName;

    private String role; // SUPER_ADMIN, ORG_ADMIN, MANAGER, EMPLOYEE

    private String department;

    private Boolean isActive;

    private Instant lastLoginAt;

    @CreatedDate
    private Instant createdAt;

    @LastModifiedDate
    private Instant updatedAt;
}
