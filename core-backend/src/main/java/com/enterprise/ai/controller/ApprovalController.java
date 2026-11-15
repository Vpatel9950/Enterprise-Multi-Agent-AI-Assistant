package com.enterprise.ai.controller;

import com.enterprise.ai.entity.ApprovalRequest;
import com.enterprise.ai.repository.ApprovalRequestRepository;
import com.enterprise.ai.security.UserPrincipal;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/approvals")
@RequiredArgsConstructor
@Tag(name = "Human-in-the-Loop Approvals", description = "Manager review gates for sensitive agent operations")
public class ApprovalController {

    private final ApprovalRequestRepository approvalRepository;

    @GetMapping
    @Operation(summary = "List approval requests for the caller's organization")
    public ResponseEntity<List<ApprovalRequest>> listApprovals(@AuthenticationPrincipal UserPrincipal userPrincipal) {
        String orgId = userPrincipal.getOrganizationId();
        List<ApprovalRequest> requests;

        if ("EMPLOYEE".equals(userPrincipal.getRole())) {
            requests = approvalRepository.findByOrganizationIdAndRequestedBy(orgId, userPrincipal.getId());
        } else {
            requests = approvalRepository.findByOrganizationIdOrderByCreatedAtDesc(orgId);
        }

        return ResponseEntity.ok(requests);
    }

    @PostMapping("/{id}/review")
    @PreAuthorize("hasAnyRole('MANAGER', 'ORG_ADMIN', 'SUPER_ADMIN')")
    @Operation(summary = "Approve or reject a pending automated action")
    public ResponseEntity<ApprovalRequest> reviewApproval(
            @PathVariable String id,
            @RequestBody Map<String, String> body,
            @AuthenticationPrincipal UserPrincipal userPrincipal
    ) {
        ApprovalRequest req = approvalRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Approval request not found"));

        String decision = body.getOrDefault("decision", "APPROVED");
        String notes = body.getOrDefault("notes", "Reviewed by " + userPrincipal.getFullName());

        req.setStatus(decision);
        req.setReviewedBy(userPrincipal.getId());
        req.setReviewedByName(userPrincipal.getFullName());
        req.setReviewNotes(notes);
        req.setReviewedAt(Instant.now());

        return ResponseEntity.ok(approvalRepository.save(req));
    }
}
