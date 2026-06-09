package com.vcsm.service;

import com.vcsm.model.Complaint;
import com.vcsm.repository.ComplaintRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.*;
import java.util.logging.Logger;

import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;


@Service
public class ComplaintService {

    private static final Logger log = Logger.getLogger(ComplaintService.class.getName());

    @Autowired
    private ComplaintRepository complaintRepository;

    private boolean isAdmin() {
        var auth = org.springframework.security.core.context.SecurityContextHolder.getContext().getAuthentication();
        if (auth == null || !auth.isAuthenticated()) return false;
        return auth.getAuthorities().stream().anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"));
    }

    private String currentUsername() {
        var auth = SecurityContextHolder.getContext().getAuthentication();
        return auth != null ? auth.getName() : null;
    }

    public Complaint fileComplaint(Complaint complaint) {
        String username = currentUsername();
        if (username == null) throw new RuntimeException("Unauthorized");

        // Force ownership to current user
        complaint.setResidentUsername(username);

        log.info("Filing complaint for user: " + username);
        return complaintRepository.save(complaint);
    }

    public List<Complaint> getAllComplaints() {
        if (isAdmin()) {
            return complaintRepository.findAllOrderByCreatedAtDesc();
        }
        String username = currentUsername();
        return complaintRepository.findByResidentUsernameOrderByCreatedAtDesc(username);
    }

    public Optional<Complaint> getComplaintById(Long id) {
        if (isAdmin()) {
            return complaintRepository.findById(id);
        }
        String username = currentUsername();
        return complaintRepository.findByIdAndResidentUsername(id, username);
    }

    public List<Complaint> getComplaintsByStatus(Complaint.ComplaintStatus status) {
        if (isAdmin()) {
            return complaintRepository.findByStatus(status);
        }
        String username = currentUsername();
        // No repo method for status+resident; filter in memory safely for small datasets
        return getAllComplaints().stream().filter(c -> c.getStatus() == status).toList();
    }

    public Complaint updateStatus(Long id, String status, String resolvedBy, String notes) {
        if (!isAdmin()) {
            throw new org.springframework.security.access.AccessDeniedException("Only admins can update complaint status");
        }

        Complaint complaint = complaintRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Complaint not found: " + id));
        complaint.setStatus(Complaint.ComplaintStatus.valueOf(status.toUpperCase()));
        if (resolvedBy != null && !resolvedBy.isBlank()) complaint.setResolvedBy(resolvedBy);
        if (notes != null && !notes.isBlank()) complaint.setResolutionNotes(notes);
        return complaintRepository.save(complaint);
    }

    public void deleteComplaint(Long id) {
        if (!isAdmin()) {
            throw new org.springframework.security.access.AccessDeniedException("Only admins can delete complaints");
        }
        complaintRepository.deleteById(id);
    }

    public Map<String, Long> getComplaintStats() {
        if (!isAdmin()) {
            throw new org.springframework.security.access.AccessDeniedException("Only admins can access analytics");
        }

        Map<String, Long> stats = new LinkedHashMap<>();
        stats.put("total", complaintRepository.count());
        stats.put("open", complaintRepository.countByStatus(Complaint.ComplaintStatus.OPEN));
        stats.put("inProgress", complaintRepository.countByStatus(Complaint.ComplaintStatus.IN_PROGRESS));
        stats.put("resolved", complaintRepository.countByStatus(Complaint.ComplaintStatus.RESOLVED));
        stats.put("closed", complaintRepository.countByStatus(Complaint.ComplaintStatus.CLOSED));
        return stats;
    }

    public Map<String, Long> getComplaintsByCategory() {
        if (!isAdmin()) {
            throw new org.springframework.security.access.AccessDeniedException("Only admins can access analytics");
        }

        Map<String, Long> map = new LinkedHashMap<>();
        for (Object[] row : complaintRepository.countByCategory()) {
            map.put(row[0].toString(), (Long) row[1]);
        }
        return map;
    }
}
