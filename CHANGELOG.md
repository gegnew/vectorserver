# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.2] - 2025-09-09

### Added

- BaseRepository pattern for improved data access layer
- Repository pattern implementation with base, chunk, document, and library repositories
- Service/repository pattern architecture replacing direct VectorDB usage

### Changed

- Replaced app/db.py VectorDB with service/repository pattern
- Database access now uses repository objects instead of direct database calls
- Improved separation of concerns between data access and business logic

### Dependencies

- Added pynvim to development dependencies

## [0.0.1] - 2025-08-26

### Added

### Fixed

### Changed

### Removed
