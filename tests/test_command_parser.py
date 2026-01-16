"""
Test suite for CommandParser module - Phase 3 Command Processing Tests

Tests covering:
- Single number parsing
- Number sequence parsing (up to 6 numbers)
- Perio indicator parsing with fuzzy matching
- Navigation command parsing
- Action parsing
- App control parsing
- Edge cases and error handling
- Performance validation
"""

import unittest
import json
import os
import sys
import time
from pathlib import Path
from typing import List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from voiceperio.command_parser import CommandParser, Command


class TestCommandClass(unittest.TestCase):
    """Test cases for Command class"""
    
    def test_command_creation(self) -> None:
        """Test creating a Command object"""
        cmd = Command(action='number_sequence', numbers=[3, 2, 3])
        self.assertEqual(cmd.action, 'number_sequence')
        self.assertEqual(cmd.params['numbers'], [3, 2, 3])
    
    def test_command_repr(self) -> None:
        """Test Command string representation"""
        cmd = Command(action='keystroke', key='tab')
        repr_str = repr(cmd)
        self.assertIn('keystroke', repr_str)
        self.assertIn('tab', repr_str)


class TestCommandParserBasics(unittest.TestCase):
    """Test cases for CommandParser basic functionality"""
    
    @classmethod
    def setUpClass(cls) -> None:
        """Set up test fixtures"""
        cls.commands_file = Path(__file__).parent.parent / 'src' / 'voiceperio' / 'commands' / 'default_commands.json'
        cls.parser = CommandParser(str(cls.commands_file))
    
    def test_parser_initialization(self) -> None:
        """Test parser initializes without errors"""
        self.assertIsNotNone(self.parser)
        self.assertTrue(len(self.parser.word_to_number) > 0)
    
    def test_load_commands(self) -> None:
        """Test loading commands from JSON"""
        parser = CommandParser()
        result = parser.load_commands(str(self.commands_file))
        self.assertTrue(result)
        self.assertIn('numbers', parser.commands_db)
        self.assertIn('perio_indicators', parser.commands_db)
    
    def test_word_to_number_mapping(self) -> None:
        """Test word-to-number mapping is built correctly"""
        expected_numbers = [
            ('zero', 0), ('oh', 0), ('one', 1), ('two', 2),
            ('three', 3), ('four', 4), ('five', 5), ('six', 6),
            ('seven', 7), ('eight', 8), ('nine', 9), ('ten', 10),
            ('eleven', 11), ('twelve', 12), ('thirteen', 13),
            ('fourteen', 14), ('fifteen', 15)
        ]
        
        for word, expected_num in expected_numbers:
            self.assertEqual(self.parser.word_to_number.get(word), expected_num,
                           f"Word '{word}' should map to {expected_num}")


class TestSingleNumbers(unittest.TestCase):
    """Test cases for single number parsing"""
    
    @classmethod
    def setUpClass(cls) -> None:
        """Set up test fixtures"""
        commands_file = Path(__file__).parent.parent / 'src' / 'voiceperio' / 'commands' / 'default_commands.json'
        cls.parser = CommandParser(str(commands_file))
    
    def test_parse_single_zero(self) -> None:
        """Test parsing single zero"""
        cmd = self.parser.parse('zero')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.action, 'single_number')
        self.assertEqual(cmd.params['numbers'], [0])
    
    def test_parse_single_oh(self) -> None:
        """Test parsing 'oh' as zero"""
        cmd = self.parser.parse('oh')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['numbers'], [0])
    
    def test_parse_single_one(self) -> None:
        """Test parsing single one"""
        cmd = self.parser.parse('one')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['numbers'], [1])
    
    def test_parse_single_four(self) -> None:
        """Test parsing single four"""
        cmd = self.parser.parse('four')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['numbers'], [4])
    
    def test_parse_single_fifteen(self) -> None:
        """Test parsing single fifteen"""
        cmd = self.parser.parse('fifteen')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['numbers'], [15])
    
    def test_parse_uppercase_number(self) -> None:
        """Test parsing uppercase number (case-insensitive)"""
        cmd = self.parser.parse('FIVE')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['numbers'], [5])
    
    def test_parse_mixed_case_number(self) -> None:
        """Test parsing mixed case number"""
        cmd = self.parser.parse('ThReE')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['numbers'], [3])


