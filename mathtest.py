#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  mathtest.py
#
#  Copyright 2017  <tjohnsen@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
import sys
import argparse
import copy
import os
from random import randint
from time import time

if sys.version_info.major == 2:
    print("This will run in Python 2 but with some problems.\n\t* You've been warned *")
    if os.name == 'nt':
        operator_translation = {ord('*'): u"x", ord('/'): u"÷"}
    else:
        operator_translation = {ord('*'): u"×", ord('/'): u"÷"}
else:
    raw_input = input
    unicode = str
    operator_translation = str.maketrans("*/", "×÷")


class Question(object):
    """
    A single math question that has two numbers and an operator between them.
    """
    def __init__(self, **kwargs):
        """
        Create an empty Question object or supply keyword elements.
        You can limit the list of valid_operators to limit what types of questions to create.
        If the operator isn't specified the program will generate a random operator from the list of valid_operators.

        :param operator: The operator for the math question
        :param first_number: The first number displayed on screen
        :param second_number: The second number displayed on screen
        :param user_answer: The answer that the user gave
        :param correct_answer: The correct answer (should let the program decide)
        :param valid_operators: A list of operators that are allowed in this question
        """
        self.operator = kwargs.get("operator")
        self.first_number = kwargs.get("first_number")
        self.second_number = kwargs.get("second_number")
        self.user_answer = kwargs.get("user_answer")
        self.valid_operators = kwargs.get("valid_operators", ["/", "*", "+", "-"])

    def __str__(self):
        formula = "{n.first_number} {n.operator} {n.second_number} = ".format(n=self)
        return formula

    def __eq__(self, other):
        if type(other) is type(self):
            return self.first_number == other.first_number \
                   and self.operator == other.operator \
                   and self.second_number == other.second_number
        else:
            return False

    def _check(self):
        """
        Ensure all properties are set properly.
        :return: Boolean
        """
        check = self.first_number is not None and self.second_number is not None
        check = check and self.operator in self.valid_operators
        # # opted to not check divide by zero and will raise exception instead
        # if self.operator == '/':
        #     # if dividing, ensure the second number is not 0.
        #     check = check and self.second_number != 0
        return check

    def generate_rand_question(self, **kwargs):
        """
        Generate a random equation.
        :param operator: Optionally specify operator to use in the equation
        :param first_number: Optionally specify the first number in equation
        :param second_number: Optionally specify the second number in equation
        """
        self.operator = kwargs.get("operator", self.valid_operators[randint(0, len(self.valid_operators) - 1)])
        # multiplication generates [0-9] * [0-9]
        if self.operator == "*":
            self.first_number = kwargs.get("first_number", randint(0, 9))
            self.second_number = kwargs.get("second_number", randint(0, 9))
        # division chooses numbers that will only divide evenly; won't divide by zero
        elif self.operator == "/":
            self.second_number = kwargs.get("second_number", randint(1, 9))
            self.first_number = kwargs.get("first_number", self.second_number * randint(0, 9))
            # if the user wants the second number to be zero and the operator is division
            # raise the error now. dev can handle this how they see fit. still sets the first number.
            if self.second_number == 0:
                raise ZeroDivisionError  # "Second number is zero in division equation."
        elif self.operator == "+":
            self.first_number = kwargs.get("first_number", randint(0, 19))
            self.second_number = kwargs.get("second_number", randint(0, 19))
        # subtraction chooses numbers that only result in positive answers (or 0)
        elif self.operator == "-":
            self.first_number = kwargs.get("first_number", randint(4, 19))
            self.second_number = kwargs.get("second_number", randint(0, self.first_number))

    @property
    def correct_answer(self):
        if self._check():
            return int(eval("{}".format(self.__str__().replace('=', ''))))
        else:
            return None

    @property
    def user_answer_correct(self):
        """
        Grade the answer by comparing the user's answer to the correct answer.
        :return: Boolean if the user's answer is correct
        """
        if self.user_answer is None:
            return False
        else:
            return self.user_answer == self.correct_answer

    def values(self):
        """
        Returns the values in this object as a tuple.
        :return: first number, operator, second number, user's answer
        """
        return self.first_number, self.operator, self.second_number, self.user_answer

    def human_readable(self):
        """
        Return the equation using unicode characters for multiplication and division.
        :return: Unicode string
        """
        return unicode(self).translate(operator_translation)

    def reset(self):
        """
        Reset values to None.
        """
        self.operator = None
        self.first_number = None
        self.second_number = None
        self.user_answer = None

    def _visualize_add_sub(self):
        for number in (self.first_number, self.second_number):
            print("{number:<3}: {stars}".format(number="{}:".format(number), stars='* ' * number))

    def _visualize_mul_div(self):
        if self.operator == '*':
            num2 = self.first_number
            num1 = self.second_number
        if self.operator == '/':
            num1 = self.correct_answer
            num2 = self.second_number

        # print column titles
        sys.stdout.write("   ")
        for y in range(num1):
            sys.stdout.write("{:^3}".format(y+1 if self.operator == '*' else '*'))
        print("")

        for y in range(num2):
            sys.stdout.write("{row_number}: ".format(row_number=y+1))
            for x in range(num1):
                display = (x+(y*num1))+1 if self.operator == '/' else '*'
                sys.stdout.write("{number:^3}".format(number=display))
            print("")  # newline

    def visualize(self):
        """
        Print a graphic visualization of the equation to the screen.
        """
        if self._check():
            if self.operator in '+-':
                self._visualize_add_sub()
            if self.operator in '*/':
                self._visualize_mul_div()

    def prompt(self, **kwargs):
        """
        Prompt the user with a random equation and get their answer.
        :param operator (Optional): specify specific operator when generating a random question
        :param first_number (Optional): specify constant first number when generating a random question
        :param second_number (Optional): specify constant second number when generating a random question
        """
        valid = False

        # if the question is missing any portions, generate new question
        if not self._check():
            self.generate_rand_question(**kwargs)

        if self._check():
            if kwargs.get("visualize"):
                self.visualize()
                print("")
            while not valid:
                try:
                    sys.stdout.write(self.human_readable())
                    self.user_answer = raw_input()
                    if self.user_answer == '':
                        pass  # put on skipped stack
                    else:
                        self.user_answer = int(self.user_answer)
                    valid = True
                except ValueError:
                    print("Invalid answer: Try again!")
                    continue
        else:
            self.user_answer = None


