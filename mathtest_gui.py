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
import mathtest
import os
import sys
from pprint import pprint

if sys.version_info.major == 2:
    from Tkinter import *
    import tkMessageBox as messagebox
    if os.name == 'nt':
        operator_translation = {ord('*'): u"x", ord('/'): u"÷"}
    else:
        operator_translation = {ord('*'): u"×", ord('/'): u"÷"}
else:
    from tkinter import *
    from tkinter import messagebox
    raw_input = input
    unicode = str
    operator_translation = str.maketrans("*/", "×÷")


class Dialog(Toplevel):
    def __init__(self, parent, title=None, window_x=None, window_y=None):

        Toplevel.__init__(self, parent)
        self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent

        self.result = None

        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+{}+{}".format(window_x-8 if window_x is not None else (parent.winfo_rootx() + 50),
                                      window_y-31 if window_y is not None else (parent.winfo_rooty() + 50)))

        self.initial_focus.focus_set()

        self.wait_window(self)

    #
    # construction hooks

    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden

        pass

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = Frame(self)

        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    #
    # standard button semantics

    def ok(self, event=None):

        if not self.validate():
            self.initial_focus.focus_set()  # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()

        self.cancel()

    def cancel(self, event=None):

        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    #
    # command hooks

    def validate(self):

        return 1  # override

    def apply(self):

        pass  # override


class QuestionWindow(Dialog):
    e1 = None
    still_going = True

    def __init__(self, parent, **kwargs):
        self.question = kwargs.get("question")
        self.visualize = kwargs.get("visualize", False)
        self.window_x = kwargs.get("window_x")
        self.window_y = kwargs.get("window_y")

        if sys.version_info.major == 3:
            super(QuestionWindow, self).__init__(parent, title=kwargs.get('title'),
                                                 window_x=self.window_x,
                                                 window_y=self.window_y)
        else:
            Dialog.__init__(self, parent, title=kwargs.get('title'),
                            window_x=self.window_x,
                            window_y=self.window_y)

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = Frame(self)
        box.pack()
        bottom = Frame(self)
        bottom.pack(side=BOTTOM)

        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Skip", width=10, command=self.skip)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(bottom, text="Exit", width=20, command=self.cancel)
        w.pack(side=BOTTOM)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.skip)

        box.pack()

    def body(self, master):
        if self.visualize:
            var = StringVar()
            visualize_string = self.question.visualize_string()
            var.set(visualize_string)
            # get longest line of string for width
            var_width = sorted([len(x) for x in visualize_string.split('\n')], reverse=True)[0]
            Message(master,
                    textvariable=var,
                    relief=GROOVE,
                    font=('courier new', 12),
                    width=var_width * 12).grid(row=0, columnspan=2)

        Label(
            master,
            text=" {:>2}".format(self.question.first_number),
            font=('courier new', 12)
        ).grid(row=1, column=1, sticky='w')
        Label(
            master,
            text=u"{}{:>2}".format(
                unicode(self.question.operator).translate(operator_translation),
                self.question.second_number),
            font=('courier new', 12)
        ).grid(row=2, column=1, sticky='w')

        Label(master, text="Answer:").grid(row=3, sticky='w')

        self.e1 = Entry(master, width=5, justify=RIGHT)

        self.e1.grid(row=3, column=1, sticky='w')
        self.e1.focus_set()

    def apply(self):
        try:
            entry = self.e1.get()
            if entry != '':
                entry = int(entry)
            self.question.user_answer = entry
        except ValueError:
            messagebox.showwarning(
                "Bad input",
                "Illegal values, please try again"
            )
            self.question.user_answer = None

    def validate(self):
        """
        Validates that the entry is only a blank or an integer
        :return: Boolean
        """
        try:
            int(self.e1.get())
            return True
        except ValueError:
            return self.e1.get() == ''

    def ok(self, event=None):

        if not self.validate():
            messagebox.showwarning(
                "Bad input",
                "Illegal values, please try again"
            )
            self.e1.select_range(0, len(self.e1.get()))
            self.e1.focus_set()  # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()
        self.parent.focus_set()
        self.window_x = self.winfo_rootx()
        self.window_y = self.winfo_rooty()
        self.destroy()

    def skip(self, event=None):
        self.question.user_answer = ''
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    def cancel(self, event=None):
        # put focus back to the parent window
        self.still_going = False
        self.parent.focus_set()
        self.destroy()


