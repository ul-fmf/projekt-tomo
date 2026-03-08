# Putka Django Models Reference

Detailed description of every model in `putka-team/putka` and its fields.

---

## Enums / Choice Constants

Defined in `ui/config/settings/enums.py`:

| Enum | Type | Values |
|------|------|--------|
| **PROG_LANGS** | IntegerChoices | `auto=100`, `txt=0`, `c=1`, `cpp=2`, `pas=3`, `java=4`, `py_noauto=5`, `py3=8`, `perl=6`, `cs=7`, `prolog=9`, `rb=10`, `rust=11`, `kotlin=12`, `go=13` |
| **ATT_TYPE** | IntegerChoices | `generic_secret=-3`, `inout_secret=-2`, `image=2`, `inout_public=3`, `generic_public=4` |
| **UPLOAD_STATUS** | IntegerChoices | `waiting=1`, `testing=2`, `done=3`, `error=4`, `manual=5` |
| **JAILRUN_STATUS** | IntegerChoices | `OK=1`, `RTE=2`, `TLE=3`, `MLE=4`, `OUT=5`, `THR=6`, `SYS=7`, `EXT=8`, `WA=9`, `PE=10` |
| **TASK_EVALUATION_TYPES** | IntegerChoices | `server_evaluation=1`, `local_evaluation=2`, `manual_evaluation=3` |
| **TASK_DIFFICULTY** | IntegerChoices | `very_easy=10`, `easy=20`, `easy_med=30`, `med=40`, `med_hard=50`, `hard=60`, `very_hard=70` |
| **CONTEST_STATE** | IntegerChoices | `upcoming=1`, `ongoing=2`, `finished=3`, `published=4` |
| **CONTEST_SCORING_TYPES** | IntegerChoices | `CLASSIC=1`, `UPM=2`, `RTK=3`, `RTKLite=4` |
| **CONTEST_GROUP_SCORING_TYPES** | IntegerChoices | `NONE=1`, `UPM=2` |
| **CONTEST_ROUND_TYPES** | IntegerChoices | `practice=1`, `regular=2`, `finale=3` |
| **FORUM_NOTIFY** | IntegerChoices | `never=0`, `recent_active=1`, `recent_passive=2`, `always=100` |
| **THREAD_TYPES** | TextChoices | `general='g'`, `task='t'`, `contest='c'` |
| **ALERT_TYPES** | IntegerChoices | `thread_activity=1`, `manual_grading=2`, `pragma=3`, `internal_error=4` |
| **SAMPLE_VALIDITY** | IntegerChoices | `ok=1`, `fail=2`, `mixed=3`, `undetermined=4` |

---

## Core Models

### User (`core/users/models.py`)

Extends Django's `AbstractUser`. Only customization is re-declaring `groups` with `related_name='users'`.

### Profile (`core/users/models.py`)

One-to-one extension of User with personal/preference data.

| Field | Type | Notes |
|-------|------|-------|
| `user` | OneToOneField(User) | primary_key=True, CASCADE |
| `lang` | CharField(max_length=2) | UI language |
| `country` | CharField(max_length=2) | |
| `birthday` | DateField | null, blank |
| `school` | CharField(max_length=200) | null, blank |
| `graduation_year` | IntegerField | null, blank |
| `forum_notify` | IntegerField | choices=FORUM_NOTIFY, default=recent_passive |
| `onsite_ip` | CharField(max_length=39) | null, blank |
| `mentor` | CharField(max_length=200) | null, blank |

### Group (`core/groups/models.py`)

