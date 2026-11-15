package com.enterprise.ai.controller;

import com.enterprise.ai.entity.User;
import com.enterprise.ai.repository.UserRepository;
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
@RequestMapping("/api/v1/users")
@RequiredArgsConstructor
@Tag(name = "User Management", description = "Role-based user management and status toggling")
public class UserController {

    private final UserRepository userRepository;

    @GetMapping
    @PreAuthorize("hasAnyRole('ORG_ADMIN', 'SUPER_ADMIN', 'MANAGER')")
    @Operation(summary = "List users for caller's organization")
    public ResponseEntity<List<User>> listUsers(@AuthenticationPrincipal UserPrincipal userPrincipal) {
        return ResponseEntity.ok(userRepository.findByOrganizationId(userPrincipal.getOrganizationId()));
    }

    @PutMapping("/{id}/role")
    @PreAuthorize("hasAnyRole('ORG_ADMIN', 'SUPER_ADMIN')")
    @Operation(summary = "Update user role (SUPER_ADMIN, ORG_ADMIN, MANAGER, EMPLOYEE)")
    public ResponseEntity<User> updateUserRole(@PathVariable String id, @RequestParam String role) {
        User user = userRepository.findById(id).orElseThrow(() -> new RuntimeException("User not found"));
        user.setRole(role);
        return ResponseEntity.ok(userRepository.save(user));
    }

    @PutMapping("/{id}/status")
    @PreAuthorize("hasAnyRole('ORG_ADMIN', 'SUPER_ADMIN')")
    @Operation(summary = "Activate or deactivate user account")
    public ResponseEntity<User> toggleUserStatus(@PathVariable String id, @RequestParam Boolean isActive) {
        User user = userRepository.findById(id).orElseThrow(() -> new RuntimeException("User not found"));
        user.setIsActive(isActive);
        return ResponseEntity.ok(userRepository.save(user));
    }
}