class Test(object):
    """
    Track multiple questions and log right and wrong answers.  Display results at the end of the test.
    """
    def __init__(self, **kwargs):
        self.right = []
        self.wrong = []
        self.skip = []
        self.question = Question(**kwargs)

    def __str__(self):
        return self._display_score()

    @property
    def grade(self):
        """
        Grade the test and return a percentage.
        :return: Float - Percent correct or 0 if no questions have been answered
        """
        total = len(self.wrong) + len(self.right) + len(self.skip)
        if total > 0:
            return float(len(self.right)) / float(total) * 100
        else:
            return 0

    def reset(self):
        """
        Reset the results of the test by clearing the list of right and wrong answers.
        """
        # delete all Question objects and replace them with a new empty list
        self.question.reset()
        del self.right
        self.right = []
        del self.wrong
        self.wrong = []
        del self.skip
        self.skip = []

    def limit_operators(self, operator_list):
        """
        Change the list of valid operators in the Question object.  If the supplied list doesn't contain any valid
        operators, exit with value 9.
        :param operator_list: List of valid operators to use during random generation of equations.
        """
        valid_operator_list = []
        for operator in operator_list:
            if operator in Question().valid_operators:
                valid_operator_list.append(operator)
        if len(valid_operator_list) == 0:
            print("List of supplied operators doesn't contain any valid operators! ({})".format(operator_list))
            print("The valid list of operators is: {}".format(Question().valid_operators))
            exit(9)
        self.question.valid_operators = valid_operator_list

    def score(self):
        """
        Score the equation by comparing the user's answer to the correct answer.
        Does nothing if the question isn't answered.
        """
        if self.question.user_answer is not None:
            if str(self.question.user_answer) == '':
                self.skip.append(copy.deepcopy(self.question))
                print("Skipped!\n")
            elif self.question.user_answer_correct:
                self.right.append(copy.deepcopy(self.question))
                print("Correct!\n")
            else:
                self.wrong.append(copy.deepcopy(self.question))
                print("Wrong! ({})\n".format(self.question.correct_answer))
            self.question.reset()

    @staticmethod
    def _rows_str(equation_list, columns=16):
        """
        Print a list of equations to the screen with 5 per row maximum.
        :param equation_list: List of tuple values using format (first number, operator, second operator, user answer)
        :param columns: Optional number of columns to print to the screen.  Default is 5.
        """
        if len(equation_list) == 0:
            return_string = "None\n"
        else:
            return_string = ''
            highs = [x.first_number for x in equation_list]
            ops = [x.operator for x in equation_list]
            lows = [x.second_number for x in equation_list]
            answers = [x.user_answer for x in equation_list]
            correct = [x.correct_answer for x in equation_list]
            for x in range(0, len(highs), columns):
                for y in range(columns if x + columns < (len(highs)) else len(highs) - x):
                    return_string += "{:>3}  ".format(highs[x + y])
                return_string += '\b\n'
                for y in range(columns if x + columns < (len(lows)) else len(lows) - x):
                    return_string += u"{}  ".format(u"{}{:>2}".format(ops[x + y], lows[x + y])).translate(
                        operator_translation)
                return_string += '\b\n'
                for y in range(columns if x + columns < (len(highs)) else len(highs) - x):
                    return_string += "---  ".format(highs[x + y])
                return_string += '\b\n'
                for y in range(columns if x + columns < (len(answers)) else len(answers) - x):
                    return_string += "{:>3}  ".format(answers[x + y])
                return_string += '\b\n'
                if answers != correct:
                    for y in range(columns if x + columns < (len(correct)) else len(correct) - x):
                        return_string += "({:>2}) ".format(int(correct[x + y]))
                    return_string += '\b\n'
                return_string += '\n'  # extra new line separator
        return return_string

    def print_rows(self, equation_list, columns=5):
        """
        Print a list of equations to the screen with 5 per row maximum.
        :param equation_list: List of tuple values using format (first number, operator, second operator, user answer)
        :param columns: Optional number of columns to print to the screen.  Default is 5.
        """
        print(self._rows_str(equation_list, columns=columns))

    def _display_score(self, **kwargs):
        """
        Display the number of equations answered correctly and incorrectly.
        :param columns: The number of columns per row to print to the screen.
        """
        skipped = len(self.skip)
        columns = kwargs.get("columns", 16)
        summary_format = "{{:^{}}}\n".format(columns * 5)
        test_string = '\n{}\n\n'.format('-' * (columns * 5))
        test_string += summary_format.format("Right    Wrong{}".format('' if skipped == 0 else "   Skipped"))
        test_string += summary_format.format("-----    -----{}".format('' if skipped == 0 else "   -------"))
        test_string += summary_format.format("{:^5}    {:^5}{}".format(len(self.right), len(self.wrong),
                                                                   '' if skipped == 0 else "   {:^7}".format(skipped)))
        test_string += "\n"
        test_string += "Correct Answers:\n\n"
        test_string += self._rows_str(self.right, columns=columns)
        test_string += "\n"
        test_string += "Wrong Answers:\n\n"
        test_string += self._rows_str(self.wrong, columns=columns)
        test_string += "\n"
        if skipped != 0:
            test_string += "Skipped:\n\n"
            test_string += self._rows_str(self.skip, columns=columns)
            test_string += "\n"
        return test_string

    def display_score(self, **kwargs):
        """
        Display the number of equations answered correctly and incorrectly.
        :param columns: The number of columns per row to print to the screen.
        """
        print(self._display_score(**kwargs))

    def get(self, attribute):
        """
        Return list of attribute desired.
        :param attribute: String of list desired: right, wrong, skip
        :return: List of questions OR List of None if invalid
        """
        return_list = [None]
        if attribute == 'right':
            return_list = self.right
        if attribute == 'wrong':
            return_list = self.wrong
        if attribute == 'skip':
            return_list = self.skip
        return return_list

    def prompt_list(self, question_list, **kwargs):
        """
        Prompt the user with the questions in the list submitted.

        Warning: If submitting the list of right questions this will go on forever.
        """
        try:
            while len(question_list) != 0:
                self.question = question_list.pop(0)
                self.question.prompt(**kwargs)
                self.score()
        except KeyboardInterrupt:
            print('')
            self.score()

    def review_wrong(self):
        """
        Review questions that the user got wrong.
        """
        while len(self.get("wrong")) > 0 or len(self.get("skip")) > 0:
            answer = 'x'
            while answer.lower() not in ['y', 'n']:
                answer = raw_input("Would you like review the questions you got wrong? (Y/N)>")
            print("")
            if answer.lower() == "y":
                self.prompt_list(self.get('wrong'), visualize=True)
                if len(self.skip) > 0:
                    print("Returned to skipped questions!")
                    self.prompt_list(self.get('skip'), visualize=True)
                    self.move_skipped_to_wrong()
            else:
                return

    def _move_skipped_to_wrong(self):
        """
        Move skipped questions to wrong.
        :return:
        """
        while len(self.skip) > 0:
            self.wrong.append(self.skip.pop(0))

    def _total_possible_questions(self, **kwargs):
        return len(self._all_questions(**kwargs))

    def _all_questions(self, **kwargs):
        all_questions = []
        operation_ranges = {
            "*": [(0, 9+1), (0, 9+1)],
            "/": [(0, 9+1), (1, 9+1)],
            "+": [(0, 19+1), (0, 19+1)],
            "-": [(4, 19+1), (0, "first_number")],
        }

        operators = kwargs.get("operator", self.question.valid_operators)
        custom_first_number = kwargs.get('first_number')
        custom_second_number = kwargs.get('second_number')
        for operator in operators:
            if custom_first_number is not None:
                operation_ranges[operator][0] = (custom_first_number, custom_first_number+1)
            if custom_second_number is not None:
                operation_ranges[operator][1] = (custom_second_number, custom_second_number+1)
            first_range = operation_ranges[operator][0]
            for first_number in range(*first_range):
                # if operator is subtraction, only generate equations with positive results
                if operator == '-':
                    second_range = (operation_ranges[operator][1][0], first_number+1)
                else:
                    second_range = operation_ranges[operator][1]
                for second_number in range(*second_range):
                    if operator == '/':
                        first_number_value = first_number * second_number
                    else:
                        first_number_value = first_number
                    all_questions.append(
                        Question(
                            first_number=first_number_value,
                            second_number=second_number,
                            operator=operator,
                            valid_operators=kwargs.get("valid_operators", Question().valid_operators)
                        )
                    )
        return all_questions

    def run(self, **kwargs):
        """
        Run the test by prompting user, scoring the answer, and finally displaying the score.
        :param questions: Optional number of questions to ask.  Default 25.
        :param unique: Optional Boolean to generate unique, one of a kind questions.
        :param kwargs: keyword arguments to pass Question.prompt and display_score.
        :return:
        """
        all_questions = []  # all possible questions, only generated if this is unique
        number_of_questions = kwargs.get("questions", 25)
        question_number = 0
        while question_number < number_of_questions:
            try:
                if kwargs.get("unique"):
                    # if we haven't generated the whole list
                    # will also run if we finished the old list
                    if len(all_questions) == 0:
                        all_questions = self._all_questions(**kwargs)
                    self.question = all_questions.pop(randint(0, len(all_questions)-1))
                else:
                    self.question.generate_rand_question(**kwargs)
                print("Question {} of {}:".format(question_number+1, number_of_questions))
                self.question.prompt(**kwargs)
            except ZeroDivisionError:
                if kwargs.get("operator") == '/' and kwargs.get("second_number") == 0:
                    # user chose an impossible situation
                    print("Your settings will always divide by zero.  Exiting.")
                    if __name__ == '__main__':
                        exit(0)
                    else:
                        return
                else:
                    # there's still a chance!
                    continue
            self.score()
            question_number += 1
        if len(self.skip) > 0:
            print("Returned to skipped questions!")
            self.prompt_list(self.get('skip'), **kwargs)
            self._move_skipped_to_wrong()
        self.display_score(**kwargs)
        if len(self.get("wrong")) > 0 or len(self.get("skip")) > 0:
            try:
                self.review_wrong()
            except KeyboardInterrupt:
                raise
            finally:
                self.display_score(**kwargs)


