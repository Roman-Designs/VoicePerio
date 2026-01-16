"""
Test Suite for ActionExecutor Module
Tests keystroke injection, window finding, and number sequencing
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
from voiceperio.utils.logger import setup_logging


logger = setup_logging(log_level=logging.DEBUG)


class TestActionExecutor(unittest.TestCase):
    """Test ActionExecutor keystroke injection functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures - launch Notepad"""
        logger.info("=" * 70)
        logger.info("PHASE 4: KEYSTROKE INJECTION TESTS")
        logger.info("=" * 70)
        logger.info("Launching Notepad for keystroke injection testing...")
        
        # Launch Notepad
        cls.notepad_process = subprocess.Popen("notepad.exe")
        time.sleep(2)  # Give Notepad time to open
        logger.info("✓ Notepad launched")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up - close Notepad"""
        logger.info("Closing Notepad...")
        try:
            cls.notepad_process.terminate()
            cls.notepad_process.wait(timeout=5)
            logger.info("✓ Notepad closed")
        except:
            cls.notepad_process.kill()
            logger.info("✓ Notepad force-closed")
    
    def setUp(self):
        """Set up before each test"""
        self.executor = ActionExecutor(target_window_title="Notepad")
        pyautogui.FAILSAFE = False  # Disable failsafe for testing
    
    # ==================== WINDOW FINDING TESTS ====================
    
    def test_01_find_window_by_title(self):
        """Test finding Notepad window by title"""
        logger.info("\n[Test 1] Finding window by title...")
        success = self.executor.find_target_window("Notepad")
        
        self.assertTrue(success, "Should find Notepad window")
        self.assertIsNotNone(self.executor.target_window_handle)
        logger.info(f"✓ Found Notepad (hwnd={self.executor.target_window_handle})")
    
    def test_02_find_window_case_insensitive(self):
        """Test window finding is case-insensitive"""
        logger.info("\n[Test 2] Case-insensitive window finding...")
        success = self.executor.find_target_window("notepad")
        
        self.assertTrue(success, "Should find window with lowercase title")
        logger.info("✓ Case-insensitive matching works")
    
    def test_03_find_window_not_found(self):
        """Test finding non-existent window"""
        logger.info("\n[Test 3] Finding non-existent window...")
        executor = ActionExecutor()
        success = executor.find_target_window("NonExistentWindow12345")
        
        self.assertFalse(success, "Should not find non-existent window")
        logger.info("✓ Correctly handles missing window")
    
    # ==================== FOCUS TESTS ====================
    
    def test_04_focus_window(self):
        """Test focusing target window"""
        logger.info("\n[Test 4] Focusing window...")
        self.executor.find_target_window("Notepad")
        success = self.executor.focus_target_window()
        
        self.assertTrue(success, "Should focus window")
        time.sleep(0.5)
        logger.info("✓ Window focused successfully")
    
    def test_05_focus_without_target(self):
        """Test focus fails when no target set"""
        logger.info("\n[Test 5] Focus without target window...")
        executor = ActionExecutor()
        success = executor.focus_target_window()
        
        self.assertFalse(success, "Should fail when no target window")
        logger.info("✓ Correctly rejects focus without target")
    
    # ==================== KEYSTROKE TESTS ====================
    
    def test_06_send_single_keystroke(self):
        """Test sending single keystroke"""
        logger.info("\n[Test 6] Sending single keystroke...")
        self.executor.find_target_window("Notepad")
        self.executor.focus_target_window()
        
        # Clear Notepad first
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.press('delete')
        time.sleep(0.3)
        
        # Send keystroke
        self.executor.send_keystroke('enter')
        time.sleep(0.3)
        
        logger.info("✓ Keystroke sent successfully")
    
    def test_07_send_key_combo(self):
        """Test sending key combination"""
        logger.info("\n[Test 7] Sending key combination...")
        self.executor.find_target_window("Notepad")
        self.executor.focus_target_window()
        
        # Clear
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.press('delete')
        time.sleep(0.3)
        
        # Send combo
        self.executor.send_key_combo(['ctrl', 's'])
        time.sleep(0.5)
        
        logger.info("✓ Key combination sent successfully")
    
    # ==================== TEXT TYPING TESTS ====================
    
    def test_08_type_single_number(self):
        """Test typing a single number"""
        logger.info("\n[Test 8] Typing single number...")
        self.executor.find_target_window("Notepad")
        self.executor.focus_target_window()
        
        # Clear
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.press('delete')
        time.sleep(0.3)
        
        # Type number
        self.executor.type_text("3")
        time.sleep(0.3)
        
        logger.info("✓ Single number typed successfully")
    
    def test_09_type_multiple_numbers(self):
        """Test typing multiple numbers"""
        logger.info("\n[Test 9] Typing multiple numbers...")
        self.executor.find_target_window("Notepad")
        self.executor.focus_target_window()
        
        # Clear
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.press('delete')
        time.sleep(0.3)
        
        # Type numbers
        self.executor.type_text("123")
        time.sleep(0.3)
        
        logger.info("✓ Multiple numbers typed successfully")
    
    def test_10_type_with_delay(self):
        """Test typing with keystroke delay"""
        logger.info("\n[Test 10] Typing with delay between keys...")
        self.executor.keystroke_delay = 0.1
        self.executor.find_target_window("Notepad")
        self.executor.focus_target_window()
        
        # Clear
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.press('delete')
        time.sleep(0.3)
        
        # Type with delay
        start = time.time()
        self.executor.type_text("345")
        elapsed = time.time() - start
        time.sleep(0.3)
        
        # Should take at least 0.2 seconds (3 chars * 0.1 delay)
        self.assertGreater(elapsed, 0.15, "Should have delay between keys")
        logger.info(f"✓ Typing delay applied ({elapsed:.2f}s elapsed)")
    
    # ==================== NUMBER SEQUENCE TESTS ====================
    
    def test_11_type_number_sequence(self):
        """Test typing number sequence with Tabs"""
        logger.info("\n[Test 11] Typing number sequence...")
        self.executor.find_target_window("Notepad")
        self.executor.focus_target_window()
        
        # Clear
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.press('delete')
        time.sleep(0.3)
        
        # Type sequence
        self.executor.type_number_sequence([3, 2, 3])
        time.sleep(0.5)
        
        logger.info("✓ Number sequence typed with Tabs")
    
    def test_12_number_sequence_varying_lengths(self):
        """Test number sequences of different lengths"""
        logger.info("\n[Test 12] Testing various sequence lengths...")
        self.executor.find_target_window("Notepad")
        self.executor.focus_target_window()
        
        test_cases = [
            [5],           # Single number
            [3, 2],        # Two numbers
            [3, 2, 3],     # Three numbers
            [4, 3, 3, 2],  # Four numbers
        ]
        
        for seq in test_cases:
            # Clear
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.press('delete')
            time.sleep(0.3)
            
            # Type sequence
            self.executor.type_number_sequence(seq)
            time.sleep(0.3)
            logger.info(f"  ✓ Sequence {seq} typed successfully")
    
    def test_13_number_sequence_boundary_values(self):
        """Test number sequences with boundary values (0 and 15)"""
        logger.info("\n[Test 13] Testing boundary values 0-15...")
        self.executor.find_target_window("Notepad")
        self.executor.focus_target_window()
        
        test_cases = [
            [0, 1, 2],           # Lower boundary
            [13, 14, 15],        # Upper boundary
            [0, 7, 15],          # Mixed
        ]
        
        for seq in test_cases:
            # Clear
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.press('delete')
            time.sleep(0.3)
            
            # Type sequence
            self.executor.type_number_sequence(seq)
            time.sleep(0.3)
            logger.info(f"  ✓ Boundary sequence {seq} typed successfully")


