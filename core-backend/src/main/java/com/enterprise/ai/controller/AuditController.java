package com.enterprise.ai.controller;

import com.enterprise.ai.entity.AuditLog;
import com.enterprise.ai.repository.AuditLogRepository;
import com.enterprise.ai.security.UserPrincipal;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/audit")
@RequiredArgsConstructor
@Tag(name = "Compliance & Audit", description = "Tamper-evident audit trails and telemetry logs")
public class AuditController {

    private final AuditLogRepository auditLogRepository;

    @GetMapping("/logs")
    @PreAuthorize("hasAnyRole('MANAGER', 'ORG_ADMIN', 'SUPER_ADMIN')")
    @Operation(summary = "Query organization compliance audit logs")
    public ResponseEntity<List<AuditLog>> getAuditLogs(@AuthenticationPrincipal UserPrincipal userPrincipal) {
        return ResponseEntity.ok(
                auditLogRepository.findTop50ByOrganizationIdOrderByTimestampDesc(userPrincipal.getOrganizationId())
        );
    }
}
