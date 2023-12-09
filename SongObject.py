# Song object class to store song information

class SongObject:
    def __init__(self, title: str, url: str, filename: str, duration: str, thumbnail: str, requester: str):
        self.title = title
        self.url = url
        self.filename = filename
        self.duration = duration  # format is HH:MM:SS
        self.thumbnail = thumbnail
        self.requester = requester

    @property
    def title(self):
        return self.title

    @title.setter
    def title(self, title: str):
        self.title = title

    @property
    def url(self):
        return self.url

    @url.setter
    def url(self, url: str):
        self.url = url

    @property
    def filename(self):
        return self.filename

    @filename.setter
    def filename(self, filename: str):
        self.filename = filename

    @property
    def duration(self):
        return self.duration

    @duration.setter
    def duration(self, duration: str):
        self.duration = duration

    def get_duration_as_seconds(self) -> int:
        duration = self.duration
        duration = duration.split(':')
        seconds = 0
        if len(duration) == 3:
            seconds += int(duration[0]) * 3600
            seconds += int(duration[1]) * 60
            seconds += int(duration[2])
        elif len(duration) == 2:
            seconds += int(duration[0]) * 60
            seconds += int(duration[1])
        elif len(duration) == 1:
            seconds += int(duration[0])
        return seconds

    @property
    def thumbnail(self):
        return self.thumbnail

    @thumbnail.setter
    def thumbnail(self, thumbnail: str):
        self.thumbnail = thumbnail

    @property
    def requester(self):
        return self.requester

    @requester.setter
    def requester(self, requester: str):
        self.requester = requester
