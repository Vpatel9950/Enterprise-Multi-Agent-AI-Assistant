package com.enterprise.ai.entity;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import lombok.Builder;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.Instant;
import java.util.Map;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Document(collection = "audit_logs")
public class AuditLog {
    @Id
    private String id;

    private String organizationId;

    private String userId;

    private String userEmail;

    private String userRole;

    private String action; // LOGIN, DOCUMENT_UPLOAD, ACTION_APPROVED, RAG_QUERY

    private String resourceType;

    private String resourceId;

    private String ipAddress;

    private String userAgent;

    private String status; // SUCCESS, FAILURE, BLOCKED

    private Map<String, Object> details;

    private Instant timestamp;
}
