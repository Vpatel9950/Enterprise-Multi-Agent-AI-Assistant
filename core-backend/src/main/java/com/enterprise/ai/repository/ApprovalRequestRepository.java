package com.enterprise.ai.repository;

import com.enterprise.ai.entity.ApprovalRequest;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ApprovalRequestRepository extends MongoRepository<ApprovalRequest, String> {
    List<ApprovalRequest> findByOrganizationIdOrderByCreatedAtDesc(String organizationId);
    List<ApprovalRequest> findByOrganizationIdAndStatus(String organizationId, String status);
    List<ApprovalRequest> findByOrganizationIdAndRequestedBy(String organizationId, String requestedBy);
    Long countByOrganizationIdAndStatus(String organizationId, String status);
}
