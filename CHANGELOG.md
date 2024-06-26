# CHANGELOG for sumologic-python-sdk
This project adheres to [Semantic Versioning](http://semver.org/). The CHANGELOG follows the format listed at [Keep A Changelog](http://keepachangelog.com/)

## [0.1.16]
### Fixed
- Fixed Retry logic and bug related to headers to make it compatible with newer python versions

## [0.1.15]
### Fixed
- Upgraded request dependency for CVE fixes

## [0.1.14]
### Added
- Added monitor apis
- Added retry logic

### Fixed
- fixed Flake 8 errors

## [0.1.13]
### Added
- Added script for tracing hierarchy


## [0.1.12]
### Added
- Added V2 report job apis
- Added get_file api for use with V2 report job

### Fixed
- Fixes for issue #63
- removing endpoint print statement from stderr via PR64 

## [0.1.11]
### Added
- Added content management and lookup apis via PR62

## [0.1.10]
### Added
- Added content sync apis via PR41  


## [0.1.9]
### Added
- Added search job deletion support via PR24
- Added support for metrics queries via PR25
- Added new parameter byReceiptTime to create search job api
- Added new get_available_builds function via PR55

### Changed
- Fixed import issue for py27/py36 users via PR22
- Improved exception messages for delete, post, put via PR31

### Breaking Changes
- Removed content create,delete and get methods.

## [0.1.7] - 2017-01-31
- Merged PR18,20

## [0.1.6] - 2017-01-05
- Fixed cookielib incompatiblity with python3 via PR17

## [0.1.4/0.1.5] - 2016-02-14
### Fixed
- pip install issue cause by ez_setup reference.

## [0.1.3] - 2016-01-26
### Added
- Region-specific end-point from @MelchiSalins.
- Class inheritability from @MelchiSalins.
