"""Enums used across the site."""
from typing import TYPE_CHECKING, Callable, Dict, Type

from django.db.models.enums import IntegerChoices, TextChoices

if TYPE_CHECKING:
	from django.utils.functional import StrPromise
	_: Callable[[str], StrPromise]
else:
	from django.utils.translation import gettext_lazy as _

#
# Putka static config - global enums; do you REALLY need to change anything here?
#

# NOTE: When editing enums, it's OK to change the description. Changing the key (first value)
# likely requires database changes.

class PROG_LANGS_(IntegerChoices):
	auto = 100, '(Auto)'
	txt = 0, 'text'
	c = 1, 'C'
	cpp = 2, 'C++'
	pas = 3, 'Pascal'
	java = 4, 'Java'
	py_noauto = 5, 'Python 2'  # Obsolete and unsupported.
	py3 = 8, 'Py 3'
	perl = 6, 'Perl'
	cs = 7, 'C#'
	prolog = 9, 'Prolog (SWI)'
	rb = 10, 'Ruby'
	rust = 11, 'Rust'
	kotlin = 12, 'Kotlin'
	go = 13, 'Go'

PROG_LANGS: Type[PROG_LANGS_] = PROG_LANGS_


IS_LANG_ACTUALLY_SUPPORTED: Dict[int, bool] = {
	PROG_LANGS.auto: True,
	PROG_LANGS.txt: True,
	PROG_LANGS.c: True,
	PROG_LANGS.cpp: True,
	PROG_LANGS.pas: True,
	PROG_LANGS.java: True,
	PROG_LANGS.py_noauto: False,
	PROG_LANGS.py3: True,
	PROG_LANGS.perl: False,
	PROG_LANGS.cs: True,
	PROG_LANGS.prolog: False,
	PROG_LANGS.rb: False,
	PROG_LANGS.rust: True,
	PROG_LANGS.kotlin: True,
	PROG_LANGS.go: True,
}
assert set(IS_LANG_ACTUALLY_SUPPORTED) == set(PROG_LANGS), f"Mismatch: {set(IS_LANG_ACTUALLY_SUPPORTED)} vs. {set(PROG_LANGS)}"


class ATT_TYPE_(IntegerChoices):
	# testing-related (for editors only)
	generic_secret = -3, _('Helper files for testing')
	inout_secret = -2, _('Test inputs/outputs')
	# testscript = -1,  'Test script' # is now a field in Task
	# content-related (public)
	# solution = 1, _('Solutions') # Uploads are now marked as solutions.
	image = 2, _('Images')
	inout_public = 3, _('Sample inputs/outputs')
	generic_public = 4, _('Other public data')

ATT_TYPE: Type[ATT_TYPE_] = ATT_TYPE_


class UPLOAD_STATUS_(IntegerChoices):
	waiting = 1, _('Waiting')
	testing = 2, _('Testing')
	done = 3, _('Done')
	error = 4, _('Internal error')
	manual = 5, _('Manual Inspection')

UPLOAD_STATUS: Type[UPLOAD_STATUS_] = UPLOAD_STATUS_


# !!! AN EXACT COPY OF THIS LIST MUST BE KEPT IN tester/lib/t_utils.py !!!
class JAILRUN_STATUS_(IntegerChoices):
	"""Result of a single testcase *or* the whole upload."""

	OK = 1, _('OK')
	RTE = 2, _('Exit/RunTime Error')
	TLE = 3, _('Time Limit Exceeded')
	MLE = 4, _('Memory Limit Exceeded')
	OUT = 5, _('Output Size Limit Exceeded')
	THR = 6, _('Thread Count Limit Exceeded')
	SYS = 7, _('Illegal System Call')
	EXT = 8, _('Nonzero Exit Code')
	WA = 9, _('Wrong Answer')
	PE = 10, _('Presentation Error')

JAILRUN_STATUS: Type[JAILRUN_STATUS_] = JAILRUN_STATUS_


class MANAGER_RESPONSE_(IntegerChoices):
	OK = 1, _('OK')
	EIMP = 2, _('Not implemented.')
	EVER = 3, _('Unsupported protocol version.')
	EFAIL = 4, _('Command failed.')
	EMOD = 5, _('Requested manager module does not exist.')
	EFUNC = 6, _('Requested function does not exist.')
	NO_ANSWER = 7, _('No response.')

MANAGER_RESPONSE: Type[MANAGER_RESPONSE_] = MANAGER_RESPONSE_


# user preferences about notifications about new posts
class FORUM_NOTIFY_(IntegerChoices):
	# choices are strictly monotonic: a larger id matches all posts which match a lower id
	never = 0, _('Never.')
	recent_active = 1, _('On new posts in threads in which I recently posted myself.')
	recent_passive = 2, _('On new posts addressed to me and on new posts in threads about tasks I recently attempted, threads about tasks from my recent contests, and threads in which I recently posted.')
	always = 100, _('On every new post.')

FORUM_NOTIFY: Type[FORUM_NOTIFY_] = FORUM_NOTIFY_


class THREAD_TYPES_(TextChoices):
	general = 'g', _('General thread')
	task = 't', _('Task thread')
	contest = 'c', _('Contest thread')

THREAD_TYPES: Type[THREAD_TYPES_] = THREAD_TYPES_


