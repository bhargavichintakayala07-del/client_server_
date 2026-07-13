def predict(domain):

    allowed = [
        "github.com",
        "leetcode.com",
        "geeksforgeeks.org",
        "w3schools.com"
    ]

    blocked = [
        "instagram.com",
        "facebook.com",
        "youtube.com",
        "netflix.com"
    ]

    if domain in allowed:
        return "Allowed"

    elif domain in blocked:
        return "Blocked"

    else:
        return "Unknown"