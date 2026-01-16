"""
Test Suite for Phase 4: Keystroke Injection
Tests enhanced window_utils.py and action_executor.py functionality
Tests keystroke injection, window finding, navigation, and special keys
"""

import unittest
import time
import subprocess
import sys
import os
import pyautogui
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from voiceperio.action_executor import ActionExecutor
from voiceperio.number_sequencer import NumberSequencer
from voiceperio.command_parser import CommandParser
from voiceperio.utils.window_utils import (
    get_foreground_window,
    get_window_info,
    find_window_by_title,
    find_window_by_class,
    get_window_title,
    get_window_class,
    get_window_position_size,
    is_window_visible,
    is_window_focused,
    focus_window,
    list_windows,
    list_windows_by_title,
    print_window_info,
    WindowInfo
)
from voiceperio.utils.logger import setup_logging

# Setup logging
logger = setup_logging(log_level=logging.DEBUG)


class TestWindowUtilsEnhancements(unittest.TestCase):
    """Test enhanced window_utils.py functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Launch Notepad for testing"""
        logger.info("=" * 70)
        logger.info("PHASE 4: WINDOW UTILS ENHANCEMENTS")
        logger.info("=" * 70)
        logger.info("Launching Notepad for window utility testing...")
        
        cls.notepad_process = subprocess.Popen("notepad.exe")
        time.sleep(2)
        logger.info("✓ Notepad launched")
    
    @classmethod
    def tearDownClass(cls):
        """Close Notepad"""
        logger.info("Closing Notepad...")
        try:
            cls.notepad_process.terminate()
            cls.notepad_process.wait(timeout=5)
            logger.info("✓ Notepad closed")
        except:
            cls.notepad_process.kill()
            logger.info("✓ Notepad force-closed")
    
    def test_01_get_foreground_window(self):
        """Test getting foreground window"""
        logger.info("\n[Test 01] Get foreground window...")
        window_info = get_foreground_window()
        
        self.assertIsNotNone(window_info)
        self.assertGreater(window_info.hwnd, 0)
        logger.info(f"✓ Foreground window: {window_info.title}")
    
    def test_02_get_window_info(self):
        """Test getting detailed window info"""
        logger.info("\n[Test 02] Get detailed window info...")
        hwnd = find_window_by_title("Notepad")
        self.assertIsNotNone(hwnd)
        
        info = get_window_info(hwnd)
        self.assertIsNotNone(info)
        self.assertEqual(info.hwnd, hwnd)
        self.assertTrue(info.is_visible)
        logger.info(f"✓ Window info: {info.title} at ({info.x}, {info.y})")
    
    def test_03_find_window_by_class(self):
        """Test finding window by class name"""
        logger.info("\n[Test 03] Find window by class...")
        # Notepad class is typically "Notepad" or "Edit"
        hwnd = find_window_by_class("Notepad")
        self.assertIsNotNone(hwnd)
        logger.info(f"✓ Found window by class: hwnd={hwnd}")
    
    def test_04_get_window_position_size(self):
        """Test getting window position and size"""
        logger.info("\n[Test 04] Get window position and size...")
        hwnd = find_window_by_title("Notepad")
        result = get_window_position_size(hwnd)
        
        self.assertIsNotNone(result)
        x, y, width, height = result
        self.assertGreater(width, 0)
        self.assertGreater(height, 0)
        logger.info(f"✓ Position: ({x}, {y}), Size: {width}x{height}")
    
    def test_05_is_window_focused(self):
        """Test checking if window is focused"""
        logger.info("\n[Test 05] Check window focus status...")
        hwnd = find_window_by_title("Notepad")
        
        # Focus it first
        focus_window(hwnd)
        time.sleep(0.2)
        
        is_focused = is_window_focused(hwnd)
        self.assertTrue(is_focused)
        logger.info("✓ Window focus detection works")
    
    def test_06_list_windows(self):
        """Test listing all visible windows"""
        logger.info("\n[Test 06] List all visible windows...")
        windows = list_windows()
        
        self.assertGreater(len(windows), 0)
        logger.info(f"✓ Found {len(windows)} visible windows")
        
        # Print first few
        for i, window in enumerate(windows[:3]):
            logger.info(f"  {i+1}. {window.title} ({window.class_name})")
    
    def test_07_list_windows_by_title(self):
        """Test listing windows by title pattern"""
        logger.info("\n[Test 07] List windows by title pattern...")
        windows = list_windows_by_title("Notepad")
        
        self.assertGreater(len(windows), 0)
        logger.info(f"✓ Found {len(windows)} windows matching 'Notepad'")
    
    def test_08_window_info_to_dict(self):
        """Test WindowInfo.to_dict() method"""
        logger.info("\n[Test 08] Convert WindowInfo to dict...")
        hwnd = find_window_by_title("Notepad")
        info = get_window_info(hwnd)
        
        info_dict = info.to_dict()
        self.assertIn('hwnd', info_dict)
        self.assertIn('position', info_dict)
        self.assertIn('size', info_dict)
        self.assertIn('visible', info_dict)
        logger.info(f"✓ WindowInfo converted to dict successfully")


