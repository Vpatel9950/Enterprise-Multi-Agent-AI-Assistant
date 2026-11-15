package com.enterprise.ai.repository;

import com.enterprise.ai.entity.Organization;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface OrganizationRepository extends MongoRepository<Organization, String> {
    Optional<Organization> findByCode(String code);
    Optional<Organization> findByDomain(String domain);
}
