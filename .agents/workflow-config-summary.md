# Workflow Configuration Summary

## What Was Created

I've created a centralized configuration system for GitHub workflows to make path management easier and more maintainable.

### 📁 New Files

1. **`.github/workflows/_config.yml`**
   - Environment variable definitions
   - Single source of truth for all path definitions
   - Can be copied into any workflow
   - Includes dummy job (required by GitHub Actions schema)

3. **`.github/workflows/README-CONFIG.md`**
   - Complete guide on how to use the configuration
   - Examples and best practices
   - Migration instructions

4. **`.github/workflows/test-agents-with-env.yml.example`**
   - Working example of a workflow using environment variables
   - Shows how to replace hardcoded paths
   - Can be used as a template

5. **`.agents/workflow-config-summary.md`** (this file)
   - Summary of changes
   - Quick reference

## Environment Variables Defined

```yaml
env:
  # Core paths
  CORE_DIR: autogrow-core
  SRC_DIR: autogrow-core/src
  TESTS_DIR: autogrow-core/tests
  SCRIPTS_DIR: autogrow-core/scripts
  
  # Key files
  REQUIREMENTS_FILE: autogrow-core/src/requirements.txt
  TESTS_REQUIREMENTS_FILE: autogrow-core/tests/requirements.txt
  
  # Agent paths
  CLAUDE_AGENT_DIR: autogrow-core/src/claude-agent
  GEMINI_AGENT_DIR: autogrow-core/src/gemini-agent
  AGENTS_DIR: autogrow-core/src/agents
  
  # Test paths
  TESTS_UNIT_DIR: autogrow-core/tests/unit
  TESTS_INTEGRATION_DIR: autogrow-core/tests/integration
  TESTS_CACHE: autogrow-core/tests/.pytest_cache
  COVERAGE_DIR: autogrow-core/tests/htmlcov
  COVERAGE_XML: autogrow-core/tests/htmlcov/coverage.xml
  
  # Script paths
  CLAUDE_SCRIPTS: autogrow-core/src/claude-agent/scripts
  GEMINI_SCRIPTS: autogrow-core/src/gemini-agent/scripts
```

## How to Use

### Quick Start

Add this to the top of any workflow file:

```yaml
env:
  CORE_DIR: autogrow-core
  REQUIREMENTS_FILE: autogrow-core/src/requirements.txt
  TESTS_DIR: autogrow-core/tests
  COVERAGE_XML: autogrow-core/tests/htmlcov/coverage.xml
```

Then use variables instead of hardcoded paths:

```yaml
# Before
- run: pip install -r autogrow-core/src/requirements.txt

# After
- run: pip install -r ${{ env.REQUIREMENTS_FILE }}
```

### Benefits

✅ **Single Source of Truth**: All paths defined in one place  
✅ **Easy Updates**: Change path once, applies everywhere  
✅ **Better Readability**: `${{ env.CORE_DIR }}` is clearer than `autogrow-core`  
✅ **Reduced Errors**: No typos in repeated paths  
✅ **Easier Refactoring**: Update structure without touching every workflow  

## Example Comparison

### Before (Hardcoded Paths)
```yaml
- name: Install dependencies
  run: pip install -r autogrow-core/src/requirements.txt

- name: Run tests
  run: |
    cd autogrow-core
    make test-unit

- name: Upload coverage
  uses: actions/upload-artifact@v4
  with:
    path: autogrow-core/tests/htmlcov/coverage.xml
```

### After (With Environment Variables)
```yaml
env:
  CORE_DIR: autogrow-core
  REQUIREMENTS_FILE: autogrow-core/src/requirements.txt
  COVERAGE_XML: autogrow-core/tests/htmlcov/coverage.xml

jobs:
  test:
    steps:
      - name: Install dependencies
        run: pip install -r ${{ env.REQUIREMENTS_FILE }}
      
      - name: Run tests
        run: |
          cd ${{ env.CORE_DIR }}
          make test-unit
      
      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          path: ${{ env.COVERAGE_XML }}
```

## Migration Strategy

### Option 1: Gradual Migration (Recommended)
1. Keep existing workflows as-is (they work fine)
2. Use env vars for new workflows
3. Migrate existing workflows one at a time when updating them

### Option 2: Full Migration
1. Backup all workflow files
2. Add env section to each workflow
3. Replace all hardcoded paths with variables
4. Test thoroughly

## Next Steps

### Immediate
- [x] Create configuration files
- [x] Create documentation
- [x] Create example workflow
- [ ] Test example workflow (optional)

### Future
- [ ] Migrate existing workflows to use env vars (optional)
- [ ] Create composite actions for common setup tasks
- [ ] Add path validation in CI

## Files to Reference

- **Configuration**: `.github/workflows/_config.yml`
- **Documentation**: `.github/workflows/README-CONFIG.md`
- **Example**: `.github/workflows/test-agents-with-env.yml.example`

## Updating Paths

When project structure changes:

1. Update `.github/workflows/_config.yml`
2. Search for old paths: `grep -r "old-path" .github/workflows/`
3. Update workflows that use env vars (automatic)
4. Update workflows with hardcoded paths (manual)

## Notes

- Current workflows still use hardcoded paths and work fine
- This configuration system is for future maintainability
- No immediate action required - use when convenient
- The `_config.yml` file has a dummy job to satisfy GitHub Actions schema

---

**Created:** November 15, 2025  
**Status:** ✅ Complete - Ready to use  
**Impact:** Low (additive only, no breaking changes)
