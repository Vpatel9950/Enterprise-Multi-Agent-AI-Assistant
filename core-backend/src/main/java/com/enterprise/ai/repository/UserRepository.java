package com.enterprise.ai.repository;

import com.enterprise.ai.entity.User;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface UserRepository extends MongoRepository<User, String> {
    Optional<User> findByEmail(String email);
    Optional<User> findByOrganizationIdAndEmail(String organizationId, String email);
    List<User> findByOrganizationId(String organizationId);
    Boolean existsByEmail(String email);
    Long countByOrganizationId(String organizationId);
}
