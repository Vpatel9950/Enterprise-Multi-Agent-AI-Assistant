package com.enterprise.ai.entity;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import lombok.Builder;
import org.springframework.data.annotation.Id;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.Instant;
import java.util.Map;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Document(collection = "approval_requests")
public class ApprovalRequest {
    @Id
    private String id;

    private String organizationId;

    private String conversationId;

    private String workflowId;

    private String requestedBy;

    private String requestedByName;

    private String actionType; // e.g. "CREATE_JIRA_ISSUE", "PROVISION_CLOUD_RESOURCE"

    private String targetSystem;

    private Map<String, Object> actionPayload;

    private String riskLevel; // LOW, MEDIUM, HIGH, CRITICAL

    private String status; // PENDING, APPROVED, REJECTED, EXPIRED

    private String reviewedBy;

    private String reviewedByName;

    private String reviewNotes;

    private Instant reviewedAt;

    @CreatedDate
    private Instant createdAt;

    private Instant expiresAt;
}
