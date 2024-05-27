import dataclasses
import os
from collections import defaultdict
from typing import TYPE_CHECKING, Dict, Iterable, List, Optional

import expurtka.putka.config.settings as settings
from django.db.models import F, Q
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from django.utils.functional import _StrOrPromise as StrOrPromise
    from expurtka.putka.models.results import TestCase
    from expurtka.putka.models.tasks import Task

# Local abbreviations for readability.
PL = settings.PROG_LANGS
US = settings.UPLOAD_STATUS
JRS = settings.JAILRUN_STATUS


EXTENSION_LANG_MAPPING = {
    ".txt": PL.txt,
    ".c": PL.c,
    ".cpp": PL.cpp,
    ".pas": PL.pas,
    ".java": PL.java,
    ".py": PL.py3,
    ".perl": PL.perl,
    ".cs": PL.cs,
    ".prolog": PL.prolog,
    ".rb": PL.rb,
    ".rs": PL.rust,
    ".kt": PL.kotlin,
    ".go": PL.go,
}


UPLOAD_STATUS_ICON: Dict[int, Optional[str]] = {
    US.waiting: "fa-clock",
    US.testing: "fa-stopwatch",
    US.done: None,  # overridden with aggregate details
    US.error: "fa-skull-crossbones",
    US.manual: "fa-hand-paper",
}
assert set(UPLOAD_STATUS_ICON) == set(
    US
), f"Mismatched keys: {set(UPLOAD_STATUS_ICON)} vs. {set(US)}"


UPLOAD_STATUS_MEANINGS: Dict[int, "StrOrPromise"] = {
    US.waiting: _(
        "The submission is waiting in the evaluation queue for a free tester."
    ),
    US.testing: _("The submission is being evaluated on the official test cases."),
    US.done: _(
        "The submission has been evaluated successfully. The result of the evaluation (e.g. WA, TLE, OK) with the "
        "corresponding icon is reported to the user. See the next section for more explanation."
    ),
    US.error: _(
        "There was an internal error during the evaluation, and the submission could not be evaluated. "
        "Please alert the judge team so that they can fix the problem and reevaluate the submission."
    ),
    US.manual: _(
        "The submission has been evaluated, but is waiting for manual inspection from the "
        "judges. This can happen because the system detected suspicious behaviour. "
        "The judges will manually judge the solution, and the status of your submission should change to "
        "e.g. RTE. If the manual status persists, please alert the judges."
    ),
}
assert set(UPLOAD_STATUS_MEANINGS) == set(
    US
), f"Mismatched keys: {set(UPLOAD_STATUS_MEANINGS)} vs. {set(US)}"


JAILRUN_STATUS_ICON: Dict[int, str] = {
    JRS.OK: "fa-check",
    JRS.RTE: "fa-times",
    JRS.TLE: "fa-times",
    JRS.MLE: "fa-times",
    JRS.OUT: "fa-times",
    JRS.THR: "fa-times",
    JRS.SYS: "fa-times",
    JRS.EXT: "fa-times",
    JRS.WA: "fa-times",
    JRS.PE: "fa-presentation-error",
}
assert set(JAILRUN_STATUS_ICON) == set(
    JRS
), f"Mismatched keys: {set(JAILRUN_STATUS_ICON)} vs. {set(JRS)}"


JAILRUN_STATUS_MEANINGS = {
    # TODO: how is trailing whitespace handled?
    JRS.OK: _(
        "The solution is correct. Full points are awarded for this task. Depending on the contest type, deductions "
        "for multiple submissions are possible. The judge system is usually relatively lenient with whitespace: "
        "an extra space or tab just before the newline is allowed. Also, the number of newlines at end of file "
        "does not matter. Note that this may be different for specific tasks."
    ),
    JRS.RTE: _(
        "The program crashed during evaluation. This includes e.g. segmentation faults in C++, exceptions "
        "in Java and Python, and many other possible reasons."
    ),
    JRS.TLE: _(
        "The program did not finish in the allotted time and was terminated. If the time limit was 3s, "
        "the reported execution time might be 3.1s. This does not mean that your solution finished only "
        "slightly after the time limit and that it will pass after minor optimizations; it only means that it was "
        "terminated after it exceeded the time limit. To determine how long your solution actually takes, you might be "
        "able to download the test cases after the contest, run it on your computer, and use the 'Custom test' facility to "
        "estimate the difference in execution speed between your computer and the evaluation system."
    ),
    JRS.MLE: _(
        "The program tried to allocate more memory than allowed. Similarly as execution time, if the memory "
        "limit was 256 MB and the reported usage is 270 MB, this does not mean that your program only just went "
        "over the memory limit and otherwise ran successfully; instead it means that it was terminated as soon as "
        "the limit was reached. Also note that hitting the memory limit often manifests as a program crash, which "
        "will be reported as RTE."
    ),
    # TODO: what are the output and thread limits
    JRS.OUT: _(
        "The program produced too much output (stdout or stderr), and was terminated. The usual limit is 100 MB."
    ),
    JRS.THR: _(
        "The program spawned too many threads or processes, and was terminated. The usual limit is 1 thread."
    ),
    JRS.SYS: _(
        "The program attempted a disallowed system call and was terminated. This means that your program attempted to "
        "e.g. open a file, connect to the network, or shut down the judge system. Note that some illegal calls may "
        "also happen as the program crashes and the language's runtime tries to do some crash handling. If you did not "
        "do anything forbidden, you can safely treat this as an RTE. If you called a forbidden function accidentally, "
        "fix the problem and treat the result as an RTE. However, if the judges decide your code had malicious intent, "
        "this may warrant disqualification."
    ),
    JRS.EXT: _(
        "The program finished with a non-zero exit code. Make sure you have <code>return 0</code> in your C / C++ code."
    ),
    JRS.WA: _(
        "The program finished successfully, but the output produced was not entirely correct."
    ),
    JRS.PE: _(
        "This is a special version of the WA result. The output of your program and the official output differ only in "
        "whitespace. An example of this is when the correct output has all answers on a single line, but your program "
        "printed the (otherwise correct) answers each on its own line. The task is not considered solved, "
        "and the solution must be fixed and resubmitted."
    ),
}
assert set(JAILRUN_STATUS_MEANINGS) == set(
    JRS
), f"Mismatched keys: {set(JAILRUN_STATUS_MEANINGS)} vs. {set(JRS)}"


