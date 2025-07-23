# TODO - Links VIS Course Patcher

## Current Status
- ✅ **Core patcher functionality complete** - removes PATCH.OFS/OBJECT.OFS files
- ✅ **Batch processing implemented** - handles single files, multiple files, and directories
- ✅ **All 39 CRS files converted** from 24 different courses
- ✅ **Basic testing completed** - several courses confirmed working

## Known Issues

### Graphics Glitches in Later Courses
- **Problem:** Later/newer courses experience graphic glitches and rendering issues
- **Hypothesis:** COURSE.HDR format differences between early and later releases
- **Evidence:** Earlier courses (original VIS era) work flawlessly, later courses have problems
- **Impact:** Affects course playability and visual quality

## High Priority Tasks

### 1. COURSE.HDR Format Analysis
- [ ] **Reverse engineer COURSE.HDR structure completely**
  - [ ] Document header format for working courses (early releases)
  - [ ] Document header format for problematic courses (later releases)  
  - [ ] Identify specific byte differences and their meanings
  - [ ] Create comprehensive format specification
- [ ] **Implement COURSE.HDR validation and correction**
  - [ ] Add COURSE.HDR analysis to patcher
  - [ ] Implement automatic header format normalization
  - [ ] Add validation warnings for problematic headers

### 2. Comprehensive Testing
- [ ] **Systematic testing of all 39 CRS files**
  - [ ] Create testing checklist for each course
  - [ ] Document specific glitches/issues per course
  - [ ] Categorize courses by compatibility level (perfect/minor issues/major issues)
  - [ ] Create test results matrix
- [ ] **Regression testing framework**
  - [ ] Automate basic file structure validation
  - [ ] Create reference screenshots for visual regression testing

### 3. Enhanced Compatibility
- [ ] **Research VIS-specific requirements**
  - [ ] Document memory constraints of VIS system
  - [ ] Identify VIS-specific file format limitations
  - [ ] Research texture/graphics format compatibility
- [ ] **Implement course-specific patches**
  - [ ] Create course-specific fix database
  - [ ] Implement conditional patching based on course ID
  - [ ] Add support for course-specific COURSE.HDR templates

## Medium Priority Tasks

### 4. Quality Assurance
- [ ] **Automated validation system**
  - [ ] File integrity checks
  - [ ] Header validation
  - [ ] Index consistency verification
- [ ] **Better error reporting**
  - [ ] Course-specific error messages
  - [ ] Detailed compatibility warnings
  - [ ] Suggested fixes for common issues

### 5. Documentation Improvements
- [ ] **Course compatibility database**
  - [ ] List all 24 courses with compatibility status
  - [ ] Document known issues per course
  - [ ] Provide course-specific usage notes
- [ ] **COURSE.HDR technical documentation**
  - [ ] Complete format specification
  - [ ] Byte-by-byte breakdown
  - [ ] Version differences documentation

### 6. Tool Enhancements
- [ ] **Analysis mode**
  - [ ] Add `--analyze` flag to examine course headers without patching
  - [ ] Generate detailed course information reports
  - [ ] Compare courses against known-good templates
- [ ] **Backup and restore functionality**
  - [ ] Automatic backup creation before patching
  - [ ] Restore original files capability

## Low Priority Tasks

### 7. User Experience
- [ ] **GUI version** for non-technical users
- [ ] **Progress indicators** for batch operations
- [ ] **Configuration file support** for advanced users

### 8. Advanced Features
- [ ] **Course metadata extraction**
  - [ ] Course name, designer, difficulty
  - [ ] Hole information and statistics
- [ ] **Custom course support**
  - [ ] Template system for creating VIS-compatible courses
  - [ ] Conversion tools for other Links formats

## Research Questions

### Technical Investigations Needed
1. **What specific graphics data causes glitches in later courses?**
2. **Are there VIS hardware limitations affecting certain course features?**
3. **Do texture formats differ between early and late courses?**
4. **Are there undocumented CRS format versions?**
5. **What role does the COURSE.HDR play in graphics rendering?**

## Course Database Status

### Courses Requiring Investigation
*Need to document which specific courses have issues*

- [ ] **Create detailed course compatibility matrix**
- [ ] **Priority list based on popularity/importance**
- [ ] **Technical difficulty assessment per course**

## Success Metrics

- [ ] **All 39 CRS files working without glitches**
- [ ] **Comprehensive COURSE.HDR documentation**
- [ ] **Automated compatibility checking**
- [ ] **Complete course database with status**

---

## Notes
- Focus on COURSE.HDR analysis as primary blocker
- Earlier courses provide good reference implementation
- Later courses reveal format evolution and compatibility challenges
- VIS hardware constraints may limit some course features regardless of patching
