# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [v0.4.0] - 2026-01-08
### Removed
- Dropped support for Python 3.7 and 3.8. Minimum required version is now Python 3.9.

### Changed
- Results are now saved incrementally after each validation-model run completes, rather than
  batching all results and saving at the end
- Documented conda-forge release workflow and added conda-forge badges to README

### Fixed
- Fixed versioneer configuration to ship the generated `_version.py` in source distributions

## [v0.3.3] - 2023-08-03
### Fixed
- Made `registration` module use module logger and not root `logging` logger
#### Development
- Updated flake8 config for new version
- Updated scikit-learn package name

## [v0.3.2] - 2022-09-11
### Fixed
- Replaced `DataFrame.append` with `pandas.concat` to stop raised `FutureWarning`

## [v0.3.1] - 2022-07-07
### Added
- `run` now returns validation results dataframe
### Fixed
- Added `typing_extensions` as a project dependency, where it wasn't specified before.

## [v0.3.0] - 2022-06-07
### Added
- Implemented skipping validation/model if it is deprecated
- Added kotsu exception EntityIsDeprecated, and use instead of ValueError for deprecated entity

### Changed
- Changed entity ID regex to extend to more permissible and expressive IDs
- Replaced kwarg `skip_if_prior_result` with `force_rerun` in `run`
- Stop raising exception when registering entities with duplicate ID and raise warning instead
- Replaced `entry_point=None` in entity spec with `deprecated=True`
- Changed passing `artefacts_store_dir` to passing `validation_artefacts_dir` and
  `model_artefacts_dir` explicitly to validations (when `artefacts_store_dir` is not None for
  `run`).
- Changed `..._directory` to `..._dir` in var names for brevity
- Changed implicit kwarg for validations from `artefacts_directory` to `artefacts_store_directory`
  to match `run` kwarg name

### Fixed
- Add run and registration to kotsu. imports
- Docs Usage section updated with latest interface

## [v0.2.1] - 2021-10-12
### Added
- `artefacts_store_directory` now creates missing directories in path and now doesn't require path
  ending in `/`

### Fixed
- Now properly passing `run_params` to validations

## [v0.2.0] - 2021-10-01
### Added
- Implement skipping validation-model combinations if already have results for that pair.
- Run time check that validation-model combinations don't return results that contain a privileged
  key name.

### Changed
- BREAKING: Decouple results store and artefacts store in `run` interface. Changes `run` arguments.


## [v0.1.0] - 2021-09-09
### Added
- Registry interfaces
- Implement main run and store interfaces
- Typing for core entities
- Implement artefacts directory functionality
- Add proper README

## [v0.0.1-alpha.1] - 2021-07-13
### Added
- Stub module

[Unreleased]: https://github.com/datavaluepeople/kotsu/compare/v0.4.0...HEAD
[v0.4.0]: https://github.com/datavaluepeople/kotsu/compare/v0.3.3...v0.4.0
[v0.3.3]: https://github.com/datavaluepeople/kotsu/compare/v0.3.2...v0.3.3
[v0.3.2]: https://github.com/datavaluepeople/kotsu/compare/v0.3.1...v0.3.2
[v0.3.1]: https://github.com/datavaluepeople/kotsu/compare/v0.3.0...v0.3.1
[v0.3.0]: https://github.com/datavaluepeople/kotsu/compare/v0.2.1...v0.3.0
[v0.2.1]: https://github.com/datavaluepeople/kotsu/compare/v0.2.0...v0.2.1
[v0.2.0]: https://github.com/datavaluepeople/kotsu/compare/v0.1.0...v0.2.0
[v0.1.0]: https://github.com/datavaluepeople/kotsu/compare/v0.0.1-alpha.1...v0.1.0
[v0.0.1-alpha.1]: https://github.com/datavaluepeople/kotsu/releases/tag/v0.0.1-alpha.1
