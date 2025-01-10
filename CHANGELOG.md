# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Changed

- Reorganization of where individual files live in the package.
- Minimum Python version is 3.9 (for [`importlib.resources`](https://docs.python.org/3/library/importlib.resources.html#importlib.resources.files))
- `helloworld.py` example moved to `docs/Examples` (though is likely to be moved again later)

- `main` is gone.

### Added

- Package has complete type annotations.
- `Catalog.default()` returns a dict with data from `catalogue.json`
- The `python_enigma.resources` "package" now exists for use with `importlib.resources`
- A mostly empty `docs` directory. But it is a start.

## 1.1.4 2025-01-08

### Changed

- Transitioning project management from [Zachary Adam-MacEwen](https://github.com/ZAdamMac) to [Jeffrey P Goldberg](https://github.com/jpgoldberg).

- The `main` function (which was an incomplete work in progress) is officially deprecated.

### Fixed

- More robust defaults for `Enigma`
- Fixed unwanted input mutation
- A few typos in the README file

### Added

- The very beginnings of a tests.
- The CHANGELOG.

## 1.1.3 2022-09-27

Final version released by original creator, [Zachary Adam-MacEwen](https://github.com/ZAdamMac).
