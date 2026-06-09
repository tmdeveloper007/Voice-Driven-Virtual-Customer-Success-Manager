package com.vcsm.controller;

import com.vcsm.model.Complaint;
import com.vcsm.service.ComplaintService;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/complaints")
@CrossOrigin(origins = "*")
public class ComplaintController {


    @Autowired
    private ComplaintService complaintService;

    @PostMapping
    public ResponseEntity<Complaint> file(@Valid @RequestBody Complaint complaint) {
        return ResponseEntity.ok(complaintService.fileComplaint(complaint));
    }

    @GetMapping
    public ResponseEntity<List<Complaint>> getAll() {
        return ResponseEntity.ok(complaintService.getAllComplaints());
    }

    @GetMapping("/{id}")
    public ResponseEntity<Complaint> getById(@PathVariable Long id) {
        return complaintService.getComplaintById(id).map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }


    @GetMapping("/status/{status}")
    public ResponseEntity<List<Complaint>> getByStatus(@PathVariable String status) {
        return ResponseEntity.ok(complaintService.getComplaintsByStatus(
                Complaint.ComplaintStatus.valueOf(status.toUpperCase())));
    }

    @PutMapping("/{id}/status")
    public ResponseEntity<Complaint> updateStatus(
            @PathVariable Long id,
            @RequestParam String status,
            @RequestParam(required = false) String resolvedBy,
            @RequestParam(required = false) String notes) {
        return ResponseEntity.ok(complaintService.updateStatus(id, status, resolvedBy, notes));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        complaintService.deleteComplaint(id);
        return ResponseEntity.noContent().build();
    }

    @GetMapping("/stats")
    public ResponseEntity<Map<String, Long>> stats() {
        return ResponseEntity.ok(complaintService.getComplaintStats());
    }

    @GetMapping("/stats/category")
    public ResponseEntity<Map<String, Long>> statsByCategory() {
        return ResponseEntity.ok(complaintService.getComplaintsByCategory());
    }
}