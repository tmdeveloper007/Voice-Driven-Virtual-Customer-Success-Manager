package com.vcsm.repository;

import com.vcsm.model.VoiceCommand;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface VoiceCommandRepository extends JpaRepository<VoiceCommand, Long> {
    List<VoiceCommand> findByIntent(String intent);
    List<VoiceCommand> findTop10ByOrderByCreatedAtDesc();
    List<VoiceCommand> findByProcessedOrderByCreatedAtDesc(boolean processed);
}
