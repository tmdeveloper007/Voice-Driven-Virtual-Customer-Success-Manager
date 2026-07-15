# TODO - Login/Signup + JWT Security (Residents vs Admins)

## Plan step 1 — Inspect current frontend calls
- [ ] Read `src/main/resources/static/js/app.js` (already inspected) and identify API calls

## Plan step 2 — Implement Spring Security + JWT backend
- [ ] Add dependencies in `pom.xml`
- [ ] Add security/JWT classes under `src/main/java/com/vcsm/security/**`
- [ ] Add `User` entity, `UserRole` enum, and `UserRepository`
- [ ] Add `AuthController` with `/api/auth/signup` and `/api/auth/login`
- [ ] Seed default admin from `application.properties`

## Plan step 3 — Enforce resident ownership of complaints
- [ ] Add `residentUsername` (or residentId) to `Complaint`
- [ ] Update `ComplaintRepository`, `ComplaintService`, `ComplaintController`
- [ ] Ensure:
  - [ ] Residents can file complaints (their own)
  - [ ] Residents can list/view only their own complaints
  - [ ] Residents cannot update status or delete
  - [ ] Admins can view/update/delete all

## Plan step 4 — Enforce admin-only event management + admin-only analytics
- [ ] Update `EventController` authorization
- [ ] Update `AnalyticsController` authorization

## Plan step 5 — JWT integration in frontend
- [ ] Update `static/js/app.js` to attach `Authorization: Bearer <token>`
- [ ] Add login/signup UI pages or integrate in existing templates

## Plan step 6 — App wiring / build
- [ ] Update `application.properties` with JWT secret + admin seed
- [ ] Run build/tests (requires Maven availability)

## Plan step 7 — Manual verification checklist
- [ ] Resident: signup/login; file complaint; list own complaints
- [ ] Resident: attempt update/delete complaint => 403
- [ ] Admin: login; view/update/delete all complaints
- [ ] Resident: view/register events; cannot create/update/delete
- [ ] Resident: GET `/api/analytics` => 403

