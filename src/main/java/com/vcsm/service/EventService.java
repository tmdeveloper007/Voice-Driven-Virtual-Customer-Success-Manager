package com.vcsm.service;

import com.vcsm.model.Event;
import com.vcsm.repository.EventRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
public class EventService {

    @Autowired
    private EventRepository eventRepository;

    public Event createEvent(Event event) { return eventRepository.save(event); }

    public List<Event> getAllEvents() { return eventRepository.findAll(); }

    public List<Event> getActiveEvents() { return eventRepository.findByActiveTrue(); }

    public List<Event> getUpcomingEvents() {
        return eventRepository.findByEventDateAfterAndActiveTrue(LocalDateTime.now());
    }

    public List<Event> getEventsByCategory(Event.EventCategory category) {
        return eventRepository.findByCategoryAndActiveTrue(category);
    }

    public Optional<Event> getEventById(Long id) { return eventRepository.findById(id); }

    public Event updateEvent(Long id, Event updated) {
        Event event = eventRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Event not found: " + id));
        event.setName(updated.getName());
        event.setDescription(updated.getDescription());
        event.setCategory(updated.getCategory());
        event.setLocation(updated.getLocation());
        event.setEventDate(updated.getEventDate());
        event.setMaxCapacity(updated.getMaxCapacity());
        return eventRepository.save(event);
    }

    public Event registerForEvent(Long id) {
        Event event = eventRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Event not found: " + id));
        // Event inactive
        if (!event.isActive()) {
          throw new RuntimeException("Event is not active");
        }
        // Event already happened
        if (event.getEventDate().isBefore(LocalDateTime.now())) {
            throw new RuntimeException("Registration closed. Event already started.");
        }

        // Capacity validation

        if (event.getRegistrations() >= event.getMaxCapacity()) {
            throw new RuntimeException(
                "Event Full! Maximum capacity of "
                        + event.getMaxCapacity()
                        + " participants reached."
            );
        }
        event.setRegistrations(event.getRegistrations() + 1);
        return eventRepository.save(event);


    }

    public List<Event> recommendEvents(String keyword) {
        try {
            return eventRepository.findByCategoryAndActiveTrue(Event.EventCategory.valueOf(keyword.toUpperCase()));
        } catch (IllegalArgumentException e) {
            return eventRepository.findByActiveTrue();
        }
    }

    public void deleteEvent(Long id) { eventRepository.deleteById(id); }
}