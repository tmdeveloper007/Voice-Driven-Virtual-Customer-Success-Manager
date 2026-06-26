package com.vcsm.service;

import com.vcsm.model.User;
import com.vcsm.model.VenueReservation;
import com.vcsm.model.VoiceCommand;
import com.vcsm.repository.UserRepository;
import com.vcsm.repository.VoiceCommandRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContext;
import org.springframework.security.core.context.SecurityContextHolder;

import java.time.LocalDateTime;
import java.util.*;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class OmnidimServiceTest {

    @Mock
    private VoiceCommandRepository voiceCommandRepository;

    @Mock
    private ComplaintService complaintService;

    @Mock
    private EventService eventService;

    @Mock
    private VoiceModelRegistryService voiceModelRegistryService;

    @Mock
    private VoiceAnalyticsService voiceAnalyticsService;

    @Mock
    private UserRepository userRepository;

    @Mock
    private SchedulingOptimizer schedulingOptimizer;

    @InjectMocks
    private OmnidimService omnidimService;

    private User testUser;

    @BeforeEach
    void setUp() {
        testUser = new User();
        testUser.setId(1L);
        testUser.setName("Alice");
        testUser.setEmail("alice@example.com");

        lenient().when(userRepository.findById(1L)).thenReturn(Optional.of(testUser));
        lenient().when(userRepository.findByEmail(anyString())).thenReturn(Optional.of(testUser));
        
        Authentication auth = mock(Authentication.class);
        lenient().when(auth.getName()).thenReturn("alice@example.com");
        SecurityContext securityContext = mock(SecurityContext.class);
        lenient().when(securityContext.getAuthentication()).thenReturn(auth);
        SecurityContextHolder.setContext(securityContext);

        lenient().when(voiceModelRegistryService.getActiveModel()).thenReturn(Optional.empty());
    }

    @Test
    void testProcessVoiceCommand_BookVenueSuccess() {
        when(schedulingOptimizer.hasConflict(eq("Clubhouse"), any(), any())).thenReturn(false);
        when(schedulingOptimizer.bookVenue(eq("Clubhouse"), eq(testUser), any(), any()))
                .thenReturn(new VenueReservation("Clubhouse", testUser, LocalDateTime.now(), LocalDateTime.now()));

        Map<String, Object> result = omnidimService.processVoiceCommand("Book the clubhouse tomorrow at 3 PM");

        assertNotNull(result);
        assertEquals("BOOK_VENUE", result.get("intent"));
        String response = (String) result.get("response");
        assertTrue(response.contains("Successfully booked Clubhouse"));
        verify(schedulingOptimizer, times(1)).bookVenue(eq("Clubhouse"), eq(testUser), any(), any());
    }

    @Test
    void testProcessVoiceCommand_BookVenueCollisionAndAlternatives() {
        when(schedulingOptimizer.hasConflict(eq("Gym"), any(), any())).thenReturn(true);
        
        LocalDateTime tomorrow3PM = LocalDateTime.now().plusDays(1).withHour(15).withMinute(0).withSecond(0).withNano(0);
        List<LocalDateTime[]> alternatives = new ArrayList<>();
        alternatives.add(new LocalDateTime[]{tomorrow3PM.minusHours(2), tomorrow3PM.minusHours(1)});
        alternatives.add(new LocalDateTime[]{tomorrow3PM.plusHours(2), tomorrow3PM.plusHours(3)});
        
        when(schedulingOptimizer.findAlternatives(eq("Gym"), any(), any())).thenReturn(alternatives);

        Map<String, Object> result = omnidimService.processVoiceCommand("Book the gym tomorrow at 3 PM");

        assertNotNull(result);
        assertEquals("BOOK_VENUE", result.get("intent"));
        String response = ((String) result.get("response")).toLowerCase();
        assertTrue(response.contains("that slot is taken, but i can book you at"));
        assertTrue(response.contains("1:00 pm"));
        assertTrue(response.contains("5:00 pm"));
    }

    @Test
    void testProcessVoiceCommand_FollowUpSelectFirstOption() {
        when(schedulingOptimizer.hasConflict(eq("Gym"), any(), any())).thenReturn(true);
        LocalDateTime tomorrow3PM = LocalDateTime.now().plusDays(1).withHour(15).withMinute(0).withSecond(0).withNano(0);
        List<LocalDateTime[]> alternatives = new ArrayList<>();
        alternatives.add(new LocalDateTime[]{tomorrow3PM.minusHours(2), tomorrow3PM.minusHours(1)});
        alternatives.add(new LocalDateTime[]{tomorrow3PM.plusHours(2), tomorrow3PM.plusHours(3)});
        when(schedulingOptimizer.findAlternatives(eq("Gym"), any(), any())).thenReturn(alternatives);

        omnidimService.processVoiceCommand("Book the gym tomorrow at 3 PM");

        Map<String, Object> followUpResult = omnidimService.processVoiceCommand("the first one");
        
        assertNotNull(followUpResult);
        assertEquals("BOOK_VENUE_FOLLOWUP", followUpResult.get("intent"));
        String response = (String) followUpResult.get("response");
        assertTrue(response.contains("Successfully booked Gym"));
        verify(schedulingOptimizer, times(1)).bookVenue(eq("Gym"), eq(testUser), any(), any());
    }

    @Test
    void testProcessVoiceCommand_FollowUpCancel() {
        when(schedulingOptimizer.hasConflict(eq("Gym"), any(), any())).thenReturn(true);
        LocalDateTime tomorrow3PM = LocalDateTime.now().plusDays(1).withHour(15).withMinute(0).withSecond(0).withNano(0);
        List<LocalDateTime[]> alternatives = new ArrayList<>();
        alternatives.add(new LocalDateTime[]{tomorrow3PM.minusHours(2), tomorrow3PM.minusHours(1)});
        when(schedulingOptimizer.findAlternatives(eq("Gym"), any(), any())).thenReturn(alternatives);

        omnidimService.processVoiceCommand("Book the gym tomorrow at 3 PM");

        Map<String, Object> followUpResult = omnidimService.processVoiceCommand("no cancel it");
        
        assertNotNull(followUpResult);
        assertEquals("BOOK_VENUE_FOLLOWUP", followUpResult.get("intent"));
        String response = (String) followUpResult.get("response");
        assertTrue(response.contains("Booking operation cancelled"));
    }
}