class TestNumberSequences(unittest.TestCase):
    """Test cases for number sequence parsing"""
    
    @classmethod
    def setUpClass(cls) -> None:
        """Set up test fixtures"""
        commands_file = Path(__file__).parent.parent / 'src' / 'voiceperio' / 'commands' / 'default_commands.json'
        cls.parser = CommandParser(str(commands_file))
    
    def test_parse_two_number_sequence(self) -> None:
        """Test parsing two number sequence"""
        cmd = self.parser.parse('three two')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.action, 'number_sequence')
        self.assertEqual(cmd.params['numbers'], [3, 2])
    
    def test_parse_three_number_sequence(self) -> None:
        """Test parsing standard three number sequence"""
        cmd = self.parser.parse('three two three')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.action, 'number_sequence')
        self.assertEqual(cmd.params['numbers'], [3, 2, 3])
    
    def test_parse_four_number_sequence(self) -> None:
        """Test parsing four number sequence"""
        cmd = self.parser.parse('four three three four')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['numbers'], [4, 3, 3, 4])
    
    def test_parse_five_number_sequence(self) -> None:
        """Test parsing five number sequence"""
        cmd = self.parser.parse('two two two two two')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['numbers'], [2, 2, 2, 2, 2])
    
    def test_parse_six_number_sequence(self) -> None:
        """Test parsing six number sequence (maximum for perio)"""
        cmd = self.parser.parse('one one one one one one')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['numbers'], [1, 1, 1, 1, 1, 1])
    
    def test_parse_mixed_single_and_double_digit(self) -> None:
        """Test parsing sequence with double-digit numbers"""
        cmd = self.parser.parse('fifteen ten five')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['numbers'], [15, 10, 5])
    
    def test_parse_number_sequence_with_extra_spaces(self) -> None:
        """Test parsing with extra spaces"""
        cmd = self.parser.parse('  three   two   three  ')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['numbers'], [3, 2, 3])


class TestIsNumberSequence(unittest.TestCase):
    """Test cases for is_number_sequence method"""
    
    @classmethod
    def setUpClass(cls) -> None:
        """Set up test fixtures"""
        commands_file = Path(__file__).parent.parent / 'src' / 'voiceperio' / 'commands' / 'default_commands.json'
        cls.parser = CommandParser(str(commands_file))
    
    def test_single_number_is_number_sequence(self) -> None:
        """Test that single number is recognized as number sequence"""
        self.assertTrue(self.parser.is_number_sequence('four'))
    
    def test_multiple_numbers_is_number_sequence(self) -> None:
        """Test that multiple numbers are recognized as number sequence"""
        self.assertTrue(self.parser.is_number_sequence('three two three'))
    
    def test_text_with_non_number_is_not_sequence(self) -> None:
        """Test that text with non-numbers is not recognized as sequence"""
        self.assertFalse(self.parser.is_number_sequence('three bleeding'))
    
    def test_too_many_numbers_is_not_sequence(self) -> None:
        """Test that more than 6 numbers is not recognized as sequence"""
        self.assertFalse(self.parser.is_number_sequence('one one one one one one one'))
    
    def test_empty_string_is_not_sequence(self) -> None:
        """Test that empty string is not recognized as sequence"""
        self.assertFalse(self.parser.is_number_sequence(''))
    
    def test_unknown_words_is_not_sequence(self) -> None:
        """Test that unknown words are not recognized as sequence"""
        self.assertFalse(self.parser.is_number_sequence('blah blah blah'))


