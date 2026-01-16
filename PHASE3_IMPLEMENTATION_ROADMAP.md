# Phase 3 Implementation Roadmap

**Date Created**: January 16, 2026  
**Target Completion**: 6-7 days  
**Team Size**: 1-2 developers  

---

## Overview

This roadmap outlines the step-by-step implementation of Phase 3 (Command Processing) for the VoicePerio project. It bridges Phase 2 (speech recognition) and Phase 4 (keystroke injection).

---

## Critical Pre-Requisite: Fix Phase 2 Bug

**BLOCKER: Must complete before any Phase 3 work**

### Issue
`speech_engine.py` line 99: 
```python
# WRONG
text = ' '.join([w['conf'] for w in result_dict['result']])

# CORRECT
text = ' '.join([w['result'] for w in result_dict['result']])
```

### Impact
Without this fix, Phase 3 receives garbage input and cannot be tested.

### Timeline
- Duration: 30 minutes
- Files: `src/voiceperio/speech_engine.py`
- Testing: Run existing Phase 2 test suite

---

## Phase 3 Implementation Stages

### Stage 1: Preparation (Day 1)

#### 1.1 Code Review
- [ ] Read PHASE3_DETAILED_ANALYSIS.md thoroughly
- [ ] Review default_commands.json structure
- [ ] Understand Command class design
- [ ] Review Phase 2 output format

**Time**: 2 hours  
**Deliverable**: Deep understanding of requirements

#### 1.2 Setup Test Infrastructure
- [ ] Create `tests/test_command_parser.py`
- [ ] Create test fixtures with command definitions
- [ ] Set up test data (sample inputs/outputs)
- [ ] Configure pytest or unittest

**Time**: 1.5 hours  
**Deliverable**: Test framework ready

#### 1.3 Setup Development Environment
- [ ] Verify all imports work
- [ ] Verify rapidfuzz installed
- [ ] Verify pytest/unittest installed
- [ ] Create development checklist

**Time**: 30 minutes  
**Deliverable**: Dev environment ready to code

---

### Stage 2: Core Implementation (Days 2-3)

#### 2.1 Implement extract_numbers() - FIRST

**Why First**: Simplest, needed by other methods

```python
def extract_numbers(self, text: str) -> List[int]:
    """Convert number words to integers
    
    Examples:
        "three two three" → [3, 2, 3]
        "four" → [4]
        "zero" → [0]
        "oh" → [0]
    """
```

**Steps**:
1. Split text by spaces
2. Look up each word in self.commands_db["numbers"]
3. Collect integers
4. Return list

**Tests**:
- Basic numbers 0-15
- All aliases (zero, oh)
- Single vs multiple
- Empty input
- Invalid words

**Time**: 2 hours (1 coding, 1 testing)  
**Success Criteria**: All unit tests pass

#### 2.2 Implement is_number_sequence() - SECOND

**Why Second**: Depends on extract_numbers, needed by parse

```python
def is_number_sequence(self, text: str) -> bool:
    """Detect if text is a number sequence
    
    Examples:
        "three" → True
        "three two three" → True
        "bleeding" → False
        "next" → False
    """
```

**Steps**:
1. Split text by spaces
2. Check if ALL words are in commands_db["numbers"]
3. Return True if all are numbers, else False

**Tests**:
- Single numbers
- Multiple numbers
- Non-numbers (commands)
- Mixed words
- Empty string

**Time**: 1.5 hours (0.75 coding, 0.75 testing)  
**Success Criteria**: All unit tests pass

#### 2.3 Implement parse() - THIRD

**Why Third**: Main routing, depends on above two

```python
def parse(self, text: str) -> Optional[Command]:
    """Parse recognized speech into Command
    
    Routing Logic:
    1. Check if number sequence
    2. Match against commands database
    3. Handle multi-keyword commands
    4. Return None if no match
    """
```

**Steps**:
1. Input validation (strip, lowercase, None check)
2. Route to is_number_sequence() if applicable
3. Try exact match against all categories
4. Try fuzzy match as fallback
5. Handle special cases (multi-keyword)
6. Return Command or None

**Tests**:
- All 39 commands
- All 20+ aliases
- Fuzzy matching
- Multi-keywords
- Invalid input
- Edge cases

**Time**: 4 hours (2.5 coding, 1.5 testing)  
**Success Criteria**: All unit tests pass

#### 2.4 Helper Methods - FOURTH