COMPILE_ERROR_ICON = "fa-exclamation-circle"
COMPILE_ERROR_TEXT = _("Compile error")
# TODO: compilation limits
COMPILE_ERROR_MEANING = _(
    "This error means that the program could not even be compiled. A compile error can be e.g. a syntax error in Python, "
    "a compile or link error in C++, a compile error in Java, etc. It can also mean that the compiler ran out of "
    "memory, took too long to compile, or crashed during compilation. Currently the compile time limit is 30s "
    "and there is no additional memory limit. "
)

PARTIAL_POINTS_ICON = "fa-exclamation-triangle"
PARTIAL_POINTS_MEANING = _(
    "If the contest type allows it, partial points may be awarded. This is the icon you will see if you get non-zero "
    "amount of points, but not all the points. The status can be any of the statuses of the not OK individual test cases."
)


def lang_from_extension(lang: int, name: str) -> Optional[int]:
    if lang == PL.auto:
        _, ext = os.path.splitext(name)
        return EXTENSION_LANG_MAPPING.get(ext)
    return lang


_RTE_MASKED = (JRS.OUT, JRS.THR, JRS.SYS, JRS.EXT, JRS.MLE)


def mask_agg_status(agg_status: int, *, is_staff: bool) -> int:
    """Mask a settings.JAILRUN_STATUS to a less specific value for non-staff users."""
    if is_staff:
        return agg_status
    if not settings.JAILRUN_DETAILS and agg_status in _RTE_MASKED:
        return JRS.RTE
    if not settings.PRESENTATION_ERRORS and agg_status == JRS.PE:
        return JRS.WA
    return agg_status


def unmask_agg_status(agg_status: int, *, is_staff: bool) -> Iterable[int]:
    """Return a list of all statuses that would mask to a give status.

    This is the preimage of `mask_agg_status`.
    """
    if is_staff:
        return (agg_status,)
    if not settings.JAILRUN_DETAILS and agg_status == JRS.RTE:
        return (JRS.RTE,) + _RTE_MASKED
    if not settings.JAILRUN_DETAILS and agg_status in _RTE_MASKED:
        return ()
    if not settings.PRESENTATION_ERRORS and agg_status == JRS.WA:
        return (JRS.WA, JRS.PE)
    if not settings.PRESENTATION_ERRORS and agg_status == JRS.PE:
        return ()
    return (agg_status,)


def upload_solved_q_expr(prefix: str = "") -> Q:
    """Return a Q expression defining when an upload is solved."""
    return Q(
        **{
            f"{prefix}status": settings.UPLOAD_STATUS.done,
            f"{prefix}preparation_status": settings.JAILRUN_STATUS.OK,
            f"{prefix}agg_status": settings.JAILRUN_STATUS.OK,
            f"{prefix}points": F(f"{prefix}max_points"),
        }
    )


@dataclasses.dataclass(slots=True)
class SubtaskDetails:
    max_points: int
    status: int
    test_cases: List["TestCase"]
    points: int = 0
    icon: str = ""

    def __post_init__(self):
        self.points = (
            self.max_points if self.status == settings.JAILRUN_STATUS.OK else 0
        )
        self.icon = "fa-check" if self.points == self.max_points else "fa-times"


def _extract_subtask(test_case_name: str) -> Optional[str]:
    try:
        return test_case_name.split(".")[-3]
    except IndexError:
        return None


# XXX hacked subtask display. A more proper solution would be for the backend to set a proper field in
# the test case model. This only works for subtasks of a specific format and with acm aggregation functions.
def maybe_split_into_subtasks(
    task: "Task", test_cases: List["TestCase"]
) -> Optional[List[SubtaskDetails]]:
    """Return a list of test cases, one for each subtask."""
    subtask_info = task.subtask_info()
    if not subtask_info:
        return None

    subtasks: Dict[str, List["TestCase"]] = defaultdict(list)
    for test_case in test_cases:
        subtask = _extract_subtask(test_case.name)
        if not subtask:
            return None
        subtasks[subtask].append(test_case)

    if len(subtasks) != len(subtask_info):
        return None

    def aggregate_statuses(ts: List["TestCase"]) -> Optional[int]:
        for t in ts:
            if t.status() != settings.JAILRUN_STATUS.OK:
                return t.status()
        return settings.JAILRUN_STATUS.OK

    return [
        SubtaskDetails(
            # Fail also in case any test cases have null status.
            status=aggregate_statuses(test_cases) or settings.JAILRUN_STATUS.WA,
            max_points=max_points,
            test_cases=test_cases,
        )
        for max_points, test_cases in zip(subtask_info, subtasks.values())
    ]
