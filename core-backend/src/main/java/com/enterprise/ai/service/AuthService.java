package com.enterprise.ai.service;

import com.enterprise.ai.dto.AuthRequest;
import com.enterprise.ai.dto.AuthResponse;
import com.enterprise.ai.dto.UserDto;
import com.enterprise.ai.entity.AuditLog;
import com.enterprise.ai.entity.User;
import com.enterprise.ai.repository.AuditLogRepository;
import com.enterprise.ai.repository.UserRepository;
import com.enterprise.ai.security.JwtTokenProvider;
import com.enterprise.ai.security.UserPrincipal;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final AuthenticationManager authenticationManager;
    private final JwtTokenProvider tokenProvider;
    private final UserRepository userRepository;
    private final AuditLogRepository auditLogRepository;

    public AuthResponse login(AuthRequest request) {
        Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(request.getEmail(), request.getPassword())
        );

        SecurityContextHolder.getContext().setAuthentication(authentication);
        UserPrincipal userPrincipal = (UserPrincipal) authentication.getPrincipal();

        String accessToken = tokenProvider.generateAccessToken(authentication);
        String refreshToken = tokenProvider.generateRefreshToken(userPrincipal);

        // Update last login
        userRepository.findById(userPrincipal.getId()).ifPresent(u -> {
            u.setLastLoginAt(Instant.now());
            userRepository.save(u);
        });

        // Audit Log entry
        AuditLog audit = AuditLog.builder()
                .organizationId(userPrincipal.getOrganizationId())
                .userId(userPrincipal.getId())
                .userEmail(userPrincipal.getEmail())
                .userRole(userPrincipal.getRole())
                .action("USER_LOGIN_SUCCESS")
                .resourceType("AUTH")
                .resourceId(userPrincipal.getId())
                .status("SUCCESS")
                .details(Map.of("authMethod", "JWT_PASSWORD"))
                .timestamp(Instant.now())
                .build();
        auditLogRepository.save(audit);

        UserDto userDto = UserDto.builder()
                .id(userPrincipal.getId())
                .organizationId(userPrincipal.getOrganizationId())
                .email(userPrincipal.getEmail())
                .fullName(userPrincipal.getFullName())
                .role(userPrincipal.getRole())
                .isActive(userPrincipal.getIsActive())
                .build();

        return AuthResponse.builder()
                .accessToken(accessToken)
                .refreshToken(refreshToken)
                .tokenType("Bearer")
                .user(userDto)
                .build();
    }

    public UserDto getCurrentUser(UserPrincipal userPrincipal) {
        User user = userRepository.findById(userPrincipal.getId())
                .orElseThrow(() -> new RuntimeException("User not found"));

        return UserDto.builder()
                .id(user.getId())
                .organizationId(user.getOrganizationId())
                .departmentId(user.getDepartmentId())
                .email(user.getEmail())
                .fullName(user.getFullName())
                .role(user.getRole())
                .department(user.getDepartment())
                .isActive(user.getIsActive())
                .build();
    }
}
