# RentalManager


## Nuitka installation

### Setup pyenv
PYTHON_CONFIGURE_OPTS="--enable-framework" pyenv install

### create application
--macos-create-app-bundle: Ceates a macOS application bundle from the standalone executable.
--follow-imports: Follow imports recursively.
--standalone: Create a standalone executable.
--onefile: Create a single file executable.
--recurse-directory: Recurse into a directory.
--output-dir: Output directory for generated files.
--output-filename: Output filename for generated files.
--remove-output: Remove output directory before compilation.
--show-progress: Show progress information.
--show-scons: Show Scons output.
--show-modules: Show modules used.
--show-memory: Show memory usage.
--show-memory-allocations: Show memory allocations.
--show-modules: Show modules used.
--show-progress: Show progress information.
--show-scons: Show Scons output.
--verbose: Verbose output.
--version: Show version information.

poetry run python -m nuitka --follow-imports --standalone --onefile --macos-create-app-bundle rental_manager/rental_manager.py