class TestExtractNumbers(unittest.TestCase):
    """Test cases for extract_numbers method"""
    
    @classmethod
    def setUpClass(cls) -> None:
        """Set up test fixtures"""
        commands_file = Path(__file__).parent.parent / 'src' / 'voiceperio' / 'commands' / 'default_commands.json'
        cls.parser = CommandParser(str(commands_file))
    
    def test_extract_single_number(self) -> None:
        """Test extracting single number"""
        numbers = self.parser.extract_numbers('four')
        self.assertEqual(numbers, [4])
    
    def test_extract_sequence(self) -> None:
        """Test extracting number sequence"""
        numbers = self.parser.extract_numbers('three two three')
        self.assertEqual(numbers, [3, 2, 3])
    
    def test_extract_with_zero_variants(self) -> None:
        """Test extracting zero in various forms"""
        numbers_zero = self.parser.extract_numbers('zero')
        numbers_oh = self.parser.extract_numbers('oh')
        self.assertEqual(numbers_zero, [0])
        self.assertEqual(numbers_oh, [0])
    
    def test_extract_with_double_digits(self) -> None:
        """Test extracting double-digit numbers"""
        numbers = self.parser.extract_numbers('ten eleven twelve')
        self.assertEqual(numbers, [10, 11, 12])
    
    def test_extract_empty_string(self) -> None:
        """Test extracting from empty string"""
        numbers = self.parser.extract_numbers('')
        self.assertEqual(numbers, [])
    
    def test_extract_no_numbers(self) -> None:
        """Test extracting when no numbers present"""
        numbers = self.parser.extract_numbers('hello world')
        self.assertEqual(numbers, [])
    
    def test_extract_case_insensitive(self) -> None:
        """Test extraction is case-insensitive"""
        numbers = self.parser.extract_numbers('THREE TWO THREE')
        self.assertEqual(numbers, [3, 2, 3])


class TestPerioIndicators(unittest.TestCase):
    """Test cases for perio indicator parsing"""
    
    @classmethod
    def setUpClass(cls) -> None:
        """Set up test fixtures"""
        commands_file = Path(__file__).parent.parent / 'src' / 'voiceperio' / 'commands' / 'default_commands.json'
        cls.parser = CommandParser(str(commands_file))
    
    def test_parse_bleeding(self) -> None:
        """Test parsing 'bleeding' indicator"""
        cmd = self.parser.parse('bleeding')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.action, 'indicator')
        self.assertEqual(cmd.params['indicator'], 'bleeding')
        self.assertEqual(cmd.params['key'], 'b')
    
    def test_parse_bleeding_alias_bleed(self) -> None:
        """Test parsing 'bleed' alias for bleeding"""
        cmd = self.parser.parse('bleed')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['indicator'], 'bleeding')
    
    def test_parse_bleeding_alias_bop(self) -> None:
        """Test parsing 'bop' alias for bleeding"""
        cmd = self.parser.parse('bop')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['indicator'], 'bleeding')
    
    def test_parse_suppuration(self) -> None:
        """Test parsing 'suppuration' indicator"""
        cmd = self.parser.parse('suppuration')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['indicator'], 'suppuration')
        self.assertEqual(cmd.params['key'], 's')
    
    def test_parse_suppuration_alias_pus(self) -> None:
        """Test parsing 'pus' alias for suppuration"""
        cmd = self.parser.parse('pus')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['indicator'], 'suppuration')
    
    def test_parse_plaque(self) -> None:
        """Test parsing 'plaque' indicator"""
        cmd = self.parser.parse('plaque')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['indicator'], 'plaque')
        self.assertEqual(cmd.params['key'], 'p')
    
    def test_parse_calculus(self) -> None:
        """Test parsing 'calculus' indicator"""
        cmd = self.parser.parse('calculus')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['indicator'], 'calculus')
        self.assertEqual(cmd.params['key'], 'c')
    
    def test_parse_calculus_alias_tartar(self) -> None:
        """Test parsing 'tartar' alias for calculus"""
        cmd = self.parser.parse('tartar')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['indicator'], 'calculus')
    
    def test_parse_furcation(self) -> None:
        """Test parsing 'furcation' indicator"""
        cmd = self.parser.parse('furcation')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['indicator'], 'furcation')
        self.assertEqual(cmd.params['key'], 'f')
    
    def test_parse_furcation_alias_furca(self) -> None:
        """Test parsing 'furca' alias for furcation"""
        cmd = self.parser.parse('furca')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['indicator'], 'furcation')
    
    def test_parse_mobility(self) -> None:
        """Test parsing 'mobility' indicator"""
        cmd = self.parser.parse('mobility')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['indicator'], 'mobility')
        self.assertEqual(cmd.params['key'], 'm')
    
    def test_parse_mobility_alias_mobile(self) -> None:
        """Test parsing 'mobile' alias for mobility"""
        cmd = self.parser.parse('mobile')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['indicator'], 'mobility')
    
    def test_parse_recession(self) -> None:
        """Test parsing 'recession' indicator"""
        cmd = self.parser.parse('recession')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['indicator'], 'recession')
        self.assertEqual(cmd.params['key'], 'r')
    
    def test_fuzzy_match_bleeding_variation(self) -> None:
        """Test fuzzy matching for speech variation 'blead'"""
        cmd = self.parser.parse('blead')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['indicator'], 'bleeding')
    