Simple named group (replaces Django's built-in Group).

| Field | Type | Notes |
|-------|------|-------|
| `name` | CharField(max_length=150) | unique |

---

## Tasks

### Tag (`core/tasks/models.py`)

Categorization labels for tasks.

| Field | Type | Notes |
|-------|------|-------|
| `name` | SlugField(max_length=50) | unique, not blank/null |
| `description` | TextField | not blank/null |

### Task (`core/tasks/models.py`)

A programming problem/exercise. Uses `ContentManagementMixin` for permission helpers.

| Field | Type | Notes |
|-------|------|-------|
| `url` | SlugField(max_length=50) | unique |
| `author` | CharField(max_length=50) | null, blank |
| `evaluation_type` | PositiveSmallIntegerField | choices=TASK_EVALUATION_TYPES |
| `difficulty` | PositiveSmallIntegerField | null, blank, default=None, choices=TASK_DIFFICULTY + None |
| `tags` | ManyToManyField(Tag) | blank |
| `authors_notes` | TextField | null, blank |
| `testscript` | TextField | not null |
| `parents` | ManyToManyField(Set) | through=TaskLink |
| `content_queryset` | GenericRelation(Content) | reverse relation to Content |

### Set (`core/tasks/models.py`)

A hierarchical container (tree structure) that holds tasks and other sets. Represents categories, courses, problem sets, etc.

| Field | Type | Notes |
|-------|------|-------|
| `parent` | ForeignKey(self) | null, PROTECT |
| `title` | CharField(max_length=50) | |
| `url` | SlugField(max_length=50) | unique within parent |
| `absolute_path` | TextField | editable=False, unique, must start/end with `/` |
| `description` | TextField | null, blank |
| `public` | BooleanField | default=False |
| `sort` | PositiveIntegerField | unique within parent |
| `user_perms` | GenericRelation(UserObjectPermission) | |
| `group_perms` | GenericRelation(GroupObjectPermission) | |

### TaskLink (`core/tasks/models.py`)

Through-model connecting a Task to a Set (soft link). A task can appear in multiple sets.

| Field | Type | Notes |
|-------|------|-------|
| `parent` | ForeignKey(Set) | CASCADE |
| `task` | ForeignKey(Task) | CASCADE |
| `sort` | PositiveIntegerField | not null; unique within parent |

Constraints: unique(parent, task), unique(parent, sort).

### File (`core/tasks/models.py`)

Binary file attached to a task (test data, templates, images, etc.). Default manager defers `data` for performance.

| Field | Type | Notes |
|-------|------|-------|
| `task` | ForeignKey(Task) | CASCADE |
| `filename` | CharField(max_length=50) | unique with task |
| `type` | IntegerField | choices=ATT_TYPE, not null |
| `data` | BinaryField | not null |
| `md5` | CharField(max_length=32) | auto-computed on save |
| `whitespace_errors` | JSONField | null, blank; auto-computed on save |

---

## Wiki / Content

### Content (`core/wiki/models.py`)

Internationalized title+body text attached to any model via GenericForeignKey (used for Task and News).

| Field | Type | Notes |
|-------|------|-------|
| `content_type` | ForeignKey(ContentType) | CASCADE |
| `object_id` | PositiveIntegerField | |
| `base_object` | GenericForeignKey | via content_type + object_id |
| `lang` | CharField(max_length=2) | language code |
| `title` | CharField(max_length=50) | default='untitled' |
| `content` | TextField | |
| `version` | PositiveIntegerField | default=1, auto-incremented on save |
| `last_editor` | ForeignKey(User) | null, SET_NULL; required as `editor` kwarg on save |
| `last_edit_time` | DateTimeField | auto_now |

---

## Results / Submissions

### UploadBase (`core/results/models.py`) — abstract

Common fields for all code submissions.

| Field | Type | Notes |
|-------|------|-------|
| `user` | ForeignKey(User) | CASCADE |
| `lang` | IntegerField | choices=PROG_LANGS |
| `filename` | TextField | |
| `source` | BinaryField | |
| `upload_time` | DateTimeField | default=now, db_index |
| `status` | IntegerField | choices=UPLOAD_STATUS, default=waiting |
| `mgr_status` | IntegerField | default=-1, null, blank |
| `preparation_status` | IntegerField | choices=JAILRUN_STATUS, null, blank |
| `preparation_output` | BinaryField | null, blank |
| `system_output` | BinaryField | null, blank |
| `tester_signature` | CharField(max_length=50) | null, blank |

### Upload (`core/results/models.py`)

Concrete submission of code for a task. Inherits all UploadBase fields.

| Field | Type | Notes |
|-------|------|-------|
| *all UploadBase fields* | | |
| `task` | ForeignKey(Task) | CASCADE |
| `points` | IntegerField | null, blank |
| `max_points` | IntegerField | null, blank |
| `agg_status` | IntegerField | choices=JAILRUN_STATUS, null, blank |
| `reviewer_comment` | TextField | null, blank |
| `reviewer` | ForeignKey(User) | null, blank, SET_NULL, related_name='reviewed' |
| `is_official_solution` | BooleanField | default=False |
| `alerts` | GenericRelation(Alert) | |

Ordering: `-upload_time`

### Stat (`core/results/models.py`) — abstract

Execution statistics for a single test run.

| Field | Type | Notes |
|-------|------|-------|
| `run_status` | IntegerField | choices=JAILRUN_STATUS, null, blank |
| `time` | FloatField | null, blank |
| `memory` | FloatField | null, blank |
| `tasks` | IntegerField | null, blank |
| `exit_code` | IntegerField | null, blank |

### TestCase (`core/results/models.py`)

Result of running one test case against an Upload. Inherits Stat fields.

| Field | Type | Notes |
|-------|------|-------|
| *all Stat fields* | | |
| `name` | CharField(max_length=100) | input filename or descriptive name |
| `upload` | ForeignKey(Upload) | CASCADE |
| `points` | IntegerField | |
| `max_points` | IntegerField | |
| `user_output` | BinaryField | null, blank |
| `user_output_line` | IntegerField | null, blank |
| `official_output` | BinaryField | null, blank |
| `official_output_line` | IntegerField | null, blank |
| `user_stderr` | BinaryField | null, blank |

Ordering: `id`

### UserTest (`core/results/models.py`)

User-initiated test run (not graded). Inherits both Stat and UploadBase.

| Field | Type | Notes |
|-------|------|-------|
| *all Stat + UploadBase fields* | | |
| `user_input` | BinaryField | |
| `user_output` | BinaryField | null, blank |
| `user_stderr` | BinaryField | null, blank |

Ordering: `-upload_time`

---

## Permissions

### UserObjectPermission (`core/pauth/models.py`)

Per-object permission for a user (via GenericForeignKey).

| Field | Type | Notes |
|-------|------|-------|
| `user` | ForeignKey(User) | CASCADE |
| `manage` | BooleanField | view vs manage permission |
| `ref_count` | PositiveSmallIntegerField | null = explicit, non-null = derived (inherited) |
| `content_type` | ForeignKey(ContentType) | CASCADE |
| `object_id` | PositiveIntegerField | |
| `related_object` | GenericForeignKey | |

### GroupObjectPermission (`core/pauth/models.py`)

Same as UserObjectPermission but for a Group. Identical field structure with `group` FK instead of `user`.

---

## Alerts

### Alert (`core/alerts/models.py`)

Notification shown to a user, linked to any object via GenericForeignKey.

| Field | Type | Notes |
|-------|------|-------|
| `created` | DateTimeField | auto_now_add |
| `user` | ForeignKey(User) | CASCADE |
| `type` | PositiveSmallIntegerField | choices=ALERT_TYPES |
| `content_type` | ForeignKey(ContentType) | CASCADE |
| `object_id` | PositiveIntegerField | |
| `related_object` | GenericForeignKey | |
| `perms_checked` | BooleanField | default=False |

Constraint: unique(user, type, content_type, object_id)

---

## Contests

### Contest (`core/contests/models.py`)

A timed competition with a set of tasks.

| Field | Type | Notes |
|-------|------|-------|
| `title` | CharField(max_length=50) | |
| `url` | SlugField(max_length=50) | unique |
| `set` | ForeignKey(Set) | PROTECT; the set containing contest tasks |
| `scheduled_start` | DateTimeField | |
| `duration_minutes` | PositiveIntegerField | null, blank |
| `autostart` | BooleanField | default=False |
| `live_results` | BooleanField | |
| `auditable_results` | BooleanField | default=False |
| `public_testdata` | BooleanField | default=False |
| `scoring_type` | IntegerField | choices=CONTEST_SCORING_TYPES |
| `freeze_minutes` | PositiveIntegerField | null, blank |
| `public` | BooleanField | default=False |
| `actual_start` | DateTimeField | null, blank |
| `actual_end` | DateTimeField | null, blank |
| `published` | BooleanField | default=False |
| `contestants` | ManyToManyField(User) | through=Contestant |
| `uploads` | ManyToManyField(Upload) | through=ContestUpload |
| `scoreboard` | OneToOneField(StaticScoreboard) | null, SET_NULL |
| `user_perms` | GenericRelation | |
| `group_perms` | GenericRelation | |

Ordering: `scheduled_start, title`

### Contestant (`core/contests/models.py`)

Through-model linking User to Contest.

| Field | Type | Notes |
|-------|------|-------|
| `contest` | ForeignKey(Contest) | CASCADE |
| `user` | ForeignKey(User) | CASCADE |
| `disqualified` | BooleanField | default=False |

### ContestUpload (`core/contests/models.py`)

Through-model linking Upload to Contest.

| Field | Type | Notes |
|-------|------|-------|
| `contest` | ForeignKey(Contest) | CASCADE |
| `upload` | ForeignKey(Upload) | CASCADE |
| `disqualified` | BooleanField | default=False |

### StaticScoreboard (`core/contests/models.py`)

Cached scoreboard data.

| Field | Type | Notes |
|-------|------|-------|
| `metadata` | TextField | |
| `data` | TextField | |
| `last_hint` | TextField | null |

### ContestGroup (`core/contests/models.py`)

Groups multiple contests into a series (e.g. UPM season).

| Field | Type | Notes |
|-------|------|-------|
| `title` | CharField(max_length=50) | |
| `url` | SlugField(max_length=50) | unique |
| `rounds` | ManyToManyField(Contest) | through=ContestGroupMembership |
| `scoring_type` | IntegerField | choices=CONTEST_GROUP_SCORING_TYPES |
| `scoreboard` | OneToOneField(StaticScoreboard) | null, SET_NULL |

### ContestGroupMembership (`core/contests/models.py`)

Through-model linking Contest to ContestGroup.

| Field | Type | Notes |
|-------|------|-------|
| `contest` | ForeignKey(Contest) | CASCADE |
| `group` | ForeignKey(ContestGroup) | CASCADE |
| `round_type` | IntegerField | choices=CONTEST_ROUND_TYPES |

---

## Forums

### Forum (`forums/models.py`)

A discussion board category.

| Field | Type | Notes |
|-------|------|-------|
| `title` | CharField(max_length=50) | |
| `description` | TextField | |
| `url` | SlugField(max_length=50) | unique |

### Thread (`forums/models.py`)

Base thread model. Subclassed for different thread types.

| Field | Type | Notes |
|-------|------|-------|
| `date_created` | DateTimeField | auto_now_add |
| `thread_type` | SlugField(max_length=1) | choices=THREAD_TYPES, not editable |
| `alerts` | GenericRelation(Alert) | |

### GeneralThread (extends Thread)

| Field | Type | Notes |
|-------|------|-------|
| `title` | CharField(max_length=50) | |
| `url` | SlugField | unique |
| `forum` | ForeignKey(Forum) | CASCADE |
| `closed` | BooleanField | default=False |

### TaskThread (extends Thread)

| Field | Type | Notes |
|-------|------|-------|
| `task` | OneToOneField(Task) | CASCADE |

### ContestThread (extends Thread)

| Field | Type | Notes |
|-------|------|-------|
| `contest` | OneToOneField(Contest) | CASCADE |

### Post (`forums/models.py`)

A single message in a thread.

| Field | Type | Notes |
|-------|------|-------|
| `thread` | ForeignKey(Thread) | CASCADE |
| `author` | ForeignKey(User) | CASCADE |
| `content` | TextField | |
| `date_posted` | DateTimeField | auto_now_add |
| `public` | BooleanField | |
| `version` | PositiveIntegerField | default=1 |
| `last_editor` | ForeignKey(User) | null, SET_NULL |
| `last_edit_time` | DateTimeField | auto_now |
| `user_perms` | GenericRelation | |
| `group_perms` | GenericRelation | |

Ordering: `date_posted`

---

## News

### News (`news/models.py`)

A news/announcement post. Uses `ContentManagementMixin` and GenericRelation to Content for i18n.

| Field | Type | Notes |
|-------|------|-------|
| `author` | ForeignKey(User) | PROTECT |
| `date` | DateTimeField | default=now |
| `published` | BooleanField | default=False |
| `content_queryset` | GenericRelation(Content) | |

Ordering: `-date`

---

## Teams (UPM competitions)

### TeamMember (`teams/models.py`)

An individual team member.

| Field | Type | Notes |
|-------|------|-------|
| `first_name` | CharField(max_length=100) | |
| `last_name` | CharField(max_length=100) | |
| `email` | EmailField | |
| `organization` | CharField(max_length=300) | |
| `vegi` | BooleanField | default=False |
| `shirt_size` | CharField(max_length=16) | null, blank |

### Team (`teams/models.py`)

A competition team of up to 3 members.

| Field | Type | Notes |
|-------|------|-------|
| `name` | CharField(max_length=100) | validated regex |
| `user` | OneToOneField(User) | CASCADE |
| `location` | CharField(max_length=2) | choices=UPM_TEAM_LOCATIONS |
| `year` | IntegerField | default=current year |
| `comment` | TextField(max_length=2048) | blank |
| `captain` | OneToOneField(TeamMember) | PROTECT |
| `member2` | OneToOneField(TeamMember) | null, blank, SET_NULL |
| `member3` | OneToOneField(TeamMember) | null, blank, SET_NULL |

---

## Tomo-specific models (`specific/tomo/models.py`)

### Enrollment

Links a user to a course (Set).

| Field | Type | Notes |
|-------|------|-------|
| `user` | ForeignKey(User) | CASCADE |
| `course` | ForeignKey(Set) | CASCADE |
| `enrolled_at` | DateTimeField | auto_now_add |

Constraint: unique(user, course)

### CourseGroup

A named group of students within a course.

| Field | Type | Notes |
|-------|------|-------|
| `course` | ForeignKey(Set) | CASCADE |
| `name` | CharField(max_length=100) | |
| `members` | ManyToManyField(User) | blank |

Constraint: unique(course, name)

### StudentObservation

Teacher-student observation link within a course.

| Field | Type | Notes |
|-------|------|-------|
| `teacher` | ForeignKey(User) | CASCADE |
| `student` | ForeignKey(User) | CASCADE |
| `course` | ForeignKey(Set) | CASCADE |

Constraint: unique(teacher, student, course)

---

## Other

- **UntabledItem** (`core/common/models.py`) — simple key-value store: `key` (CharField, PK) + `value` (TextField, null).
- **Balloon** (`balloons/models.py`) — tracks balloon delivery for contest first-solves: `upload` (OneToOneField(Upload), PK), `status` (IntegerField, choices=BALLOON_STATUS), `user` (FK), `contest` (FK), `task` (FK). Constraint: unique(user, contest, task).
- **Onsite** (`onsite/models.py`) — configuration for on-site contest environments: `active`, `unique_ips`, `start_time`, `disable_logins`, `groups` (M2M), `static_password`, `client_seed`.
- **PrintJob** (`printing/models.py`) — print queue for on-site contests: `user` (FK), `file` (FileField), `filename`, `notes`, `time`, `status` (choices=PRINTJOB_STATUS). Ordering: `-time`.
- **CercTeamMetadata** (`specific/cerc/models.py`) — CERC-specific team metadata: `team` (OneToOneField(Team)), `cerc_id`, `rank`, `rank_citation`, `medal_citation`, `room`.
