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
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Document(collection = "uploaded_documents")
public class UploadedDocument {
    @Id
    private String id;

    private String organizationId;

    private String departmentId;

    private String fileName;

    private String fileType; // pdf, docx, txt

    private Long fileSize;

    private String storagePath;

    private String contentPreview;

    private Integer chunkCount;

    private String vectorCollection;

    private String classification; // PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED

    private List<String> allowedRoles; // e.g. ["EMPLOYEE", "MANAGER", "ORG_ADMIN", "SUPER_ADMIN"]

    private String uploadedBy;

    private String uploadedByName;

    private String status; // PROCESSING, INDEXED, FAILED

    private String errorMessage;

    @CreatedDate
    private Instant createdAt;

    @LastModifiedDate
    private Instant updatedAt;
}