class TestNavigationCommands(unittest.TestCase):
    """Test cases for navigation command parsing"""
    
    @classmethod
    def setUpClass(cls) -> None:
        """Set up test fixtures"""
        commands_file = Path(__file__).parent.parent / 'src' / 'voiceperio' / 'commands' / 'default_commands.json'
        cls.parser = CommandParser(str(commands_file))
    
    def test_parse_next(self) -> None:
        """Test parsing 'next' navigation"""
        cmd = self.parser.parse('next')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.action, 'navigation')
        self.assertEqual(cmd.params['command'], 'next')
        self.assertEqual(cmd.params['key'], 'tab')
    
    def test_parse_next_alias_next_tooth(self) -> None:
        """Test parsing 'next tooth' alias"""
        cmd = self.parser.parse('next tooth')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['command'], 'next')
    
    def test_parse_previous(self) -> None:
        """Test parsing 'previous' navigation"""
        cmd = self.parser.parse('previous')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['command'], 'previous')
        self.assertEqual(cmd.params['key'], 'shift+tab')
    
    def test_parse_previous_alias_back(self) -> None:
        """Test parsing 'back' alias for previous"""
        cmd = self.parser.parse('back')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['command'], 'previous')
    
    def test_parse_previous_alias_prev(self) -> None:
        """Test parsing 'prev' alias for previous"""
        cmd = self.parser.parse('prev')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['command'], 'previous')
    
    def test_parse_skip(self) -> None:
        """Test parsing 'skip' navigation"""
        cmd = self.parser.parse('skip')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['command'], 'skip')
    
    def test_parse_upper_right(self) -> None:
        """Test parsing 'upper right' quadrant"""
        cmd = self.parser.parse('upper right')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['command'], 'upper_right')
        self.assertEqual(cmd.params['quadrant'], 1)
    
    def test_parse_upper_right_alias_ur(self) -> None:
        """Test parsing 'ur' alias for upper right"""
        cmd = self.parser.parse('ur')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['quadrant'], 1)
    
    def test_parse_upper_right_alias_quadrant_one(self) -> None:
        """Test parsing 'quadrant one' alias"""
        cmd = self.parser.parse('quadrant one')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['quadrant'], 1)
    
    def test_parse_upper_left(self) -> None:
        """Test parsing 'upper left' quadrant"""
        cmd = self.parser.parse('upper left')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['quadrant'], 2)
    
    def test_parse_lower_left(self) -> None:
        """Test parsing 'lower left' quadrant"""
        cmd = self.parser.parse('lower left')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['quadrant'], 3)
    
    def test_parse_lower_right(self) -> None:
        """Test parsing 'lower right' quadrant"""
        cmd = self.parser.parse('lower right')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['quadrant'], 4)
    
    def test_parse_facial(self) -> None:
        """Test parsing 'facial' side navigation"""
        cmd = self.parser.parse('facial')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['side'], 'facial')
    
    def test_parse_facial_alias_buccal(self) -> None:
        """Test parsing 'buccal' alias for facial"""
        cmd = self.parser.parse('buccal')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['side'], 'facial')
    
    def test_parse_lingual(self) -> None:
        """Test parsing 'lingual' side navigation"""
        cmd = self.parser.parse('lingual')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['side'], 'lingual')
    
    def test_parse_lingual_alias_palatal(self) -> None:
        """Test parsing 'palatal' alias for lingual"""
        cmd = self.parser.parse('palatal')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['side'], 'lingual')