Support functions for parse():
```python
def _build_command(self, cmd_def)
def _fuzzy_match_command(self, text, cmd_name, cmd_def)
def _parse_multi_keyword(self, text)
def _validate_input(self, text)
```

**Time**: 1.5 hours  
**Success Criteria**: parse() uses these helpers

---

### Stage 3: Enhancement (Day 4)

#### 3.1 Multi-Keyword Command Support

**Commands Affected**:
- "furcation one/two/three"
- "mobility one/two/three"
- "quadrant one/two/three/four"
- "next tooth"
- "voice perio wake/sleep/stop"
- "upper right", "upper left", etc.

```python
def _parse_multi_keyword(self, text: str) -> Optional[Command]:
    """Handle commands requiring 2+ words
    
    Examples:
        "furcation one" → Command(key="f", class="1")
        "quadrant two" → Command(quadrant=2)
    """
```

**Logic**:
1. Split text into words
2. Identify multi-word patterns
3. Extract parameters
4. Build appropriate Command

**Time**: 2 hours  
**Tests**: All multi-keyword combinations

#### 3.2 Fuzzy Matching Integration

**Current State**: fuzzy_match() exists but not used  
**Enhancement**: Use only as fallback

```python
def _get_fuzzy_match(self, text: str, threshold: int = 80) -> Optional[str]:
    """Find command with fuzzy matching"""
    # 1. Build list of all command names + aliases
    # 2. Try fuzzy_match with threshold
    # 3. Return best match or None
```

**Rules**:
1. Exact match takes priority (100%)
2. Fuzzy match only if no exact match (80%+)
3. Prefer longer matches over shorter

**Time**: 1.5 hours  
**Tests**: Speech recognition error simulation

#### 3.3 Input Validation

```python
def _validate_input(self, text: str) -> bool:
    """Validate input before parsing
    
    Checks:
    - Not None
    - Not empty after strip
    - ASCII only
    - Reasonable length
    """
```

**Time**: 1 hour  
**Tests**: Malformed input handling

#### 3.4 Error Handling & Logging

```python
def parse(self, text: str) -> Optional[Command]:
    try:
        # ... parsing logic
    except Exception as e:
        logger.error(f"Parse error for '{text}': {e}")
        return None
```

**Improvements**:
- Try/except in parse()
- Detailed logging of decisions
- Error statistics tracking
- Performance logging

**Time**: 1.5 hours  
**Tests**: Error recovery

---

### Stage 4: Testing (Day 5)

#### 4.1 Unit Test Expansion

Create `tests/test_command_parser_complete.py`

**Test Coverage**:
- All public methods (100%)
- All error paths
- All command categories
- All aliases and variations
- Edge cases and boundary conditions

**Target**: 90%+ code coverage

**Time**: 2 hours  
**Deliverable**: Passing test suite

#### 4.2 Integration Tests

Create `tests/test_phase3_integration.py`

**Tests**:
- Phase 2 → Phase 3 pipeline
- Command → Phase 4 execution
- End-to-end scenarios
- Performance benchmarks
- Stress testing

**Time**: 1.5 hours  
**Deliverable**: Integration tests passing

#### 4.3 Performance Testing

```python
def test_parsing_performance():
    """Verify parse() completes in < 5ms"""
    commands = [
        "three two three",
        "bleeding",
        "furcation one",
        "quadrant two",
        # ... many more
    ]
    
    for cmd_text in commands:
        start = time.time()
        parser.parse(cmd_text)
        elapsed = time.time() - start
        assert elapsed < 0.005, f"Too slow: {elapsed}s for '{cmd_text}'"
```

**Time**: 1 hour  
**Target**: < 5ms per command

#### 4.4 Regression Testing

Ensure no Phase 2 breakage:
- Test audio capture still works
- Test speech engine output format
- Test with real Vosk recognition

**Time**: 1 hour

---

### Stage 5: Documentation (Day 6)

#### 5.1 Code Documentation

- [ ] Docstrings for all methods
- [ ] Inline comments for complex logic
- [ ] Type hints complete and correct
- [ ] Error codes documented

**Time**: 1.5 hours

#### 5.2 Algorithm Documentation

Create `docs/PHASE3_PARSING_ALGORITHM.md`

- [ ] Parsing algorithm flowchart
- [ ] Decision tree for command matching
- [ ] State diagrams
- [ ] Complexity analysis

**Time**: 1 hour

#### 5.3 Integration Guide

Create `docs/PHASE3_INTEGRATION.md`

- [ ] How Phase 2 feeds Phase 3
- [ ] How Phase 3 feeds Phase 4
- [ ] Data format s
