# Copyright (C) 2008-2009 Open Society Institute
#               Thomas Moroz: tmoroz@sorosny.org
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License Version 2 as published
# by the Free Software Foundation.  You may not use, modify or distribute
# this program under any other version of the GNU General Public License.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import calendar
import datetime
from karl.content.calendar.presenters.base import BasePresenter
from karl.content.calendar.presenters.base import BaseEvent           
from karl.content.calendar.presenters.day import DayViewPresenter
from karl.content.calendar.utils import BubblePainter
from karl.content.calendar.utils import MonthSkeleton
from karl.content.calendar.utils import next_month
from karl.content.calendar.utils import prior_month                   

class WeekViewPresenter(BasePresenter):
    name = 'week'
    
    def _initialize(self):
        self._init_title()
        self.feed_url = self.url_for('atom.xml')  

        self._init_week_around_focus_datetime()
        self._init_first_and_last_moment()
        self._init_next_and_prev_datetime()
        self._init_hour_labels()
        self._init_navigation()
        self._init_bubble_painter()
        
    def _init_title(self):
        day_num = calendar.weekday(self.focus_datetime.year,
                                   self.focus_datetime.month,
                                   self.focus_datetime.day)
        day_name = calendar.day_name[day_num]                                   

        self.title = "Week of %s %d/%d" % (day_name, 
                                           self.focus_datetime.month,
                                           self.focus_datetime.day)

    def _init_week_around_focus_datetime(self):
        skeleton = MonthSkeleton(self.focus_datetime.year,
                                 self.focus_datetime.month)

        # find the week containing the datetime in focus                                     
        found_day = False
        for week_of_datetimes in skeleton.weeks:
            for dt in week_of_datetimes:
                same_year  = (dt.year  == self.focus_datetime.year)
                same_month = (dt.month == self.focus_datetime.month)
                same_day   = (dt.day   == self.focus_datetime.day)

                if (same_year and same_month and same_day):
                    found_day = True
                    break           
            if found_day:
                break        
        
        # save week in focus on the instance
        self.week = []
        for dt in week_of_datetimes:
            format = '%s?year=%d&month=%d&day=%d'
            show_url = format % (self.url_for('day.html'),
                                 dt.year, dt.month, dt.day)
            
            self.week.append(
                DayOnWeekView(dt.year, dt.month, dt.day, show_url)
            )
    
    def _init_first_and_last_moment(self):
        first_day = self.week[0]
        self._first_moment = datetime.datetime(first_day.year,
                                               first_day.month,
                                               first_day.day,
                                               0, 0, 0)
        last_day = self.week[6]        
        self._last_moment = datetime.datetime(last_day.year,
                                              last_day.month,
                                              last_day.day,
                                              23, 59, 59)

    def _init_next_and_prev_datetime(self):                          
        seven_days = datetime.timedelta(days=7)
        self.next_datetime  = self.focus_datetime + seven_days
        self.prev_datetime = self.focus_datetime - seven_days

    def _init_hour_labels(self):
        self.hour_labels = []
        for hour in range(0, 24):
            if hour == 0:
                label = '12 AM'
            elif hour == 12:
                label = '12 PM'
            elif hour < 12:
                label = '%d AM' % hour
            else:
                label = '%d PM' % (hour - 12)
            self.hour_labels.append(label)

    def _init_bubble_painter(self):
        self._bubble_painter = BubblePainter(self)

    def paint_events(self, events):
        events_to_bubble, other_events = self._separate_events(events)
        
        self._paint_events_into_upper_tray(events_to_bubble)
        self._paint_events_into_time_slots(other_events)

    def _separate_events(self, events):
        events_to_bubble = [] 
        other_events     = []

        for event in events:  
            if self._bubble_painter.should_paint_event(event):
                events_to_bubble.append(event)
            else:
                other_events.append(event)

        return (events_to_bubble, other_events)

    def _paint_events_into_time_slots(self, events):
        for day in self.week:
            presenter = DayViewPresenter(focus_datetime= day.start_datetime,
                                         now_datetime  = self.now_datetime,
                                         url_for       = self.url_for)
            
            presenter.paint_events(
                self._filter_events_for_day(events, day)
            )  
            
            day.half_hour_slots = presenter.half_hour_slots
            day.add_event_url   = presenter.add_event_url

    def _paint_events_into_upper_tray(self, events):
        pass

    def _filter_events_for_day(self, events, day):
        filtered = []
        one_day = datetime.timedelta(days=1)
        for event in events: 
            dt = event.startDate
            while dt < event.endDate:
              same_year  = (dt.year  == day.year)
              same_month = (dt.month == day.month)
              same_day   = (dt.day   == day.day)

              if (same_year and same_month and same_day):
                filtered.append(event)

              dt += one_day
        
        return filtered  

    @property
    def today_class(self):
        today_class = ''
        for day_of_week in self.week:
            same_year  = (self.now_datetime.year  == day_of_week.year)
            same_month = (self.now_datetime.month == day_of_week.month)
            same_day   = (self.now_datetime.day   == day_of_week.day)
            
            if (same_year and same_month and same_day):
                today_class = 'cal_today_%s' % day_of_week.css_day_abbr
                break
        return today_class

    @property 
    def auto_scroll_class(self):
        at_or_after_first_moment = (self.now_datetime >= self.first_moment)
        at_or_before_last_moment = (self.now_datetime <= self.last_moment)
        
        if at_or_after_first_moment and at_or_before_last_moment:
            css_class = 'today'
        else:
            css_class = ''

        return css_class

    @property
    def first_moment(self):
        return self._first_moment

    @property
    def last_moment(self):
        return self._last_moment
    
    @property
    def template_filename(self):
        return 'templates/calendar_week.pt'


class DayOnWeekView(object):
    _css_day_abbr = ('mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun')
    
    def __init__(self, year, month, day, show_url=None, add_event_url=None):
        self.year     = year
        self.month    = month
        self.day      = day
        self.show_url = show_url
        self.add_event_url = add_event_url

        self.start_datetime = datetime.datetime(year, month, day, 0,   0,  0)
        self.end_datetime   = datetime.datetime(year, month, day, 23, 59, 59)

        self._init_heading_and_css_day_abbr()

        self.all_day_events  = []
        self.half_hour_slots = []
    
    def _init_heading_and_css_day_abbr(self):
        day_idx = calendar.weekday(self.start_datetime.year,
                                   self.start_datetime.month,
                                   self.start_datetime.day)
        day_abbr = calendar.day_abbr[day_idx]                               

        self.heading = '%s %d/%d' % (day_abbr, 
                                     self.start_datetime.month,
                                     self.start_datetime.day)

        self.css_day_abbr = self._css_day_abbr[day_idx]

