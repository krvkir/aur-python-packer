## Context

The current implementation uses `print()` for feedback and `subprocess.run()` with varying levels of output capture. This makes it hard to reconstruct the execution flow after a failure. We need to transition to a structured logging approach that persists detailed data while keeping the terminal interface clean.

## Goals / Non-Goals

**Goals:**
- Provide a persistent, detailed audit trail of every run.
- Stream merged stdout/stderr of external commands to the log file in real-time.
- Minimal changes to calling code (Manager, Builder) to adopt the new system.
- Log environment overrides to aid in debugging path-related issues.

**Non-Goals:**
- Log rotation or automatic cleanup of old logs (for now).
- Centralized logging server integration.
- Full environment dump (only overrides).

## Decisions

### 1. Logging Infrastructure
- **Choice**: Use a custom `aur_python_packer/logger.py` module.
- **Rationale**: Centralizes configuration and ensures that all components use the same formatting and handlers.
- **Handlers**:
  - `logging.StreamHandler` (Level: INFO) for terminal output.
  - `logging.FileHandler` (Level: DEBUG) for the persistent log file.
- **Log File Naming**: `logs/run_%Y%m%d_%H%M%S.log`.

### 2. Command Execution Wrapper
- **Choice**: Implement `run_command` in `aur_python_packer/utils.py` using `subprocess.Popen`.
- **Rationale**: `subprocess.run` blocks until completion and doesn't easily allow real-time streaming of merged output to a logger while the process is running. `Popen` with `stdout=subprocess.PIPE, stderr=subprocess.STDOUT` allows us to read line-by-line and log each line immediately.
- **Output Merging**: stdout and stderr will be interleaved into a single stream to preserve the chronological order of events.

### 3. Environment Logging
- **Choice**: Log only the `env` dictionary passed to `run_command`.
- **Rationale**: Full environment dumps are noisy and can leak sensitive information. Logging overrides provides the necessary context for debugging build environments without the bloat.

### 4. Integration Strategy
- **Choice**: Refactor `Manager` to call the logger setup in `__init__` (or `cli.py` before `Manager` creation).
- **Rationale**: `cli.py` is the best place to initialize logging as it has immediate access to the `workdir` and can report the log path before any logic starts.

## Risks / Trade-offs

- **[Risk] Sudo Password Prompt**: If a command wrapped by `run_command` prompts for a password via `sudo`, it might hang if not handled correctly.
  - **Mitigation**: Ensure `sudo` is configured for the user, or use `-S` and pipe if necessary (though usually Arch builders assume NOPASSWD for specific tools or handle it out-of-band). We will continue to rely on the system's `sudo` configuration.
- **[Risk] Log Bloat**: Building many packages can generate large log files.
  - **Mitigation**: Users are expected to manage the `logs/` directory. Since this is a CLI tool, run-based logs are appropriate.
- **[Risk] Performance**: Line-by-line reading of subprocess output adds slight overhead.
  - **Mitigation**: Minimal impact compared to the actual build time of AUR packages.