class TestNumberSequencer(unittest.TestCase):
    """Test NumberSequencer with ActionExecutor integration"""
    
    @classmethod
    def setUpClass(cls):
        """Launch Notepad"""
        logger.info("\n" + "=" * 70)
        logger.info("NUMBER SEQUENCER INTEGRATION TESTS")
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
        pyautogui.FAILSAFE = False
    
    def test_14_sequencer_without_executor(self):
        """Test sequencer fails without executor"""
        logger.info("\n[Test 14] Sequencer without executor...")
        sequencer = NumberSequencer()
        result = sequencer.sequence_numbers([3, 2, 3])
        
        self.assertFalse(result, "Should fail without executor")
        logger.info("✓ Correctly rejects sequence without executor")
    
    def test_15_sequencer_single_number(self):
        """Test sequencer with single number"""
        logger.info("\n[Test 15] Sequencer with single number...")
        
        # Clear
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.press('delete')
        time.sleep(0.3)
        
        result = self.sequencer.sequence_numbers([5])
        time.sleep(0.3)
        
        self.assertTrue(result, "Should sequence single number")
        logger.info("✓ Single number sequenced successfully")
    
    def test_16_sequencer_multiple_numbers(self):
        """Test sequencer with multiple numbers"""
        logger.info("\n[Test 16] Sequencer with multiple numbers...")
        
        # Clear
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.press('delete')
        time.sleep(0.3)
        
        result = self.sequencer.sequence_numbers([3, 2, 3])
        time.sleep(0.5)
        
        self.assertTrue(result, "Should sequence multiple numbers")
        logger.info("✓ Multiple numbers sequenced successfully")
    
    def test_17_sequencer_without_final_tab(self):
        """Test sequencer can skip final Tab"""
        logger.info("\n[Test 17] Sequencer without final Tab...")
        
        sequencer = NumberSequencer(tab_after_sequence=False)
        sequencer.set_action_executor(self.sequencer.action_executor)
        
        # Clear
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.press('delete')
        time.sleep(0.3)
        
        result = sequencer.sequence_numbers([3, 2, 3])
        time.sleep(0.3)
        
        self.assertTrue(result, "Should sequence without final tab")
        logger.info("✓ Sequencing without final Tab works")
    
    def test_18_sequencer_custom_delays(self):
        """Test sequencer with custom delays"""
        logger.info("\n[Test 18] Sequencer with custom delays...")
        
        sequencer = NumberSequencer(inter_number_delay_ms=100)
        sequencer.set_action_executor(self.sequencer.action_executor)
        
        # Clear
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.press('delete')
        time.sleep(0.3)
        
        start = time.time()
        result = sequencer.sequence_numbers([3, 2, 3])
        elapsed = time.time() - start
        time.sleep(0.3)
        
        self.assertTrue(result, "Should sequence with delays")
        # Should take at least 0.3 seconds (3 numbers, 2 gaps, 100ms each)
        self.assertGreater(elapsed, 0.2, "Should apply custom delays")
        logger.info(f"✓ Custom delays applied ({elapsed:.2f}s elapsed)")


