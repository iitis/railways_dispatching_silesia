class Block:
    def __init__(self, name, speed, arr=None, derp=None, approx_enter=None, label=None, shuting=None, turnaround_time_minutes=0):
        self.name = name
        self.speed = speed
        self.arr = arr
        self.derp = derp
        self.approx_enter = approx_enter
        self.label = label
        self.shuting = shuting
        self.turnaround_time_minutes = turnaround_time_minutes

class TimeTableBlocks:
    def __init__(self):
        self.time_table_blocks = []
    
    def __getitem__(self,name):
        return next((block for block in self.time_table_blocks if block.name == name), None)
    
    def get_previous(self,block):
        return None

    def get_next(self,block):
        return None

    def passing_time(self,block): #TODO: it depends on next block.
        return None

class TimeTable:
    def __init__(self, train, blocks, info):
        """Constructor  for the TimeTable class

        :param train: Train id
        :type train: int
        :param blocks: train blocks
        :type end: list
        :param info: Extra info of the time_table
        :type weight: list
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
    def __init__(self):
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
        return next(self.time_tables[train], None)

    def __repr__(self):
        """Used for printing

        :return: String representation of the object
        :rtype: string
        """
        return self.time_tables.__repr__()
