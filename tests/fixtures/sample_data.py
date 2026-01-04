"""Sample test data for yt-dlp responses."""

# Sample video data from yt-dlp
SAMPLE_VIDEO_DATA = {
    "id": "dQw4w9WgXcQ",
    "title": "Rick Astley - Never Gonna Give You Up",
    "duration": 212,
    "view_count": 1400000000,
    "uploader": "Rick Astley",
    "channel": "Rick Astley",
    "upload_date": "20091025",
    "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
    "timestamp": 1256428800,
    "release_timestamp": None,
}

SAMPLE_VIDEO_DATA_WITH_THUMBNAILS = {
    "id": "abc123XYZ00",
    "title": "Test Video with Thumbnails",
    "duration": 300,
    "view_count": 5000,
    "uploader": "Test Channel",
    "channel": "Test Channel",
    "thumbnails": [
        {"url": "https://i.ytimg.com/vi/abc123XYZ00/default.jpg", "width": 120, "height": 90},
        {"url": "https://i.ytimg.com/vi/abc123XYZ00/mqdefault.jpg", "width": 320, "height": 180},
        {"url": "https://i.ytimg.com/vi/abc123XYZ00/maxresdefault.jpg", "width": 1280, "height": 720},
    ],
    "timestamp": 1700000000, # 2023-11-11 00:00:00
}

SAMPLE_VIDEO_DETAILS_DATA = {
    "id": "dQw4w9WgXcQ",
    "title": "Rick Astley - Never Gonna Give You Up",
    "duration": 212,
    "view_count": 1400000000,
    "uploader": "Rick Astley",
    "uploader_id": "UCuAXFkgsw1L7xaCfnd5JJOw",
    "channel": "Rick Astley",
    "channel_id": "UCuAXFkgsw1L7xaCfnd5JJOw",
    "upload_date": "20091025",
    "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
    "description": "The official video for Never Gonna Give You Up by Rick Astley",
    "tags": ["rick astley", "never gonna give you up", "80s music"],
    "categories": ["Music"],
    "like_count": 15000000,
    "comment_count": 2500000,
    "age_limit": 0,
    "formats": [{"format_id": "22"}, {"format_id": "18"}],
    "timestamp": 1256428800,
}

# Sample playlist data from yt-dlp
SAMPLE_PLAYLIST_DATA = {
    "id": "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
    "title": "Python Tutorial Playlist",
    "uploader": "Python Channel",
    "channel": "Python Channel",
    "uploader_id": "UCpython",
    "channel_id": "UCpython",
    "playlist_count": 50,
    "n_entries": 50,
    "thumbnail": "https://i.ytimg.com/vi/playlist/default.jpg",
    "description": "Complete Python tutorial series",
    "modified_date": "20240101",
}

SAMPLE_PLAYLIST_DATA_WITH_THUMBNAILS = {
    "id": "PLtest123456",
    "title": "Test Playlist with Thumbnails",
    "uploader": "Test Uploader",
    "playlist_count": 10,
    "thumbnails": [
        {"url": "https://i.ytimg.com/vi/playlist/small.jpg"},
        {"url": "https://i.ytimg.com/vi/playlist/large.jpg"},
    ],
}

SAMPLE_PLAYLIST_DETAILS_DATA = {
    "id": "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
    "title": "Python Tutorial Playlist",
    "uploader": "Python Channel",
    "channel": "Python Channel",
    "uploader_id": "UCpython",
    "channel_id": "UCpython",
    "playlist_count": 50,
    "thumbnail": "https://i.ytimg.com/vi/playlist/default.jpg",
    "description": "Complete Python tutorial series",
    "modified_date": "20240101",
    "availability": "public",
    "tags": ["python", "tutorial", "programming"],
    "view_count": 100000,
    "entries": [
        {"id": "video1", "title": "Intro"},
        {"id": "video2", "title": "Variables"},
    ],
}

# Sample search results
SAMPLE_SEARCH_RESULTS = {
    "entries": [
        {
            "id": "video1",
            "title": "First Video",
            "duration": 100,
            "view_count": 1000,
            "uploader": "Uploader 1",
            "timestamp": 1700000000,
        },
        {
            "id": "video2",
            "title": "Second Video",
            "duration": 200,
            "view_count": 2000,
            "uploader": "Uploader 2",
            "timestamp": 1700000001,
        },
    ]
}

# Edge cases
SAMPLE_VIDEO_MINIMAL = {
    "id": "minimal0001",
    "title": "Minimal Video",
}

SAMPLE_VIDEO_NONE_VALUES = {
    "id": "none_vals001",
    "title": "Video with None Values",
    "duration": None,
    "view_count": None,
    "uploader": None,
    "channel": None,
    "upload_date": None,
    "thumbnail": None,
    "timestamp": None,
}