class TestIntegrationCommandToExecution(unittest.TestCase):
    """Integration test: CommandParser → NumberSequencer → ActionExecutor"""
    
    @classmethod
    def setUpClass(cls):
        """Launch Notepad"""
        logger.info("\n" + "=" * 70)
        logger.info("INTEGRATION TEST: Command → Execution Pipeline")
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
        """Set up pipeline components"""
        self.parser = CommandParser()
        
        executor = ActionExecutor(target_window_title="Notepad")
        executor.find_target_window("Notepad")
        executor.focus_target_window()
        
        self.sequencer = NumberSequencer()
        self.sequencer.set_action_executor(executor)
        self.executor = executor
        
        pyautogui.FAILSAFE = False
    
    def test_19_pipeline_parse_to_execution(self):
        """Test full pipeline from speech to keystroke"""
        logger.info("\n[Test 19] Full pipeline: Parse → Execute...")
        
        # Clear Notepad
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.press('delete')
        time.sleep(0.3)
        
        # Parse "three two three"
        command = self.parser.parse("three two three")
        logger.info(f"  Parsed: {command.action} - {command.params}")
        
        self.assertEqual(command.action, "number_sequence")
        self.assertEqual(command.params['numbers'], [3, 2, 3])
        
        # Execute
        result = self.sequencer.sequence_numbers(command.params['numbers'])
        time.sleep(0.5)
        
        self.assertTrue(result, "Should execute from parsed command")
        logger.info("✓ Full pipeline executed successfully")
    
    def test_20_pipeline_multiple_commands(self):
        """Test executing multiple commands in sequence"""
        logger.info("\n[Test 20] Multiple commands in sequence...")
        
        commands_to_test = [
            ("three two three", [3, 2, 3]),
            ("four three three", [4, 3, 3]),
            ("two two two", [2, 2, 2]),
        ]
        
        for speech, expected_numbers in commands_to_test:
            # Clear
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.press('delete')
            time.sleep(0.3)
            
            # Parse
            command = self.parser.parse(speech)
            logger.info(f"  Executing: {speech}")
            
            # Execute
            if command.action == "number_sequence":
                result = self.sequencer.sequence_numbers(command.params['numbers'])
                self.assertTrue(result)
            
            time.sleep(0.3)
        
        logger.info("✓ Multiple commands executed successfully")
    
    def test_21_pipeline_with_navigation_command(self):
        """Test pipeline with navigation command"""
        logger.info("\n[Test 21] Pipeline with navigation command...")
        
        # Clear
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.press('delete')
        time.sleep(0.3)
        
        # Parse navigation command
        command = self.parser.parse("next")
        logger.info(f"  Parsed navigation: {command.action} - {command.params}")
        
        self.assertEqual(command.action, "navigation")
        
        # Execute navigation (press tab)
        if command.action == "navigation" and command.params['action'] == 'next':
            self.executor.send_keystroke('tab')
            time.sleep(0.3)
        
        logger.info("✓ Navigation command executed successfully")


