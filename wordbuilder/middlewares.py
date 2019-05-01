from re import match
from datetime import date

from .models import Statistics


class StatisticsUpdateMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_anonymous:
            url = request.path

            if match(r'/trainings/[a-z_]+/', url):
                statistic = Statistics.objects.get(user__username=request.user.username)
                original_date = statistic.last_training
                new_date = date.today()

                if original_date is not None:
                    delta = new_date - original_date

                    if delta.days == 1:
                        statistic.day_streak += 1
                    elif delta.days > 1:
                        statistic.day_streak = 1

                    if statistic.day_streak > statistic.record_day_streak:
                        statistic.record_day_streak = statistic.day_streak

                else:
                    statistic.day_streak = 1
                    statistic.record_day_streak = 1

                statistic.last_training = date.today()
                statistic.save()

        response = self.get_response(request)
        return response
