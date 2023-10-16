import sublime_plugin, sublime_api
from sublime import View

_SLT_POPUP_TITLE = "Additional Information"
_SLT_POPUP_STYLE = '''
<style>
    body {
        font-family: system;
    }
    h1 {
        font-size: 1.1rem;
        font-weight: bold;
        margin: 0 0 0.25em 0;
    }
    p {
        font-size: 1.05rem;
        margin: 0;
    }
</style>
'''

_SLT_title_text = None
_SLT_fn_on_navigate = None
_SLT_fn_on_navigate_showable = None
_SLT_fn_on_popup_content = None

def _SLT_default_on_navigate(href) -> None:
    print("href = '%s'" % href)

def _SLT_default_on_navigate_showable(view, point) -> bool:
    word = view.substr(view.word(point))
    word = word.strip()
    return len(word) > 0

def _SLT_hooking_function_on_navigate(href) -> None:
    '''
    The hooking function of `View.on_navigate(...)`
    '''
    if _SLT_fn_on_navigate: _SLT_fn_on_navigate(href)

def _SLT_default_fn_popup_content(view, point) -> list:
    result = []
    word = view.substr(view.word(point))
    word = word.strip()
    text = "No additional information for '%s'" % word
    result.append(text)
    return result

def _SLT_make_popup_body(view: View, point) -> str:
    result  = _SLT_title_text
    if _SLT_fn_on_popup_content:
        result += "".join(["<p>" + e + "</p>" for e in _SLT_fn_on_popup_content(view, point)])
    return result

def _SLT_hooking_function_show_popup(self, content, flags=0, location=-1,
    max_width=320, max_height=240, on_navigate=None, on_hide=None):
    '''
    The hooking function of `View.show_popup(...)`
    '''
    if content.find(_SLT_title_text) == -1:
        TAG_STYLE_CLOSED = "</style>"
        insert_position = content.find(TAG_STYLE_CLOSED) + len(TAG_STYLE_CLOSED) + 1
        # append my content
        new_content  = ""
        new_content += content[:insert_position]
        new_content += _SLT_make_popup_body(self, location)
        new_content += "<br>"
        new_content += content[insert_position:]
        # remove ":" from buit-in heading
        new_content = new_content.replace("<h1>Definition:</h1>", "<h1>Definition</h1>")
        new_content = new_content.replace("<h1>References:</h1>", "<h1>References</h1>")
        # update content
        content = new_content
    on_navigate = _SLT_hooking_function_on_navigate # hook the class method 'View.on_navigate'
    sublime_api.view_show_popup(
        self.view_id, location, content, flags, max_width, max_height, on_navigate, on_hide)

# Listener - Mouse Hover

class EventListener(sublime_plugin.EventListener):
  def on_hover(self, view, point, hover_zone):
    if not view.is_popup_visible() and _SLT_fn_on_navigate_showable(view, point):
        my_content  = ""
        my_content += "<body id=show-definitions>"
        my_content += _SLT_POPUP_STYLE
        my_content += _SLT_make_popup_body(view, point)
        my_content += "</body>"
        width, height = view.viewport_extent()
        view.show_popup(
            my_content, location=point, max_width=width, max_height=height)

# Setup - The public function

def setup(heading_text = None, fn_popup_content = None, fn_on_navigate = None, fn_on_navigate_showable = None):
    '''
    Setup to extend the sublime text's default pop-up.
    :param heading_text: The heading text.
    :param fn_popup_content(view, point) -> list: The function that make the popup content.
    :param fn_on_navigate(href) -> None: The function that handle the hyper-link's click event on popup.
    '''
    global _SLT_title_text
    _SLT_title_text = "<h1>%s</h1>" % (heading_text if heading_text else _SLT_POPUP_TITLE)
    global _SLT_fn_on_navigate
    _SLT_fn_on_navigate = fn_on_navigate if fn_on_navigate else _SLT_default_on_navigate
    global _SLT_fn_on_navigate_showable
    _SLT_fn_on_navigate_showable = fn_on_navigate_showable if fn_on_navigate_showable else _SLT_default_on_navigate_showable
    global _SLT_fn_on_popup_content
    _SLT_fn_on_popup_content = fn_popup_content if fn_popup_content else _SLT_default_fn_popup_content
    View.show_popup = _SLT_hooking_function_show_popup # hook the class method 'View.show_popup'