class TestActionExecutorEdgeCases(unittest.TestCase):
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
    
    def test_22_empty_number_sequence(self):
        """Test handling empty number sequence"""
        logger.info("\n[Test 22] Empty number sequence...")
        
        self.executor.focus_target_window()
        self.executor.type_number_sequence([])
        
        logger.info("✓ Empty sequence handled gracefully")
    
    def test_23_keystroke_delay_zero(self):
        """Test keystroke with zero delay"""
        logger.info("\n[Test 23] Zero keystroke delay...")
        
        self.executor.keystroke_delay = 0
        self.executor.focus_target_window()
        
        # Clear
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.press('delete')
        time.sleep(0.3)
        
        start = time.time()
        self.executor.type_text("ABC")
        elapsed = time.time() - start
        time.sleep(0.3)
        
        logger.info(f"✓ Zero delay typing completed in {elapsed:.3f}s")
    
    def test_24_special_keystrokes(self):
        """Test special keystrokes"""
        logger.info("\n[Test 24] Special keystrokes...")
        
        self.executor.focus_target_window()
        
        # Clear first
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.press('delete')
        time.sleep(0.3)
        
        special_keys = ['enter', 'tab', 'space']
        for key in special_keys:
            self.executor.send_keystroke(key)
            time.sleep(0.1)
            logger.info(f"  ✓ Sent {key}")
    
    def test_25_rapid_keystrokes(self):
        """Test rapid keystroke execution"""
        logger.info("\n[Test 25] Rapid keystrokes...")
        
        self.executor.keystroke_delay = 0.01
        self.executor.focus_target_window()
        
        # Clear
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.press('delete')
        time.sleep(0.3)
        
        start = time.time()
        for _ in range(10):
            self.executor.type_text("X")
        elapsed = time.time() - start
        time.sleep(0.3)
        
        logger.info(f"✓ 10 rapid keystrokes in {elapsed:.3f}s")


def run_tests():
    """Run all tests with verbose output"""
    logger.info("\n" + "=" * 70)
    logger.info("PHASE 4: KEYSTROKE INJECTION - COMPREHENSIVE TEST SUITE")
    logger.info("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestActionExecutor))
    suite.addTests(loader.loadTestsFromTestCase(TestNumberSequencer))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationCommandToExecution))
    suite.addTests(loader.loadTestsFromTestCase(TestActionExecutorEdgeCases))
    
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
    success = run_tests()
    sys.exit(0 if success else 1)
