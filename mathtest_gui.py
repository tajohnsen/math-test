from tkinter import *
from tkinter import messagebox
from pprint import pprint
import mathtest
import os

if sys.version_info.major == 2:
    if os.name == 'nt':
        operator_translation = {ord('*'): u"x", ord('/'): u"÷"}
    else:
        operator_translation = {ord('*'): u"×", ord('/'): u"÷"}
else:
    raw_input = input
    unicode = str
    operator_translation = str.maketrans("*/", "×÷")


class Dialog(Toplevel):
    def __init__(self, parent, title=None):

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

        self.geometry("+%d+%d" % (parent.winfo_rootx() + 50,
                                  parent.winfo_rooty() + 50))

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
        w = Button(box, text="Skip", width=10, command=self.cancel)
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
        super(QuestionWindow, self).__init__(parent, title=kwargs.get('title'))

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
            message = Message(master,
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
            text="{}{:>2}".format(self.question.operator.translate(operator_translation), self.question.second_number),
            font=('courier new', 12)
        ).grid(row=2, column=1, sticky='w')

        Label(master, text="Answer:").grid(row=3, sticky='w')

        self.e1 = Entry(master, width=5)

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

    def ok(self, event=None):

        if not self.validate():
            self.initial_focus.focus_set()  # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()
        self.parent.focus_set()
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


class TestGUI(Tk):
    def __init__(self, *args, **kwargs):
        super(TestGUI, self).__init__(*args, **kwargs)
        self.title("Math Test")
        self.display_string = StringVar()
        self.message = Message(self,
                               textvariable=self.display_string,
                               relief=RAISED,
                               font=('courier new', 12),
                               width=80*12)
        self.test = mathtest.Test()
        self.still_going = True

    def update_display(self, **kwargs):
        final_grade = kwargs.get('final_grade', False)
        if final_grade:
            self.display_string.set(
                self.test.display_string(**kwargs) + '\nFinal Score: {:0.2f}%'.format(self.test.grade)
            )
        else:
            self.display_string.set(self.test.display_string(**kwargs))
        self.message.pack()
        self.update()

    def run_new_questions(self, **kwargs):
        for question_number, question in self.test.get_questions(**kwargs):
            q = QuestionWindow(
                self, question=question, title="Question {} of {}".format(
                    question_number+1,
                    kwargs.get("questions", 25)
                ),
                **kwargs)
            self.still_going = q.still_going
            if not self.still_going:
                break
            self.test.score()
            self.update_display(**kwargs)

    def run_skipped_questions(self, **kwargs):
        for question in self.test.question_list(self.test.get("skip")):
            if self.still_going:
                q = QuestionWindow(self, question=question, title="Skipped Question", **kwargs)
                self.still_going = q.still_going
                self.test.score()
                self.update_display(**kwargs)
            else:
                self.test.wrong.append(question)

    def run_wrong_questions(self, **kwargs):
        while len(self.test.wrong) > 0:
            for question in self.test.question_list(self.test.get('wrong')):
                if self.still_going:
                    q = QuestionWindow(self, question=question, title="Skipped Question", visualize=True)
                    self.test.score()
                    self.update_display(**kwargs)
                    self.still_going = q.still_going
                else:
                    self.test.wrong.append(question)
                    break

    def end_test(self):
        self.update_display(showing_answers=True, final_grade=True)
        self.mainloop()


def main():
    kwargs = mathtest.arg_parse()
    test = TestGUI()
    test.update_display(**kwargs)
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