class TestActionExecutorEnhancements(unittest.TestCase):
    """Test enhanced action_executor.py functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Launch Notepad"""
        logger.info("\n" + "=" * 70)
        logger.info("PHASE 4: ACTION EXECUTOR ENHANCEMENTS")
        logger.info("=" * 70)
        cls.notepad_process = subprocess.Popen("notepad.exe")
        time.sleep(2)
    
    @classmethod
    def tearDownClass(cls):
        """Close Notepad"""
        try:
            cls.notepad_process.terminate()
            cls.notepad_process.wait(timeout=5)
        except:
            cls.notepad_process.kill()
    
    def setUp(self):
        """Set up before each test"""
        self.executor = ActionExecutor(target_window_title="Notepad")
        self.executor.find_target_window("Notepad")
        self.executor.focus_target_window()
        pyautogui.FAILSAFE = False
    
    # ==================== KEYSTROKE MAPPING TESTS ====================
    
    def test_09_keystroke_mapping_basic(self):
        """Test basic keystroke mapping"""
        logger.info("\n[Test 09] Keystroke mapping - basic keys...")
        
        test_cases = [
            ('enter', 'enter'),
            ('tab', 'tab'),
            ('escape', 'esc'),
            ('backspace', 'backspace'),
            ('space', 'space'),
        ]
        
        for input_key, expected in test_cases:
            mapped = self.executor._map_keystroke(input_key)
            self.assertEqual(mapped, expected)
            logger.info(f"  ✓ {input_key} → {mapped}")
    
    def test_10_keystroke_mapping_special_keys(self):
        """Test mapping special keys"""
        logger.info("\n[Test 10] Keystroke mapping - special keys...")
        
        test_cases = [
            ('home', 'home'),
            ('end', 'end'),
            ('pageup', 'pageup'),
            ('delete', 'delete'),
            ('insert', 'insert'),
        ]
        
        for input_key, expected in test_cases:
            mapped = self.executor._map_keystroke(input_key)
            self.assertEqual(mapped, expected)
            logger.info(f"  ✓ {input_key} → {mapped}")
    
    def test_11_keystroke_mapping_arrow_keys(self):
        """Test mapping arrow keys"""
        logger.info("\n[Test 11] Keystroke mapping - arrow keys...")
        
        test_cases = ['up', 'down', 'left', 'right']
        
        for key in test_cases:
            mapped = self.executor._map_keystroke(key)
            self.assertEqual(mapped, key)
            logger.info(f"  ✓ {key} → {mapped}")
    
    def test_12_keystroke_mapping_function_keys(self):
        """Test mapping function keys"""
        logger.info("\n[Test 12] Keystroke mapping - function keys...")
        
        for i in range(1, 13):
            key = f'f{i}'
            mapped = self.executor._map_keystroke(key)
            self.assertEqual(mapped, key)
        
        logger.info("✓ F1-F12 mapping works")
    
    def test_13_keystroke_mapping_combinations(self):
        """Test mapping key combinations"""
        logger.info("\n[Test 13] Keystroke mapping - key combinations...")
        
        test_cases = [
            ('ctrl+s', 'ctrl+s'),
            ('ctrl+z', 'ctrl+z'),
            ('shift+tab', 'shift+tab'),
            ('ctrl+a', 'ctrl+a'),
        ]
        
        for input_combo, expected in test_cases:
            mapped = self.executor._map_keystroke(input_combo)
            self.assertEqual(mapped, expected)
            logger.info(f"  ✓ {input_combo} → {mapped}")
    
    # ==================== SPECIAL CHARACTER TESTS ====================
    
    def test_14_special_character_mapping(self):
        """Test special character mapping"""
        logger.info("\n[Test 14] Special character mapping...")
        
        test_chars = ['@', '#', '$', '%', '&', '*', '(', ')']
        
        for char in test_chars:
            self.assertIn(char, self.executor.SPECIAL_CHARS)
            logger.info(f"  ✓ {char} mapped")
        
        logger.info("✓ Special character mappings verified")
    
    # ==================== NUMBER VALIDATION TESTS ====================
    
    def test_15_valid_perio_numbers(self):
        """Test valid periodontal numbers (0-15)"""
        logger.info("\n[Test 15] Valid perio numbers (0-15)...")
        
        valid_numbers = list(range(0, 16))
        
        for num in valid_numbers:
            self.executor.focus_target_window()
            # Clear
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            pyautogui.press('delete')
            time.sleep(0.2)
            
            result = self.executor.type_number(num)
            self.assertTrue(result, f"Should type number {num}")
        
        logger.info("✓ All valid numbers (0-15) typed successfully")
    
    def test_16_invalid_perio_numbers(self):
        """Test invalid periodontal numbers"""
        logger.info("\n[Test 16] Invalid perio numbers...")
        
        invalid_numbers = [-1, 16, 20, 100]
        
        for num in invalid_numbers:
            result = self.executor.type_number(num)
            self.assertFalse(result, f"Should fail for number {num}")
        
        logger.info("✓ Invalid numbers properly rejected")
    
    # ==================== KEYSTROKE DELAY TESTS ====================
    
    def test_17_set_keystroke_delay(self):
        """Test setting keystroke delay"""
        logger.info("\n[Test 17] Set keystroke delay...")
        
        delay_ms = 100
        self.executor.set_keystroke_delay(delay_ms)
        self.assertAlmostEqual(self.executor.keystroke_delay, delay_ms / 1000.0, places=3)
        
        logger.info(f"✓ Keystroke delay set to {delay_ms}ms")
    
    def test_18_keystroke_delay_effect(self):
        """Test that keystroke delay affects typing speed"""
        logger.info("\n[Test 18] Keystroke delay effect on typing speed...")
        
        self.executor.focus_target_window()
        
        # Test with 10ms delay
        self.executor.set_keystroke_delay(10)
        start = time.time()
        self.executor.type_text("ABC")
        time_10ms = time.time() - start
        
        # Clear
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.press('delete')
        time.sleep(0.2)
        
        # Test with 100ms delay
        self.executor.set_keystroke_delay(100)
        start = time.time()
        self.executor.type_text("ABC")
        time_100ms = time.time() - start
        
        # 100ms delay should take roughly 10x longer (approximately)
        # We allow some margin for system variance
        self.assertGreater(time_100ms, time_10ms * 3)
        logger.info(f"✓ 10ms delay: {time_10ms:.3f}s, 100ms delay: {time_100ms:.3f}s")
    
    # ==================== TARGET WINDOW INFO TESTS ====================
    
    def test_19_get_target_window_info(self):
        """Test getting target window information"""
        logger.info("\n[Test 19] Get target window info...")
        
        info = self.executor.get_target_window_info()
        self.assertIsNotNone(info)
        self.assertIn('hwnd', info)
        self.assertIn('title', info)
        self.assertIn('position', info)
        self.assertIn('size', info)
        
        logger.info(f"✓ Window info retrieved: {info['title']}")
    
    def test_20_is_target_window_focused(self):
        """Test checking if target window is focused"""
        logger.info("\n[Test 20] Check if target window is focused...")
        
        self.executor.focus_target_window()
        time.sleep(0.2)
        
        is_focused = self.executor.is_target_window_focused()
        self.assertTrue(is_focused)
        
        logger.info("✓ Target window focus detection works")
    
    # ==================== CONVENIENCE METHOD TESTS ====================
    
    def test_21_convenience_methods(self):
        """Test convenience keystroke methods"""
        logger.info("\n[Test 21] Convenience keystroke methods...")
        
        self.executor.focus_target_window()
        
        # Clear first
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.press('delete')
        time.sleep(0.2)
        
        # Test methods
        test_methods = [
            ('press_enter', self.executor.press_enter),
            ('press_tab', self.executor.press_tab),
            ('press_escape', self.executor.press_escape),
        ]
        
        for method_name, method in test_methods:
            result = method()
            self.assertTrue(result)
            logger.info(f"  ✓ {method_name} works")
        
        logger.info("✓ All convenience methods work")
    
    def test_22_ctrl_key_combinations(self):
        """Test Ctrl key combinations"""
        logger.info("\n[Test 22] Ctrl key combinations...")
        
        self.executor.focus_target_window()
        
        # Save (Ctrl+S)
        result = self.executor.save()
        self.assertTrue(result)
        time.sleep(0.3)
        
        # Undo (Ctrl+Z)
        result = self.executor.undo()
        self.assertTrue(result)
        time.sleep(0.3)
        
        logger.info("✓ Ctrl combinations work")


