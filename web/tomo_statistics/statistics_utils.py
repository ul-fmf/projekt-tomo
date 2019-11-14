from courses.models import Course
from attempts.models import HistoricalAttempt
from users.models import User

import datetime

def problem_timeline(problem, submissions):
    """
    Function that will receive all submissions for particular problem and create
    a timeline of times and solve statuses at that time.

    Example:
        2019-10-10T15:00:00 : part_1 correct, part_2 empty, part_3 empty
        2019-10-10T15:03:22 : part_1 correct, part_2 incorrect, part_3 empty
        2019-10-10T15:03:48 : part_1 correct, part_2 correct, part_3 empty


    Parameters:
        problem : Problem instance
            instance of the Problem model, for which we are calculating the timeline
        submissions : list of HistoricalAttempt instances
            a list of user attempts on given problem
    
    Returns:
        dictionary of (submission_date : solve state of current problem )
    """

    sorted_attempts = []
    for attempt in submissions:
        sorted_attempts.append((attempt.submission_date, attempt))
    
    sorted_attempts.sort()

    timeline = []
    parts_list = list(problem.parts.all())
    state = [None]*len(parts_list)
    
    index = 0
    while index < len(sorted_attempts):

        print('Calculating', index, len(sorted_attempts))

        current_time = sorted_attempts[index][0]

        same_time_index = index
        while same_time_index < len(sorted_attempts) and (sorted_attempts[same_time_index][0] - current_time) < datetime.timedelta(seconds=5):
            historical_attempt = sorted_attempts[same_time_index][1]
            part = historical_attempt.part
            part_index = parts_list.index(part)
            state[part_index] = historical_attempt
            same_time_index += 1

        timeline.append((current_time.strftime('%H:%M:%S - %d.%m.%Y'), state[:]))
        index = same_time_index

    return timeline

def get_submission_history(problemset, user):
    """
    Function that will return a queryset of users submissions in a given course.

    Parameters:
        problemset : ProblemSet instance
            Problem set in which we are interested
        user : User instance
            user for which we want the submission history

    Returns:
        dictionary of { problem : {part : [history] }}
    """

    submission_history = {}
    for problem in problemset.problems.all():
        submission_history[problem] = []


    user_attempts = HistoricalAttempt.objects.filter(
        user=user, part__problem__problem_set=problemset
    ).prefetch_related('part', 'part__problem', 'part__problem__problem_set')

    for attempt in user_attempts:
        problem = attempt.part.problem
        submission_history[problem].append(attempt)
    
    for problem, submissions in submission_history.items():
        submission_history[problem] = problem_timeline(problem, submissions)

    return submission_history