from datetime import datetime, time, timedelta


class StructureExitCalculator(object):
    """Calculates the armor and shield exit timer for structures"""
    def __init__(self, dow, hour, is_powered, minimum_final_timer, now=None):
        self.dow = int(dow)
        self.hour = int(hour)
        self.is_powered = bool(int(is_powered))
        self.minimum_final_timer = timedelta(hours=int(float(minimum_final_timer)*24))

        if now is None:
            self.now = datetime.now()
        else:
            self.now = now


    def next_dow(self, date, day):
        return (date + timedelta(days=(day-date.isoweekday()+7)%7)).date()


    def get_armor_window(self):
        """Calculates the armor timer window, returns none if there won't be one"""
        if self.is_powered:
            now = self.now + timedelta(days=1)
            return now - timedelta(hours=2), now + timedelta(hours=2)
        return None

    
    def get_armor_window_start(self):
        return self.get_armor_window()[0]
    def get_armor_window_end(self):
        return self.get_armor_window()[1]


    def get_structure_window(self):
        # Calculate the time that the final timer start should be calculated from
        start = self.get_armor_window()
        if start is None:
            start = self.now
        else:
            # Take the end of the armor window as that's the worst case
            start = start[1]

        # Calculate the final timer
        final_target = datetime.combine(self.next_dow(start, self.dow), time(self.hour, 0))
        # Check its within the minimum timer range
        final_timer_duration = final_target - start
        if final_timer_duration < self.minimum_final_timer:
            final_target = final_target + timedelta(days=7)

        return final_target - timedelta(hours=2), final_target + timedelta(hours=2)

    def get_structure_window_start(self):
        return self.get_structure_window()[0]
    def get_structure_window_end(self):
        return self.get_structure_window()[1]


    def get_structure_window_guarantee(self):
        offset = self.minimum_final_timer
        if self.is_powered:
            offset = offset + timedelta(hours=26)

        final_target = self.get_structure_window()[0] + timedelta(hours=2)
        return final_target - offset