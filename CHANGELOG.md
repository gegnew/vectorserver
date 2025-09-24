# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-09-24

### Added

- **Comprehensive Metadata Filtering**: Complete metadata filter system with 10 operators (eq, ne, gt, gte, lt, lte, in, contains, starts_with, ends_with)
- **Smart Chunking System**: Advanced chunking with overlap detection and boundary preservation for improved context retention
- **Index Persistence**: Automatic index persistence to disk for faster application restarts and data durability
- **Complete Transaction Management**: Full transactional CRUD operations across all repositories with rollback support
- **Comprehensive Error Handling**: Robust error handling with proper exception chains and validation
- **Production Health Checks**: Enhanced health check endpoint with database connectivity monitoring
- **Metadata Filter Unit Tests**: 21 comprehensive unit tests covering all filter operators and edge cases
- **FastAPI Best Practices**: Standardized response models, enhanced validation, and improved API documentation

### Changed

- **Model Architecture**: Consistent metadata field across all Create/Get models (LibraryCreate, DocumentCreate, ChunkCreate)
- **Base Models**: Introduced BaseEntityModel inheritance pattern with DRY principles for common fields
- **Response Models**: Standardized ErrorResponse, PaginatedResponse, and HealthCheck models
- **API Documentation**: Enhanced OpenAPI schema with realistic examples and comprehensive field descriptions
- **Code Organization**: Refactored complex service methods into focused, single-responsibility functions
- **Service Layer**: Improved separation of concerns with proper repository pattern implementation

### Fixed

- **Pydantic Forward References**: Resolved startup crash with SearchResult model circular imports
- **Test Database Isolation**: Proper test database separation preventing test pollution
- **HTTP Status Codes**: Corrected API response status codes (200 vs 201, 204 for DELETE operations)
- **Model Consistency**: Fixed AttributeError where Create models were missing metadata fields
- **Linting Issues**: Resolved 121+ linting violations achieving zero-error codebase
- **Repository Patterns**: Standardized model patterns removing architectural inconsistencies
- **API Design Issues**: Fixed critical routing and endpoint design problems

### Technical Improvements

- **Code Quality**: Zero linting errors, consistent formatting, enhanced type safety
- **Test Coverage**: Comprehensive metadata filtering tests, improved test reliability
- **Documentation**: Complete production readiness analysis and code review documentation
- **Architecture**: Clean domain-driven design with proper transaction boundaries
- **Performance**: Optimized database operations with proper connection management
- **Maintainability**: Simplified complex code, reduced duplication, improved readability

### Documentation

- **Production Readiness Guide**: Complete analysis of deployment requirements and next steps
- **Code Review Documentation**: Detailed technical improvement analysis and metrics
- **Transaction Management**: Comprehensive documentation of transaction architecture
- **FastAPI Best Practices**: Implementation guide for API design patterns

## [1.0.0] - 2025-09-12

### Added

- **Document Management**: Complete document CRUD operations with add_document route
- **End-to-End Testing**: Comprehensive E2E test suite for API validation
- **Async Architecture**: Full conversion to async/await pattern across all services and repositories
- **Database Operations**: Async database operations with improved performance

### Changed

- **Repository Layer**: All repositories converted to async operations
- **Service Layer**: LibraryService and all services now use async patterns
- **Route Handlers**: All API routes converted to async for better concurrency
- **Database Connection**: Async database connections with proper connection management
- **Development Environment**: Updated dev database and improved reload configuration

### Fixed

- **Repository Updates**: Removed required created_at field from update payloads
- **Main Application**: Set proper reload directories for development
- **Test Suite**: Fixed FlatIndex tests and improved test reliability

### Technical Improvements

- **Performance**: Async operations provide better I/O handling and concurrency
- **Code Quality**: Consistent async/await patterns throughout codebase
- **Documentation**: Updated README with current project state
- **Dependencies**: Cleaned up and updated project dependencies

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