def arg_parse():
    def assign_if_greater_than_0(value):
        value = int(value)
        if value > 0:
            return value
        else:
            raise ValueError

    def interactive_operators():
        question = Question()
        words = {
            "+": "addition",
            "-": "subtraction",
            "*": "multiplication",
            "/": "division",
        }
        operator_list = ''

        for op in question.valid_operators:
            answer = 'x'
            while answer.lower() not in ['y', 'n', '']:
                answer = raw_input("Would you like to do {}? (Y/N)>".format(words[op]))
            if answer.lower() == 'y':
                operator_list += op

        if len(operator_list) == 0:
            print("You didn't select any operators!  Try again...")
            return interactive_operators()

        return operator_list

    def interactive_visualize():
        answer = 'x'
        while answer.lower() not in ['y', 'n', '']:
            answer = raw_input("Would you like a visualization of the questions? (Y/N)>")
        return answer.lower() == 'y'

    def interactive_questions():
        try:
            questions = raw_input("How many questions would you like on the test?>")
            if questions == '':
                print("Using default of 25 questions.")
                return 25
            return assign_if_greater_than_0(questions)
        except ValueError:
            print("Invalid input! Please enter a number greater than 0.")
            return interactive_questions()

    parser = argparse.ArgumentParser(description="Math Test. Choose what kind of math problems and how many.")
    parser.add_argument("-i", "--interactive", action='store_true',
                        help="Interactively set options before starting the test.")
    parser.add_argument("-v", "--visualize", action='store_true',
                        help="Show visualization of equation.")
    parser.add_argument("-u", "--unique", action='store_true',
                        help="Only unique questions; don't repeat unless necessary.")
    parser.add_argument("-o", "--operator", help="Type of questions (+ - * /). No spaces if multiple.",
                        metavar="OPERATOR or OPERATORS")
    parser.add_argument("-q", "--questions", help="Number of questions.")
    parser.add_argument("-n", "--constant-number", help="Constant number for every question.",
                        metavar="NUMBER")
    parser.add_argument("-c", "--columns", help="Number of columns to print when the test score is displayed.")
    args = parser.parse_args()
    kwargs = dict()
    if args.interactive:
        args.operator = args.operator or interactive_operators()
        args.questions = args.questions or interactive_questions()
        args.visualize = args.visualize or interactive_visualize()
    if args.operator:
        question = Question()
        if len(args.operator) == 1 and args.operator in question.valid_operators:
            kwargs["operator"] = args.operator
        elif len(args.operator) > 1:
            for operator in args.operator:
                if operator not in question.valid_operators:
                    print("{} is not a valid operator!".format(operator))
                    print("Valid operators are {}.".format(question.valid_operators))
                    exit(3)
            kwargs["valid_operators"] = [x for x in args.operator]
            kwargs.pop("operator", None)
        else:
            print("'{}' is an invalid operator!".format(args.operator))
            print("Valid operators are: {}".format(question.valid_operators))
            exit(1)
    if args.questions:
        try:
            kwargs["questions"] = assign_if_greater_than_0(args.questions)
        except ValueError:
            print("--questions must be a number greater than 0!")
            exit(2)
    if args.constant_number:
        try:
            kwargs["second_number"] = int(args.constant_number)
        except ValueError:
            print("--constant-number must be a number!")
            exit(3)
    if args.columns:
        try:
            kwargs["columns"] = assign_if_greater_than_0(args.columns)
        except ValueError:
            print("--columns must be a number greater than 0!")
            exit(4)
    kwargs["visualize"] = args.visualize
    kwargs["unique"] = args.unique
    return kwargs


def main():
    try:
        kwargs = arg_parse()
    except KeyboardInterrupt:
        exit(0)
    start = int(time())
    try:
        test = Test(**kwargs)
        test.run(**kwargs)
    except KeyboardInterrupt:
        test.display_score(**kwargs)
    end = int(time())
    total_time = end - start

    print("Total time was:  {}:{:0>2}".format(int(total_time / 60), int(total_time % 60)))
    print("Percentage:      {:0.2f}%".format(test.grade))

    return 0


if __name__ == '__main__':
    main()