class CONTEST_STATE_(IntegerChoices):
	upcoming = 1, _('upcoming')
	ongoing = 2, _('ongoing')
	finished = 3, _('finished')
	published = 4, _('published')

CONTEST_STATE: Type[CONTEST_STATE_] = CONTEST_STATE_


class CONTEST_SCORING_TYPES_(IntegerChoices):
	CLASSIC = 1, 'Putka Classic'
	UPM = 2, 'UPM'
	RTK = 3, 'RTK'

CONTEST_SCORING_TYPES: Type[CONTEST_SCORING_TYPES_] = CONTEST_SCORING_TYPES_


class CONTEST_GROUP_SCORING_TYPES_(IntegerChoices):
	NONE = 1, _("Administrative group only")  # Makes the contest group purely administrative, with no aggregate scoreboard.
	UPM = 2, _("UPM")

CONTEST_GROUP_SCORING_TYPES: Type[CONTEST_GROUP_SCORING_TYPES_] = CONTEST_GROUP_SCORING_TYPES_


class CONTEST_ROUND_TYPES_(IntegerChoices):
	practice = 1, _("Practice")
	regular = 2, _("Regular")
	finale = 3, _("Finale")

CONTEST_ROUND_TYPES: Type[CONTEST_ROUND_TYPES_] = CONTEST_ROUND_TYPES_


class TASK_EVALUATION_TYPES_(IntegerChoices):
	server_evaluation = 1, _("Server evaluation")
	local_evaluation = 2, _("Local evaluation")
	manual_evaluation = 3, _("Manual evaluation")


TASK_EVALUATION_TYPES: Type[TASK_EVALUATION_TYPES_] = TASK_EVALUATION_TYPES_
TASK_EVALUATION_TYPE_DESCRIPTION: Dict[int, str] = {
	TASK_EVALUATION_TYPES.server_evaluation: _(
		"Submitted solutions are automatically evaluated on the judge server in a "
		"<a href='/info/#sys-info'>controlled environment</a>. "
		"Time and memory limits are specified in the task and enforced on the server. "
		"The solution must use one of the <a href='/info/#sys-info'>supported languages</a> and will receive "
		"one of the <a href='/info/#statuses'>available statuses</a> upon evaluation. "
		"More information is available in the <a href='/info/#sys-usage'>Judge system usage</a> section."
	),
	TASK_EVALUATION_TYPES.local_evaluation: _(
		"To solve the task, you must download a helper file to your computer, where you write your solution. "
		"You must use the same programming language as used in the helper file. Running the file on your computer "
		"will evaluate your solution on the test cases in the file and the results will be uploaded to the server. "
		"The judge server can additionally check the correctness of your results, but it will not run your file."
	),
	TASK_EVALUATION_TYPES.manual_evaluation: _(
		"The submitted solutions are evaluated manually and will not be run automatically. No immediate "
		"feedback is given."
	),
}
assert TASK_EVALUATION_TYPE_DESCRIPTION.keys() == set(TASK_EVALUATION_TYPES)


# Keys are ordered by difficulty.
class TASK_DIFFICULTY_(IntegerChoices):
	very_easy = 10, _('Very easy')
	easy = 20, _('Easy')
	easy_med = 30, _('Easy-Medium')
	med = 40, _('Medium')
	med_hard = 50, _('Medium-Hard')
	hard = 60, _('Hard')
	very_hard = 70, _('Very hard')

TASK_DIFFICULTY: Type[TASK_DIFFICULTY_] = TASK_DIFFICULTY_


class ALERT_TYPES_(IntegerChoices):
	thread_activity = 1, 'Activity in a forum thread'
	manual_grading = 2, 'An upload needs manual grading'
	pragma = 3, 'Uploaded source contains suspicious code'
	internal_error = 4, 'An upload caused an internal error'

ALERT_TYPES: Type[ALERT_TYPES_] = ALERT_TYPES_


ALERT_SUBCLASS_MAP = {
	ALERT_TYPES.thread_activity: 'ui.core.alerts.types._ThreadActivityAlert',
	ALERT_TYPES.manual_grading: 'ui.core.alerts.types._ManualGradingAlert',
	ALERT_TYPES.pragma: 'ui.core.alerts.types._SuspiciousUploadAlert',
	ALERT_TYPES.internal_error: 'ui.core.alerts.types._InternalErrorAlert',
}
assert set(ALERT_TYPES) == set(ALERT_SUBCLASS_MAP), "{} vs. {}".format(set(ALERT_TYPES), set(ALERT_SUBCLASS_MAP))

class SAMPLE_VALIDITY_(IntegerChoices):
	ok = 1, _('All official solutions agree with this sample case.')
	fail = 2, _('No official solution agrees with this sample case.')
	mixed = 3, _('Some official solutions agree and some disagree with this sample case.')
	undetermined = 4, _('Some official solutions were not evaluated on this sample case.')

SAMPLE_VALIDITY: Type[SAMPLE_VALIDITY_] = SAMPLE_VALIDITY_

# UPM-specific

class UPM_TEAM_LOCATIONS_(TextChoices):
	Ljubljana = 'LJ', 'Ljubljana'
	Maribor = 'MB', 'Maribor'
	Koper = 'KP', 'Koper'

UPM_TEAM_LOCATIONS: Type[UPM_TEAM_LOCATIONS_] = UPM_TEAM_LOCATIONS_
