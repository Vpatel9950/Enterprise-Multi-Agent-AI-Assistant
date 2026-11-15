package com.enterprise.ai.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserDto {
    private String id;
    private String organizationId;
    private String departmentId;
    private String email;
    private String fullName;
    private String role;
    private String department;
    private Boolean isActive;
}
