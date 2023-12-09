# Song object class to store song information

class SongObject:
    def __init__(self, title, url, filename, duration, thumbnail, requester):
        self.title: str = title
        self.url: str = url
        self.filename: str = filename
        self.duration: str = duration  # format is HH:MM:SS
        self.thumbnail: str = thumbnail
        self.requester: str = requester

    def get_title(self) -> str:
        return self.title

    def get_url(self) -> str:
        return self.url

    def get_duration_as_string(self) -> str:
        return self.duration

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

    def get_thumbnail(self) -> str:
        return self.thumbnail

    def get_requester(self) -> str:
        return self.requester