class OptionWindow(Dialog):
    def __init__(self, parent, in_kwargs, *args, **kwargs):
        self.parent = parent
        self.kwargs = {}
        self.division = BooleanVar(value='/' in in_kwargs.get('valid_operators', ['/']))
        self.multiplication = BooleanVar(value='*' in in_kwargs.get('valid_operators', ['*']))
        self.addition = BooleanVar(value='+' in in_kwargs.get('valid_operators', ['+']))
        self.subtraction = BooleanVar(value='-' in in_kwargs.get('valid_operators', ['-']))
        self.visualize = BooleanVar(value=in_kwargs.get('visualize', False))
        self.questions = in_kwargs.get('questions', 25)
        self.questions_entry = None
        if sys.version_info.major == 3:
            super(OptionWindow, self).__init__(parent, title="Math Test Options")
        else:
            Dialog.__init__(self, parent, title="Math Test Options")

    def body(self, master):
        row = 0

        division_button = Checkbutton(master, text="Division", variable=self.division, onvalue=True, offvalue=False)
        multiplication_button = Checkbutton(master, text="Multiplication", variable=self.multiplication, onvalue=True,
                                            offvalue=False)
        addition_button = Checkbutton(master, text="Addition", variable=self.addition, onvalue=True, offvalue=False)
        subtraction_button = Checkbutton(master, text="Subtraction", variable=self.subtraction, onvalue=True,
                                         offvalue=False)
        visualize_button = Checkbutton(master, text="Visualize", variable=self.visualize, onvalue=True, offvalue=False)

        division_button.grid(row=row, sticky='w')
        row += 1
        # division_button.select()
        multiplication_button.grid(row=row, sticky='w')
        row += 1
        # multiplication_button.select()
        addition_button.grid(row=row, sticky='w')
        row += 1
        # addition_button.select()
        subtraction_button.grid(row=row, sticky='w')
        row += 1
        # subtraction_button.select()

        visualize_button.grid(row=row, sticky='w', pady=10)
        row += 1

        Label(master, text="Questions:").grid(row=row, sticky='w', pady=10)
        row += 1

        self.questions_entry = Entry(master)
        self.questions_entry.insert(0, '25')

        self.questions_entry.grid(row=5, column=1, sticky='w')
        division_button.focus_set()

    def buttonbox(self):
        box = Frame(self)
        box.pack()

        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    def validate(self):
        """
        Validates that the entry is only a blank or an integer
        :return: Boolean
        """
        try:
            int(self.questions_entry.get())
            return True
        except ValueError:
            return self.questions_entry.get() == ''

    def ok(self, event=None):
        if not self.validate():
            messagebox.showwarning(
                "Bad input",
                "Illegal values, please try again"
            )
            self.questions_entry.select_range(0, len(self.questions_entry.get()))
            self.questions_entry.focus_set()  # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()
        self.parent.focus_set()
        self.destroy()

    def cancel(self, event=None):
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    def apply(self):
        kwargs = dict(unique=True)
        kwargs['valid_operators'] = []
        if self.division.get():
            kwargs['valid_operators'].append('/')
        if self.multiplication.get():
            kwargs['valid_operators'].append('*')
        if self.addition.get():
            kwargs['valid_operators'].append('+')
        if self.subtraction.get():
            kwargs['valid_operators'].append('-')

        kwargs['visualize'] = self.visualize.get()

        questions = self.questions_entry.get()

        if questions != '':
            try:
                kwargs['questions'] = int(questions)
            except ValueError:
                pass

        self.kwargs = kwargs


