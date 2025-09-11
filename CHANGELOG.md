# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-09-11

### Added

- **Vector Indexing System**: Complete vector search infrastructure with IVF and Flat indexing
- **IVF (Inverted File) Index**: Efficient approximate nearest neighbor search using k-means clustering
- **FlatIndex**: Optimized exact nearest neighbor search with stateless design
- **Repository Pattern**: VectorIndexRepository abstraction with FlatIndexRepository and IVFIndexRepository implementations
- **KMeans Implementation**: Custom k-means clustering algorithm extracted from IVF for reusability  
- **Vector Index Routes**: API endpoints for vector-based document search
- **Library Management**: CRUD operations for document libraries
- **Incremental Index Updates**: Add/remove chunks without full rebuilds

### Changed

- **LibraryService Architecture**: Moved to services/ directory with improved vector search integration
- **Chunk Model**: Made embedding field required (no longer optional)
- **FlatIndex Design**: Refactored to stateless utility class for better separation of concerns
- **Test Structure**: Enhanced test coverage for vector indexing components

### Fixed

- **Matrix Shape Issues**: Resolved cosine similarity computation errors in FlatIndex
- **Vector Transposition**: Proper handling of vector matrix dimensions (D×N format)
- **Index State Management**: Clean separation between computation and data storage

### Technical Improvements

- **Stateless Utilities**: FlatIndex and IVF classes focus purely on computation
- **Repository Pattern**: Clean data access layer with persistence planning
- **Service Layer**: Improved separation of concerns in business logic
- **Type Safety**: Enhanced type hints and validation across vector operations

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