class TestActionCommands(unittest.TestCase):
    """Test cases for action command parsing"""
    
    @classmethod
    def setUpClass(cls) -> None:
        """Set up test fixtures"""
        commands_file = Path(__file__).parent.parent / 'src' / 'voiceperio' / 'commands' / 'default_commands.json'
        cls.parser = CommandParser(str(commands_file))
    
    def test_parse_enter(self) -> None:
        """Test parsing 'enter' action"""
        cmd = self.parser.parse('enter')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.action, 'typed_action')
        self.assertEqual(cmd.params['action_name'], 'enter')
        self.assertEqual(cmd.params['key'], 'enter')
    
    def test_parse_enter_alias_okay(self) -> None:
        """Test parsing 'okay' alias for enter"""
        cmd = self.parser.parse('okay')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['action_name'], 'enter')
    
    def test_parse_enter_alias_ok(self) -> None:
        """Test parsing 'ok' alias for enter"""
        cmd = self.parser.parse('ok')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['action_name'], 'enter')
    
    def test_parse_cancel(self) -> None:
        """Test parsing 'cancel' action"""
        cmd = self.parser.parse('cancel')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['action_name'], 'cancel')
        self.assertEqual(cmd.params['key'], 'escape')
    
    def test_parse_cancel_alias_escape(self) -> None:
        """Test parsing 'escape' alias for cancel"""
        cmd = self.parser.parse('escape')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['action_name'], 'cancel')
    
    def test_parse_cancel_alias_esc(self) -> None:
        """Test parsing 'esc' alias for cancel"""
        cmd = self.parser.parse('esc')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['action_name'], 'cancel')
    
    def test_parse_save(self) -> None:
        """Test parsing 'save' action"""
        cmd = self.parser.parse('save')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['action_name'], 'save')
        self.assertEqual(cmd.params['key'], 'ctrl+s')
    
    def test_parse_undo(self) -> None:
        """Test parsing 'undo' action"""
        cmd = self.parser.parse('undo')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['action_name'], 'undo')
        self.assertEqual(cmd.params['key'], 'ctrl+z')
    
    def test_parse_correction(self) -> None:
        """Test parsing 'correction' action"""
        cmd = self.parser.parse('correction')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['action_name'], 'correction')
    
    def test_parse_correction_alias_scratch_that(self) -> None:
        """Test parsing 'scratch that' alias"""
        cmd = self.parser.parse('scratch that')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['action_name'], 'correction')
    
    def test_parse_correction_alias_scratch(self) -> None:
        """Test parsing 'scratch' alias"""
        cmd = self.parser.parse('scratch')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['action_name'], 'correction')


