# Pi repo TODO

- [ ] Add `displayotron-charset-sweep` utility to map supported LCD characters.
  - Generate a paged on-device character matrix (candidate bytes/chars).
  - Prompt the user to confirm which glyphs are readable/correct.
  - Save confirmed-safe charset to a tracked JSON/text file.
  - Update notification sanitization to use discovered charset map instead of ASCII-only fallback.
