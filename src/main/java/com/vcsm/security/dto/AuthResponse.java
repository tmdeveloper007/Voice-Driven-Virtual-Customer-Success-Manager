package com.vcsm.security.dto;

public class AuthResponse {
    private final String token;
    private final String tokenType = "Bearer";

    public AuthResponse(String token) {
        this.token = token;
    }

    public String getToken() {
        return token;
    }

    public String getTokenType() {
        return tokenType;
    }
}

