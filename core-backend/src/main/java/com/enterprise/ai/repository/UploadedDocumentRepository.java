package com.enterprise.ai.repository;

import com.enterprise.ai.entity.UploadedDocument;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface UploadedDocumentRepository extends MongoRepository<UploadedDocument, String> {
    List<UploadedDocument> findByOrganizationId(String organizationId);
    List<UploadedDocument> findByOrganizationIdAndAllowedRolesContaining(String organizationId, String role);
    Long countByOrganizationId(String organizationId);
}
