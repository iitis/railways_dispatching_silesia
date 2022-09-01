class TimeTable:
    def __init__(self, train, blocks, info):
        """Constructor  for the TimeTable class

        :param train: Train id
        :type start: int
        :param end: End time
        :type end: int
        :param weight: Weight of the time_table
        :type weight: float
        :param id: Id of the time_table
        :type id: int
        """
        self.train = train
        self.blocks = blocks
        self.info = info

    def __repr__(self):
        """Used for printing

        :return: String representation of the object
        :rtype: string
        """
        return f"TimeTable for train no: {self.train} \n"


class TimeTableCollector:
    def __init__(self) -> None:
        """Constructor for the TimeTableCollector class"""

        self.time_tables = {}

    def new_timetable(self, train, blocks, info)-> TimeTable:
        """Creates a new time_table

        :param start: Start time
        :type start: int
        :param end: End time
        :type end: int
        :param weight: Weight of the time_table
        :type weight: float
        :param track: track information for music files
        :type track: int
        :return: Created time_table
        :rtype: TimeTable
        """
        time_table = TimeTable(train, blocks, info)
        self += time_table
        return time_table

    def __add__(self, time_table: TimeTable) -> "TimeTableCollector":
        """Adds a time_table to the time_table list of the TimeTableCollector

        :param time_table: TimeTable to add
        :type time_table: TimeTable
        :return: TimeTableCollector object
        :rtype: TimeTableCollector
        """
        if self[time_table.train] == None:
            self.time_tables[time_table.train]=time_table
        else:
            print(f"TimeTable for train {time_table.train} already exists")
        return self

    def __getitem__(self, train) -> TimeTable:
        """Returns the time_table with the given train, None if it is not found

        :param id: train number of the time_table
        :type id: int
        :return: time_table with the given train number
        :rtype:TimeTable
        """
        return next((time_table for time_table in self.time_tables if time_table.train == train), None)

    def __repr__(self):
        """Used for printing

        :return: String representation of the object
        :rtype: string
        """
        return self.time_tables.__repr__()