class TestAppControlCommands(unittest.TestCase):
    """Test cases for app control command parsing"""
    
    @classmethod
    def setUpClass(cls) -> None:
        """Set up test fixtures"""
        commands_file = Path(__file__).parent.parent / 'src' / 'voiceperio' / 'commands' / 'default_commands.json'
        cls.parser = CommandParser(str(commands_file))
    
    def test_parse_wake(self) -> None:
        """Test parsing 'wake' app control"""
        cmd = self.parser.parse('wake')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.action, 'app_control')
        self.assertEqual(cmd.params['command'], 'wake')
    
    def test_parse_wake_full_phrase(self) -> None:
        """Test parsing full 'voice perio wake' phrase"""
        cmd = self.parser.parse('voice perio wake')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['command'], 'wake')
    
    def test_parse_sleep(self) -> None:
        """Test parsing 'sleep' app control"""
        cmd = self.parser.parse('sleep')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['command'], 'sleep')
    
    def test_parse_sleep_full_phrase(self) -> None:
        """Test parsing full 'voice perio sleep' phrase"""
        cmd = self.parser.parse('voice perio sleep')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['command'], 'sleep')
    
    def test_parse_pause(self) -> None:
        """Test parsing 'pause' alias for sleep"""
        cmd = self.parser.parse('pause')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['command'], 'sleep')
    
    def test_parse_stop(self) -> None:
        """Test parsing 'stop' app control"""
        cmd = self.parser.parse('stop')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['command'], 'stop')
    
    def test_parse_stop_full_phrase(self) -> None:
        """Test parsing full 'voice perio stop' phrase"""
        cmd = self.parser.parse('voice perio stop')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['command'], 'stop')
    
    def test_parse_exit(self) -> None:
        """Test parsing 'exit' alias for stop"""
        cmd = self.parser.parse('exit')
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.params['command'], 'stop')


class TestEdgeCasesAndErrors(unittest.TestCase):
    """Test cases for edge cases and error handling"""
    
    @classmethod
    def setUpClass(cls) -> None:
        """Set up test fixtures"""
        commands_file = Path(__file__).parent.parent / 'src' / 'voiceperio' / 'commands' / 'default_commands.json'
        cls.parser = CommandParser(str(commands_file))
    
    def test_parse_empty_string(self) -> None:
        """Test parsing empty string"""
        cmd = self.parser.parse('')
        self.assertIsNone(cmd)
    
    def test_parse_whitespace_only(self) -> None:
        """Test parsing whitespace only"""
        cmd = self.parser.parse('   ')
        self.assertIsNone(cmd)
    
    def test_parse_unrecognized_text(self) -> None:
        """Test parsing unrecognized text"""
        cmd = self.parser.parse('xyz abc def')
        self.assertIsNone(cmd)
    
    def test_parse_mixed_numbers_and_indicators(self) -> None:
        """Test that mixed text doesn't parse as numbers"""
        cmd = self.parser.parse('three bleeding two')
        # Should not parse as number sequence since it has non-number
        self.assertNotEqual(cmd.action, 'number_sequence') if cmd else None
    
    def test_parser_without_loading_commands(self) -> None:
        """Test parser behavior when commands not loaded"""
        empty_parser = CommandParser()
        cmd = empty_parser.parse('three two three')
        self.assertIsNone(cmd)
    
    def test_parse_similar_sounding_words(self) -> None:
        """Test fuzzy matching doesn't over-match"""
        # 'bear' should NOT match 'bleed'
        cmd = self.parser.parse('bear')
        if cmd:
            self.assertNotEqual(cmd.params.get('indicator'), 'bleeding')
    
    def test_parse_seven_numbers_exceeds_limit(self) -> None:
        """Test that more than 6 numbers are rejected"""
        cmd = self.parser.parse('one two three four five six seven')
        # Should not be parsed as number sequence
        self.assertNotEqual(cmd.action, 'number_sequence') if cmd else None


