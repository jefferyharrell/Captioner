# Product Requirements Document (PRD)

## Product: Captioner

---

## Purpose
Captioner is a private, web-based tool for viewing and captioning photographs. It is designed to streamline the process of organizing, reviewing, and annotating large collections of images, with a focus on extensibility, reliability, and developer sanity (or what’s left of it).

---

## Target Users
- Individuals or small teams who need to review and caption large numbers of images.
- Users who value privacy: all data remains local; no cloud dependencies.
- Power users and developers who may want to extend or automate the system.

---

## User Stories
- As a user, I want to see all my images in a grid so I can quickly browse my collection.
- As a user, I want to see captions on my images so I know which ones I’ve already annotated.
- As a user, I want to click an image to view it full-size and edit its caption in place.
- As a user, I want the system to automatically find new images I add to the folder, so I don’t have to do anything special to import them.
- As a user, I want to be able to trigger a manual rescan if I add a lot of new images at once.
- As a user, I want the app to be fast and responsive, even with thousands of images.
- As a user, I want to know if something goes wrong, and for errors to be clear and actionable.
- As a user, I want my data to be safe: no accidental deletions, no silent failures.

---

## Features (MVP)
- **Gallery View:** Grid of photo thumbnails, each with its caption (if present).
- **Detail View:** Click a thumbnail to see the full image and edit its caption.
- **Automatic Image Discovery:** Backend scans the images folder at startup and detects new images added later.
- **Manual Rescan:** Button in the frontend triggers a backend rescan.
- **Caption Storage:** Captions are stored in a local SQLite database.
- **Thumbnail Caching:** Thumbnails are generated and cached in memory (default 100MB, configurable).
- **Error Handling:** All errors are returned in a consistent, machine-parseable JSON format.
- **Authentication:** Simple password-based login (env var controlled).
- **No Upload/Delete UI:** Images are added/removed by manipulating the backend folder directly.
- **Responsive Design:** Usable on desktop and mobile browsers.
- **Basic Accessibility:** Alt text logic: caption > filename > blank.
- **Test Coverage:** All features are covered by automated tests (Pytest, React Testing Library).

---

## Out of Scope (for MVP)
- Image upload or deletion via the UI
- Cloud storage or remote access
- Advanced search, filtering, or sorting
- Automatic captioning (ML)
- Multi-user support

---

## Success Criteria
- User can view all images in the gallery grid.
- User can edit captions and see them update in real time.
- New images added to the folder appear after a rescan or automatic detection.
- System performance is acceptable with at least 5,000 images.
- All errors are returned in the standardized JSON format and are understandable by a human.
- All code is covered by automated tests, and tests pass reliably.

---

## Non-Functional Requirements
- **Performance:** Gallery loads in under 2 seconds for up to 5,000 images.
- **Reliability:** No data loss or corruption during normal use.
- **Extensibility:** Codebase is structured for easy addition of upload, delete, search, or ML features.
- **Security:** Password is not hard-coded; no sensitive data is logged or leaked.
- **Portability:** Works on macOS and Linux with minimal setup.

---

## Risks & Mitigations
- **Large image sets may exceed memory:** Use thumbnail caching with eviction policy.
- **User confusion over lack of upload/delete:** Clearly document the workflow in the README and UI.
- **Password leakage:** Always read from environment at request time; never hard-code.
- **Test rot:** Enforce TDD and CI to catch regressions early.

---

## Future Enhancements (Post-MVP)
- Image upload and delete from UI
- Search and filter capabilities
- Automatic captioning (ML integration)
- Multi-user support and permissions
- Cloud backup/export

---

## Open Questions
- What’s the best way to detect new images in real time (polling vs. inotify)?
- Should we support Windows, or is that a bridge too far?
- How much configurability do users really want (e.g., cache size, DB location)?

---

## Appendix
- See `DETAILED_SPEC.md` for technical requirements and implementation details.
- All requirements are subject to change if you find a better way (and can prove it with tests).