class TestGUI(Tk):
    def __init__(self, *args, **kwargs):
        if sys.version_info.major == 3:
            super(TestGUI, self).__init__(*args, **kwargs)
        else:
            Tk.__init__(self, *args, **kwargs)
        self.question_x = None
        self.question_y = None
        self.title("Math Test")
        self.display_string = StringVar()
        self.message = Message(self,
                               textvariable=self.display_string,
                               relief=RAISED,
                               font=('courier new', 12),
                               width=80*12)
        self.test = mathtest.Test()
        self.still_going = True

    def get_options(self, **kwargs):
        """
        Prompt the user with available options
        :param kwargs: Dictionary of incoming settings
        :return: Dictionary of settings
        """
        option_window = OptionWindow(self, kwargs)
        return option_window.kwargs

    def update_display(self, **kwargs):
        """
        Redraw the scoreboard with current information.
        :return:
        """
        final_grade = kwargs.get('final_grade', False)
        if final_grade:
            self.display_string.set(
                self.test.display_string(**kwargs) + '\nFinal Score: {:0.2f}%'.format(self.test.grade)
            )
        else:
            self.display_string.set(self.test.display_string(**kwargs))
        self.message.pack()
        self.update()

    def _post_question(self, q, score=False, **kwargs):
        self.still_going = q.still_going
        self.question_x = q.window_x
        self.question_y = q.window_y
        if score:
            self.test.score()
            self.update_display(**kwargs)

    def run_new_questions(self, **kwargs):
        """
        Get new questions based off of elements in kwargs and prompt the user.
        """
        for question_number, question in self.test.get_questions(**kwargs):
            kwargs.update(dict(window_x=self.question_x))
            kwargs.update(dict(window_y=self.question_y))
            q = QuestionWindow(
                self, question=question, title="Question {} of {}".format(
                    question_number+1,
                    kwargs.get("questions", 25),
                ),
                **kwargs)
            self._post_question(q)
            if not self.still_going:
                break
            self.test.score()
            self.update_display(**kwargs)

    def run_skipped_questions(self, **kwargs):
        """
        Prompt user with skipped questions. If the user elects to stop it will move remaining questions to wrong.
        """
        for question in self.test.question_list(self.test.get("skip")):
            kwargs.update(dict(window_x=self.question_x))
            kwargs.update(dict(window_y=self.question_y))
            if self.still_going:
                q = QuestionWindow(self, question=question, title="Skipped Question", **kwargs)
                self._post_question(q, score=True, **kwargs)
            else:
                self.test.wrong.append(question)

    def run_wrong_questions(self, **kwargs):
        """
        Prompt user with questions from the wrong list. The user can elect to stop.
        """
        kwargs.update(visualize=True)
        while len(self.test.wrong) > 0:
            for question in self.test.question_list(self.test.get('wrong')):
                kwargs.update(dict(window_x=self.question_x))
                kwargs.update(dict(window_y=self.question_y))
                if self.still_going:
                    q = QuestionWindow(self, question=question, title="Skipped Question", **kwargs)
                    self._post_question(q, score=True, **kwargs)
                else:
                    self.test.wrong.append(question)
                    return

    def end_test(self):
        """
        Update display for the final time, revealing correct answers to missed questions.
        :return:
        """
        self.update_display(showing_answers=True, final_grade=True)
        self.mainloop()


def main():
    kwargs = mathtest.arg_parse()
    test = TestGUI()
    test.update_display(**kwargs)
    kwargs = test.get_options(**kwargs)
    test.run_new_questions(**kwargs)

    if len(test.test.get('skip')) and not test.still_going:
        test.still_going = messagebox.askyesno(title="Review", message="Review questions you skipped?")

    while len(test.test.get("skip")) > 0:
        test.run_skipped_questions(**kwargs)

    test.update_display(**kwargs)

    if len(test.test.wrong) > 0:
        test.still_going = messagebox.askyesno(title="Review", message="Retry questions you got wrong?")
    kwargs['visualize'] = True
    while len(test.test.get("skip") + test.test.get("wrong")) > 0 and test.still_going:
        test.run_wrong_questions(visualize=True)
        test.run_skipped_questions(visualize=True)

    test.end_test()


if __name__ == '__main__':
    main()