class TestEnhancedNumberSequencing(unittest.TestCase):
    """Test enhanced number sequencing with new features"""
    
    @classmethod
    def setUpClass(cls):
        """Launch Notepad"""
        logger.info("\n" + "=" * 70)
        logger.info("ENHANCED NUMBER SEQUENCING TESTS")
        logger.info("=" * 70)
        cls.notepad_process = subprocess.Popen("notepad.exe")
        time.sleep(2)
    
    @classmethod
    def tearDownClass(cls):
        """Close Notepad"""
        try:
            cls.notepad_process.terminate()
            cls.notepad_process.wait(timeout=5)
        except:
            cls.notepad_process.kill()
    
    def setUp(self):
        """Set up before each test"""
        executor = ActionExecutor(target_window_title="Notepad")
        executor.find_target_window("Notepad")
        executor.focus_target_window()
        
        self.sequencer = NumberSequencer()
        self.sequencer.set_action_executor(executor)
        self.executor = executor
        
        pyautogui.FAILSAFE = False
    
    def test_23_sequence_with_validation(self):
        """Test number sequencing with validation"""
        logger.info("\n[Test 23] Number sequencing with validation...")
        
        # Clear
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.press('delete')
        time.sleep(0.2)
        
        result = self.sequencer.sequence_numbers([3, 2, 3])
        self.assertTrue(result)
        logger.info("✓ Sequence [3, 2, 3] entered successfully")
    
    def test_24_sequence_boundary_values(self):
        """Test sequence with boundary values"""
        logger.info("\n[Test 24] Sequence with boundary values...")
        
        test_cases = [
            [0, 0, 0],
            [15, 15, 15],
            [0, 7, 15],
        ]
        
        for seq in test_cases:
            # Clear
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            pyautogui.press('delete')
            time.sleep(0.2)
            
            result = self.sequencer.sequence_numbers(seq)
            self.assertTrue(result)
            logger.info(f"  ✓ Sequence {seq} successful")
    
    def test_25_sequence_without_final_tab(self):
        """Test sequence without final tab"""
        logger.info("\n[Test 25] Sequence without final tab...")
        
        sequencer = NumberSequencer(tab_after_sequence=False)
        sequencer.set_action_executor(self.executor)
        
        # Clear
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.press('delete')
        time.sleep(0.2)
        
        result = sequencer.sequence_numbers([3, 2, 3])
        self.assertTrue(result)
        logger.info("✓ Sequence without final tab works")


