package com.enterprise.ai.controller;

import com.enterprise.ai.entity.UploadedDocument;
import com.enterprise.ai.repository.UploadedDocumentRepository;
import com.enterprise.ai.security.UserPrincipal;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.time.Instant;
import java.util.Arrays;
import java.util.List;

@RestController
@RequestMapping("/api/v1/documents")
@RequiredArgsConstructor
@Tag(name = "Knowledge Documents", description = "RAG document ingestion, metadata ACL tagging, and clearance filtering")
public class DocumentController {

    private final UploadedDocumentRepository documentRepository;

    @GetMapping
    @Operation(summary = "List documents filtered by organization and user role clearance")
    public ResponseEntity<List<UploadedDocument>> listDocuments(@AuthenticationPrincipal UserPrincipal userPrincipal) {
        String role = userPrincipal.getRole();
        String orgId = userPrincipal.getOrganizationId();

        List<UploadedDocument> docs;
        if ("SUPER_ADMIN".equals(role) || "ORG_ADMIN".equals(role)) {
            docs = documentRepository.findByOrganizationId(orgId);
        } else {
            // Strictly filter by documents where allowedRoles contains caller's role!
            docs = documentRepository.findByOrganizationIdAndAllowedRolesContaining(orgId, role);
        }

        return ResponseEntity.ok(docs);
    }

    @PostMapping("/upload")
    @PreAuthorize("hasAnyRole('MANAGER', 'ORG_ADMIN', 'SUPER_ADMIN')")
    @Operation(summary = "Upload and index business document with ACL classification")
    public ResponseEntity<UploadedDocument> uploadDocument(
            @RequestParam("file") MultipartFile file,
            @RequestParam(value = "classification", defaultValue = "INTERNAL") String classification,
            @RequestParam(value = "allowedRoles", defaultValue = "EMPLOYEE,MANAGER,ORG_ADMIN,SUPER_ADMIN") String allowedRoles,
            @AuthenticationPrincipal UserPrincipal userPrincipal
    ) throws Exception {
        String content = new String(file.getBytes());
        List<String> rolesList = Arrays.stream(allowedRoles.split(","))
                .map(String::trim)
                .toList();

        UploadedDocument doc = UploadedDocument.builder()
                .organizationId(userPrincipal.getOrganizationId())
                .fileName(file.getOriginalFilename())
                .fileType(file.getOriginalFilename() != null && file.getOriginalFilename().contains(".") ?
                        file.getOriginalFilename().substring(file.getOriginalFilename().lastIndexOf('.') + 1) : "txt")
                .fileSize(file.getSize())
                .storagePath("/storage/" + userPrincipal.getOrganizationId() + "/" + file.getOriginalFilename())
                .contentPreview(content.length() > 300 ? content.substring(0, 300) + "..." : content)
                .chunkCount((content.split("\\s+").length / 200) + 1)
                .classification(classification)
                .allowedRoles(rolesList)
                .uploadedBy(userPrincipal.getId())
                .uploadedByName(userPrincipal.getFullName())
                .status("INDEXED")
                .createdAt(Instant.now())
                .updatedAt(Instant.now())
                .build();

        return ResponseEntity.ok(documentRepository.save(doc));
    }
}
