import re

find_tag_scheme = re.compile(r"(?!<a[^>]*?>)(?P<tagged>#\w+)(?![^<]*?</a>)")


def process_tags(extra_tag_list, content):

    # Make extra text list clickable
    extra_tag_list = list(set(["#" + tag for tag in extra_tag_list]))
    extra_tag_list_clickable = [f"<a href='' rel='tag'>{tag}</a>" for tag in extra_tag_list]

    # collect tags from the post body
    intext_tag_list = re.findall(find_tag_scheme, content)
    if intext_tag_list:
        content = re.sub(find_tag_scheme, r"<a href='' rel='tag'>\g<tagged></a>", content)

    # Set tags as activitypub collection
    apub_tag_list = set(intext_tag_list + extra_tag_list)
    object_tags = [{
                       "href": "",
                       "name": tag,
                       "type": "Hashtag"
                   } for tag in apub_tag_list]

    footer_tags = ""
    if extra_tag_list_clickable:
        footer_tags = f"<br> {' '.join(extra_tag_list_clickable)}"

    return content, footer_tags, object_tags