class TestPerformance(unittest.TestCase):
    """Test cases for performance requirements"""
    
    @classmethod
    def setUpClass(cls) -> None:
        """Set up test fixtures"""
        commands_file = Path(__file__).parent.parent / 'src' / 'voiceperio' / 'commands' / 'default_commands.json'
        cls.parser = CommandParser(str(commands_file))
    
    def test_parse_performance_number_sequence(self) -> None:
        """Test parsing performance is under 5ms for number sequence"""
        start = time.time()
        for _ in range(100):
            self.parser.parse('three two three')
        elapsed = (time.time() - start) * 1000 / 100
        
        self.assertLess(elapsed, 5.0, f"Average parse time: {elapsed:.2f}ms (should be < 5ms)")
    
    def test_parse_performance_indicator(self) -> None:
        """Test parsing performance is under 5ms for indicator"""
        start = time.time()
        for _ in range(100):
            self.parser.parse('bleeding')
        elapsed = (time.time() - start) * 1000 / 100
        
        self.assertLess(elapsed, 5.0, f"Average parse time: {elapsed:.2f}ms (should be < 5ms)")
    
    def test_parse_performance_navigation(self) -> None:
        """Test parsing performance is under 5ms for navigation"""
        start = time.time()
        for _ in range(100):
            self.parser.parse('next tooth')
        elapsed = (time.time() - start) * 1000 / 100
        
        self.assertLess(elapsed, 5.0, f"Average parse time: {elapsed:.2f}ms (should be < 5ms)")


class TestIntegrationScenarios(unittest.TestCase):
    """Test cases for realistic clinical scenarios"""
    
    @classmethod
    def setUpClass(cls) -> None:
        """Set up test fixtures"""
        commands_file = Path(__file__).parent.parent / 'src' / 'voiceperio' / 'commands' / 'default_commands.json'
        cls.parser = CommandParser(str(commands_file))
    
    def test_scenario_basic_charting_sequence(self) -> None:
        """Test basic clinical charting scenario"""
        # Enter pocket depths
        cmd1 = self.parser.parse('three two three')
        self.assertEqual(cmd1.params['numbers'], [3, 2, 3])
        
        # Mark bleeding
        cmd2 = self.parser.parse('bleeding')
        self.assertEqual(cmd2.params['indicator'], 'bleeding')
        
        # Move to next tooth
        cmd3 = self.parser.parse('next')
        self.assertEqual(cmd3.params['command'], 'next')
    
    def test_scenario_correction_workflow(self) -> None:
        """Test correction workflow"""
        # User enters number
        cmd1 = self.parser.parse('three')
        self.assertIsNotNone(cmd1)
        
        # User says correction
        cmd2 = self.parser.parse('scratch that')
        self.assertEqual(cmd2.params['action_name'], 'correction')
        
        # User re-enters
        cmd3 = self.parser.parse('four')
        self.assertEqual(cmd3.params['numbers'], [4])
    
    def test_scenario_quadrant_navigation(self) -> None:
        """Test quadrant navigation scenario"""
        # Jump to upper right
        cmd1 = self.parser.parse('quadrant one')
        self.assertEqual(cmd1.params['quadrant'], 1)
        
        # Chart teeth
        cmd2 = self.parser.parse('three two three')
        self.assertEqual(cmd2.params['numbers'], [3, 2, 3])
        
        # Move to next tooth
        cmd3 = self.parser.parse('next')
        self.assertIsNotNone(cmd3)
    
    def test_scenario_side_switching(self) -> None:
        """Test side switching scenario"""
        # Chart facial
        cmd1 = self.parser.parse('three two three')
        self.assertEqual(cmd1.params['numbers'], [3, 2, 3])
        
        # Switch to lingual
        cmd2 = self.parser.parse('lingual')
        self.assertEqual(cmd2.params['side'], 'lingual')
        
        # Chart lingual
        cmd3 = self.parser.parse('three three two')
        self.assertEqual(cmd3.params['numbers'], [3, 3, 2])


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