class TestEdgeCasesAndErrorHandling(unittest.TestCase):
    """Test edge cases and error handling"""
    
    @classmethod
    def setUpClass(cls):
        """Launch Notepad"""
        logger.info("\n" + "=" * 70)
        logger.info("EDGE CASES & ERROR HANDLING")
        logger.info("=" * 70)
        cls.notepad_process = subprocess.Popen("notepad.exe")
        time.sleep(2)
    
    @classmethod
    def tearDownClass(cls):
        """Close Notepad"""
        try:
            cls.notepad_process.terminate()
            cls.notepad_process.wait(timeout=5)
        except:
            cls.notepad_process.kill()
    
    def setUp(self):
        """Set up test fixtures"""
        self.executor = ActionExecutor(target_window_title="Notepad")
        self.executor.find_target_window("Notepad")
        pyautogui.FAILSAFE = False
    
    def test_26_empty_keystroke(self):
        """Test sending empty keystroke"""
        logger.info("\n[Test 26] Empty keystroke...")
        
        result = self.executor.send_keystroke("")
        self.assertFalse(result)
        logger.info("✓ Empty keystroke rejected")
    
    def test_27_empty_text(self):
        """Test typing empty text"""
        logger.info("\n[Test 27] Empty text...")
        
        self.executor.focus_target_window()
        result = self.executor.type_text("")
        self.assertTrue(result)  # Empty text is OK (no-op)
        logger.info("✓ Empty text handled gracefully")
    
    def test_28_empty_number_sequence(self):
        """Test empty number sequence"""
        logger.info("\n[Test 28] Empty number sequence...")
        
        result = self.executor.type_number_sequence([])
        self.assertTrue(result)  # Empty sequence is OK (no-op)
        logger.info("✓ Empty sequence handled gracefully")
    
    def test_29_invalid_keystroke_type(self):
        """Test invalid keystroke type"""
        logger.info("\n[Test 29] Invalid keystroke type...")
        
        # Non-existent key (should still work with pyautogui)
        result = self.executor.send_keystroke("nonexistent_key_xyz")
        # Result might be False or True depending on pyautogui behavior
        logger.info(f"✓ Invalid key handled (result: {result})")
    
    def test_30_rapid_number_sequence(self):
        """Test rapid number sequencing"""
        logger.info("\n[Test 30] Rapid number sequencing...")
        
        self.executor.set_keystroke_delay(10)  # Very fast
        self.executor.focus_target_window()
        
        # Clear
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.press('delete')
        time.sleep(0.2)
        
        result = self.executor.type_number_sequence([3, 2, 3], final_separator=True)
        self.assertTrue(result)
        time.sleep(0.3)
        
        logger.info("✓ Rapid sequence executed successfully")


def run_tests():
    """Run all Phase 4 tests with verbose output"""
    logger.info("\n" + "=" * 70)
    logger.info("PHASE 4: KEYSTROKE INJECTION - COMPREHENSIVE TEST SUITE")
    logger.info("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestWindowUtilsEnhancements))
    suite.addTests(loader.loadTestsFromTestCase(TestActionExecutorEnhancements))
    suite.addTests(loader.loadTestsFromTestCase(TestEnhancedNumberSequencing))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCasesAndErrorHandling))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("TEST SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Tests run: {result.testsRun}")
    logger.info(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    logger.info(f"Failures: {len(result.failures)}")
    logger.info(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        logger.info("\n✓ ALL TESTS PASSED - Phase 4 Complete!")
    else:
        logger.info("\n✗ SOME TESTS FAILED - Review output above")
    
    logger.info("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    import logging
    success = run_tests()
    sys.exit(0 if success else 1)
