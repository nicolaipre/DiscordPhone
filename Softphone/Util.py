from datetime import datetime

class Frame:
    def __init__(self, data, source=None, target=None):
        self.data = data

    def __str__(self):
        return unicode(self).encode('ascii', 'replace')

    def __unicode__(self):
            return "#%-6d Time: %s From: %-10s To: %-10s Len: %d " % (self.id, self.get_time_str(), self.source, self.target, len(self.data))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        return self.data[key]

     def get_time_str(self):
        """ Return current time in dashed ISO-like format.
        """
        return '{dt}-{tz}'.format(dt=self.time.strftime('%Y-%m-%d-%H-%M-%S.%f'), tz=time.tzname[time.localtime().tm_isdst])