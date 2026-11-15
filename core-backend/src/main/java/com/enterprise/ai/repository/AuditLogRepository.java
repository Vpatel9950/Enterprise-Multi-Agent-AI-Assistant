package com.enterprise.ai.repository;

import com.enterprise.ai.entity.AuditLog;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface AuditLogRepository extends MongoRepository<AuditLog, String> {
    List<AuditLog> findTop50ByOrganizationIdOrderByTimestampDesc(String organizationId);
    List<AuditLog> findByOrganizationIdAndUserId(String organizationId, String userId);
}
